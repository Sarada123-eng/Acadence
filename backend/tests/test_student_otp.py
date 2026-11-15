import importlib.util
import os
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret")

from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    Table,
    create_engine,
    insert,
    inspect,
)
from sqlalchemy.exc import IntegrityError

from app.database.connection import Settings
from app.models.student import PENDING_VERIFICATION_STATUS, Student
from app.models.student_email_otp import StudentEmailOtpChallenge
from app.services.email_service import EmailDeliveryError
from app.services.student_otp_service import (
    create_student_email_otp_digest,
    generate_student_email_otp,
    issue_student_email_otp,
    verify_student_email_otp_digest,
)


class FakeSession:
    def __init__(self, student: Student, challenge=None) -> None:
        self.student = student
        self.challenge = challenge
        self.commits = 0

    def get(self, model, student_id):
        return self.student if model is Student and student_id == self.student.id else None

    def scalar(self, statement):
        return self.challenge

    def add(self, challenge):
        self.challenge = challenge

    def commit(self):
        self.commits += 1

    def refresh(self, challenge):
        return None

    def rollback(self):
        return None


def load_migration():
    path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "a1b2c3d4e5f6_add_student_email_otp_challenges.py"
    )
    spec = importlib.util.spec_from_file_location("student_otp_migration", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load OTP migration.")
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return migration


class StudentOtpHelperTests(unittest.TestCase):
    def test_generated_otp_is_six_digits(self) -> None:
        for _ in range(100):
            self.assertRegex(generate_student_email_otp(), r"^\d{6}$")

    def test_digest_is_challenge_bound_and_constant_time_verified(self) -> None:
        secret = "s" * 32
        first = create_student_email_otp_digest("001234", "challenge-1", 7, secret)
        second = create_student_email_otp_digest("001234", "challenge-2", 7, secret)
        challenge = StudentEmailOtpChallenge(
            id="challenge-1",
            student_id=7,
            otp_digest=first,
            expires_at=datetime.now(timezone.utc),
            last_sent_at=datetime.now(timezone.utc),
        )

        self.assertNotEqual(first, second)
        self.assertTrue(
            verify_student_email_otp_digest("001234", challenge, 7, secret)
        )
        self.assertFalse(
            verify_student_email_otp_digest("001235", challenge, 7, secret)
        )

    def test_otp_settings_validate_positive_values(self) -> None:
        base = {
            "DATABASE_URL": "sqlite+pysqlite:///:memory:",
            "JWT_SECRET_KEY": "test-only-secret",
        }
        with self.assertRaises(ValueError):
            Settings(**base, STUDENT_EMAIL_OTP_EXPIRE_MINUTES=0)
        with self.assertRaises(ValueError):
            Settings(**base, STUDENT_EMAIL_OTP_MAX_ATTEMPTS=-1)


class StudentOtpIssuanceTests(unittest.IsolatedAsyncioTestCase):
    def settings(self) -> Settings:
        return Settings(
            DATABASE_URL="sqlite+pysqlite:///:memory:",
            JWT_SECRET_KEY="test-only-secret",
            STUDENT_EMAIL_OTP_SECRET="s" * 32,
            STUDENT_EMAIL_OTP_EXPIRE_MINUTES=5,
            RESEND_API_KEY="test",
            EMAIL_FROM_ADDRESS="no-reply@example.edu",
        )

    def student(self) -> Student:
        return Student(
            id=7,
            name="Student",
            institutional_email="student@example.edu",
            account_status=PENDING_VERIFICATION_STATUS,
        )

    @patch("app.services.student_otp_service.send_email", new_callable=AsyncMock)
    async def test_issue_returns_safe_result_and_sends_both_bodies(
        self,
        send_email: AsyncMock,
    ) -> None:
        send_email.return_value = "email-1"
        session = FakeSession(self.student())

        result = await issue_student_email_otp(session, session.student, self.settings())

        self.assertEqual(result["provider_message_id"], "email-1")
        self.assertNotIn("otp", result)
        self.assertEqual(session.commits, 1)
        arguments = send_email.await_args.args
        self.assertEqual(arguments[0], "student@example.edu")
        self.assertRegex(arguments[2], r"\d{6}")
        self.assertIn("<strong>", arguments[3])

    @patch("app.services.student_otp_service.send_email", new_callable=AsyncMock)
    async def test_delivery_failure_invalidates_challenge(
        self,
        send_email: AsyncMock,
    ) -> None:
        send_email.side_effect = EmailDeliveryError("Email provider failed to send the message.")
        session = FakeSession(self.student())

        with self.assertRaises(EmailDeliveryError):
            await issue_student_email_otp(session, session.student, self.settings())

        self.assertIsNotNone(session.challenge.invalidated_at)
        self.assertEqual(session.commits, 2)

    async def test_missing_secret_fails_before_persistence(self) -> None:
        session = FakeSession(self.student())
        weak_settings = self.settings()
        weak_settings.STUDENT_EMAIL_OTP_SECRET = "weak"

        with self.assertRaisesRegex(RuntimeError, "not configured safely"):
            await issue_student_email_otp(session, session.student, weak_settings)

        self.assertEqual(session.commits, 0)


class StudentOtpMigrationTests(unittest.TestCase):
    def test_unique_student_constraint_is_enforced_and_downgrade_is_scoped(self) -> None:
        engine = create_engine("sqlite+pysqlite:///:memory:")
        metadata = MetaData()
        students = Table(
            "students",
            metadata,
            Column("id", Integer, primary_key=True),
        )
        metadata.create_all(engine)
        migration = load_migration()
        with engine.begin() as connection:
            from alembic.migration import MigrationContext
            from alembic.operations import Operations

            context = MigrationContext.configure(connection)
            with Operations.context(context):
                migration.upgrade()
            connection.execute(insert(students).values(id=1))
            otp = Table("student_email_otp_challenges", MetaData(), autoload_with=engine)
            values = {
                "id": "challenge-1",
                "student_id": 1,
                "otp_digest": "d" * 64,
                "expires_at": datetime.now(timezone.utc),
                "attempt_count": 0,
                "created_at": datetime.now(timezone.utc),
                "last_sent_at": datetime.now(timezone.utc),
            }
            connection.execute(insert(otp).values(values))
            with self.assertRaises(IntegrityError):
                connection.execute(insert(otp).values({**values, "id": "challenge-2"}))
            with Operations.context(context):
                migration.downgrade()

        self.assertNotIn(
            "student_email_otp_challenges",
            inspect(engine).get_table_names(),
        )
        self.assertIn("students", inspect(engine).get_table_names())
        engine.dispose()


if __name__ == "__main__":
    unittest.main()
