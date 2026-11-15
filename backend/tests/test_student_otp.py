import importlib.util
import os
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Event, Thread
from unittest.mock import AsyncMock, patch

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret")

from sqlalchemy import (
    Column,
    DateTime,
    JSON,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    insert,
    inspect,
    select,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.database.connection import Settings
from app.models.student import ACTIVE_STATUS, PENDING_VERIFICATION_STATUS, Student
from app.models.student_email_otp import StudentEmailOtpChallenge
from app.services.email_service import EmailDeliveryError
from app.services.student_otp_service import (
    StudentOtpTransactionError,
    StudentOtpValidationError,
    StudentOtpVerificationError,
    create_student_email_otp_digest,
    generate_student_email_otp,
    issue_student_email_otp,
    verify_student_email_otp,
    verify_student_email_otp_digest,
)


class FakeSession:
    def __init__(self, student: Student, challenge=None) -> None:
        self.student = student
        self.challenge = challenge
        self.commits = 0
        self.scalar_calls = 0

    class _Transaction:
        def __init__(self, session) -> None:
            self.session = session

        def __enter__(self):
            return self.session

        def __exit__(self, exc_type, exc_value, traceback):
            if exc_type is None:
                self.session.commits += 1
            return False

    def scalar(self, statement):
        self.scalar_calls += 1
        return self.student if self.scalar_calls == 1 else self.challenge

    def add(self, challenge):
        self.challenge = challenge

    def begin(self):
        return self._Transaction(self)

    def in_transaction(self):
        return False

    def execute(self, statement):
        if self.challenge is not None:
            if "invalidated_at" in str(statement):
                self.challenge.invalidated_at = datetime.now(timezone.utc)
            else:
                self.challenge.last_sent_at = datetime.now(timezone.utc)

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


def load_nullable_migration():
    path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "b2c3d4e5f6a7_allow_unsent_otp_challenges.py"
    )
    spec = importlib.util.spec_from_file_location("student_otp_nullable_migration", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load nullable OTP migration.")
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
        self.assertEqual(session.commits, 2)
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


class StudentOtpDatabaseTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        metadata = MetaData()
        Table(
            "students",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(100), nullable=False),
            Column("institutional_student_id", String(100)),
            Column("normalized_student_id", String(100)),
            Column("institutional_email", String(320)),
            Column("normalized_email", String(320)),
            Column("registration_reference", String(36)),
            Column("pending_registration_expires_at", DateTime(timezone=True)),
            Column("account_status", String(32), nullable=False),
            Column("email_verified_at", DateTime(timezone=True)),
            Column("identity_verified_at", DateTime(timezone=True)),
            Column("face_embedding", JSON),
            Column("voice_embedding", JSON),
        )
        metadata.create_all(self.engine)
        StudentEmailOtpChallenge.__table__.create(self.engine)
        self.session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )
        with self.session_factory() as session:
            session.add(
                Student(
                    id=11,
                    name="Persisted Student",
                    institutional_email="persisted@example.edu",
                    registration_reference="11111111-1111-1111-1111-111111111111",
                    pending_registration_expires_at=datetime.now(timezone.utc)
                    + timedelta(minutes=30),
                    account_status=PENDING_VERIFICATION_STATUS,
                )
            )
            session.commit()

    def tearDown(self) -> None:
        self.engine.dispose()

    def add_challenge(
        self,
        session,
        otp: str = "123456",
        *,
        expires_at: datetime | None = None,
        sent: bool = True,
    ) -> StudentEmailOtpChallenge:
        now = datetime.now(timezone.utc)
        challenge = StudentEmailOtpChallenge(
            id="challenge-for-verification",
            student_id=11,
            otp_digest=create_student_email_otp_digest(
                otp,
                "challenge-for-verification",
                11,
                "s" * 32,
            ),
            expires_at=expires_at or now + timedelta(minutes=5),
            last_sent_at=now if sent else None,
        )
        session.add(challenge)
        session.commit()
        return challenge

    @patch("app.services.student_otp_service.send_email", new_callable=AsyncMock)
    async def test_real_session_creates_and_rotates_one_challenge(
        self,
        send_email: AsyncMock,
    ) -> None:
        app_settings = Settings(
            DATABASE_URL="sqlite+pysqlite:///:memory:",
            JWT_SECRET_KEY="test-only-secret",
            STUDENT_EMAIL_OTP_SECRET="s" * 32,
            STUDENT_EMAIL_OTP_EXPIRE_MINUTES=5,
        )

        with self.session_factory() as session:
            async def provider(*args, **kwargs):
                self.assertFalse(session.in_transaction())
                return "email-1"

            send_email.side_effect = provider
            student = session.get(Student, 11)
            session.rollback()
            first = await issue_student_email_otp(session, student, app_settings)
            first_challenge = session.scalar(
                select(StudentEmailOtpChallenge).where(
                    StudentEmailOtpChallenge.student_id == 11
                )
            )
            first_id = first_challenge.id
            first_challenge.attempt_count = 2
            first_challenge.consumed_at = datetime.now(timezone.utc)
            session.commit()

            second = await issue_student_email_otp(session, student, app_settings)
            second_challenge = session.scalar(
                select(StudentEmailOtpChallenge).where(
                    StudentEmailOtpChallenge.student_id == 11
                )
            )

            self.assertEqual(first["provider_message_id"], "email-1")
            self.assertNotEqual(first_id, second["challenge_id"])
            self.assertEqual(second_challenge.id, second["challenge_id"])
            self.assertEqual(second_challenge.attempt_count, 0)
            self.assertIsNone(second_challenge.consumed_at)
            self.assertIsNone(second_challenge.invalidated_at)
            self.assertIsNotNone(second_challenge.last_sent_at)
            self.assertEqual(
                session.query(StudentEmailOtpChallenge).count(),
                1,
            )
            self.assertNotIn(
                send_email.await_args_list[0].args[2].split("code is ")[1].split(".")[0],
                second_challenge.otp_digest,
            )

    @patch("app.services.student_otp_service.send_email", new_callable=AsyncMock)
    async def test_active_caller_transaction_is_not_modified(
        self,
        send_email: AsyncMock,
    ) -> None:
        with self.session_factory() as session:
            student = session.get(Student, 11)
            student.name = "Caller-owned change"

            with self.assertRaises(StudentOtpTransactionError):
                await issue_student_email_otp(
                    session,
                    student,
                    Settings(
                        DATABASE_URL="sqlite+pysqlite:///:memory:",
                        JWT_SECRET_KEY="test-only-secret",
                        STUDENT_EMAIL_OTP_SECRET="s" * 32,
                    ),
                )

            self.assertTrue(session.in_transaction())
            self.assertEqual(student.name, "Caller-owned change")
            self.assertEqual(
                session.query(StudentEmailOtpChallenge).count(),
                0,
            )
            send_email.assert_not_awaited()

    @patch("app.services.student_otp_service.send_email", new_callable=AsyncMock)
    async def test_locked_query_refreshes_stale_student_state(
        self,
        send_email: AsyncMock,
    ) -> None:
        app_settings = Settings(
            DATABASE_URL="sqlite+pysqlite:///:memory:",
            JWT_SECRET_KEY="test-only-secret",
            STUDENT_EMAIL_OTP_SECRET="s" * 32,
        )
        with self.session_factory() as session_a, self.session_factory() as session_b:
            stale_student = session_a.get(Student, 11)
            session_a.commit()
            updated_student = session_b.get(Student, 11)
            updated_student.account_status = "active"
            session_b.commit()

            self.assertEqual(stale_student.account_status, PENDING_VERIFICATION_STATUS)
            with self.assertRaises(StudentOtpValidationError):
                await issue_student_email_otp(
                    session_a,
                    stale_student,
                    app_settings,
                )

            self.assertEqual(stale_student.account_status, "active")
            send_email.assert_not_awaited()

    def settings(self, **overrides) -> Settings:
        values = {
            "DATABASE_URL": "sqlite+pysqlite:///:memory:",
            "JWT_SECRET_KEY": "test-only-secret",
            "STUDENT_EMAIL_OTP_SECRET": "s" * 32,
        }
        values.update(overrides)
        return Settings(**values)

    def test_correct_otp_activates_student_and_consumes_challenge(self) -> None:
        with self.session_factory() as session:
            self.add_challenge(session)

            result = verify_student_email_otp(
                session,
                "11111111-1111-1111-1111-111111111111",
                "123456",
                self.settings(),
            )

            student = session.get(Student, 11)
            challenge = session.get(
                StudentEmailOtpChallenge,
                "challenge-for-verification",
            )
            self.assertEqual(result["account_status"], ACTIVE_STATUS)
            self.assertEqual(student.account_status, ACTIVE_STATUS)
            self.assertIsNotNone(student.email_verified_at)
            self.assertIsNone(student.identity_verified_at)
            self.assertIsNotNone(challenge.consumed_at)

            session.commit()
            with self.assertRaises(StudentOtpVerificationError):
                verify_student_email_otp(
                    session,
                    "11111111-1111-1111-1111-111111111111",
                    "123456",
                    self.settings(),
                )

    def test_expiry_is_checked_after_student_and_challenge_locks(self) -> None:
        before_lock = datetime.now(timezone.utc)
        after_lock = before_lock + timedelta(seconds=2)
        student = Student(
            id=11,
            name="Locked Student",
            registration_reference="11111111-1111-1111-1111-111111111111",
            pending_registration_expires_at=before_lock + timedelta(seconds=1),
            account_status=PENDING_VERIFICATION_STATUS,
        )
        challenge = StudentEmailOtpChallenge(
            id="challenge-for-verification",
            student_id=11,
            otp_digest=create_student_email_otp_digest(
                "123456",
                "challenge-for-verification",
                11,
                "s" * 32,
            ),
            expires_at=before_lock + timedelta(seconds=1),
            last_sent_at=before_lock,
        )
        session = FakeSession(student, challenge)
        student_lock_started = Event()
        release_student_lock = Event()
        challenge_locked = Event()
        outcomes = []
        original_scalar = session.scalar

        def scalar(statement):
            if session.scalar_calls == 0:
                student_lock_started.set()
                if not release_student_lock.wait(timeout=2):
                    raise RuntimeError("Timed out waiting to release student lock.")
            result = original_scalar(statement)
            if session.scalar_calls == 2:
                challenge_locked.set()
            return result

        session.scalar = scalar

        def verify() -> None:
            try:
                verify_student_email_otp(
                    session,
                    student.registration_reference,
                    "123456",
                    self.settings(),
                )
            except Exception as exc:
                outcomes.append(exc)

        with patch("app.services.student_otp_service.datetime") as service_datetime:
            def capture_now(tz):
                if not challenge_locked.is_set():
                    raise AssertionError("Timestamp captured before challenge lock.")
                return after_lock

            service_datetime.now.side_effect = capture_now
            thread = Thread(target=verify)
            thread.start()
            self.assertTrue(student_lock_started.wait(timeout=2))
            release_student_lock.set()
            thread.join(timeout=2)

        self.assertFalse(thread.is_alive())
        self.assertEqual(len(outcomes), 1)
        self.assertIsInstance(outcomes[0], StudentOtpVerificationError)
        self.assertEqual(session.commits, 0)

    def test_invalid_otp_persists_attempts_and_invalidates_at_limit(self) -> None:
        with self.session_factory() as session:
            self.add_challenge(session)
            app_settings = self.settings(STUDENT_EMAIL_OTP_MAX_ATTEMPTS=2)

            with self.assertRaises(StudentOtpVerificationError):
                verify_student_email_otp(
                    session,
                    "11111111-1111-1111-1111-111111111111",
                    "000000",
                    app_settings,
                )
            challenge = session.get(
                StudentEmailOtpChallenge,
                "challenge-for-verification",
            )
            self.assertEqual(challenge.attempt_count, 1)
            session.commit()

            with self.assertRaises(StudentOtpVerificationError):
                verify_student_email_otp(
                    session,
                    "11111111-1111-1111-1111-111111111111",
                    "000000",
                    app_settings,
                )
            student = session.get(Student, 11)
            challenge = session.get(
                StudentEmailOtpChallenge,
                "challenge-for-verification",
            )
            self.assertEqual(challenge.attempt_count, 2)
            self.assertIsNotNone(challenge.invalidated_at)
            self.assertEqual(student.account_status, PENDING_VERIFICATION_STATUS)
            self.assertIsNone(student.email_verified_at)

    def test_unusable_challenge_and_expired_registration_are_rejected(self) -> None:
        with self.session_factory() as session:
            self.add_challenge(session, sent=False)
            with self.assertRaises(StudentOtpVerificationError):
                verify_student_email_otp(
                    session,
                    "11111111-1111-1111-1111-111111111111",
                    "123456",
                    self.settings(),
                )
            session.rollback()

            student = session.get(Student, 11)
            challenge = session.get(
                StudentEmailOtpChallenge,
                "challenge-for-verification",
            )
            student.pending_registration_expires_at = (
                datetime.now(timezone.utc) - timedelta(minutes=1)
            )
            challenge.expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            challenge.last_sent_at = datetime.now(timezone.utc)
            session.commit()
            with self.assertRaises(StudentOtpVerificationError):
                verify_student_email_otp(
                    session,
                    "11111111-1111-1111-1111-111111111111",
                    "123456",
                    self.settings(),
                )
            session.rollback()

            student = session.get(Student, 11)
            challenge = session.get(
                StudentEmailOtpChallenge,
                "challenge-for-verification",
            )
            student.pending_registration_expires_at = (
                datetime.now(timezone.utc) + timedelta(minutes=5)
            )
            challenge.last_sent_at = datetime.now(timezone.utc)
            challenge.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
            session.commit()
            with self.assertRaises(StudentOtpVerificationError):
                verify_student_email_otp(
                    session,
                    "11111111-1111-1111-1111-111111111111",
                    "123456",
                    self.settings(),
                )

    def test_missing_consumed_invalidated_and_exhausted_challenges_are_rejected(
        self,
    ) -> None:
        with self.session_factory() as session:
            with self.assertRaises(StudentOtpVerificationError):
                verify_student_email_otp(
                    session,
                    "11111111-1111-1111-1111-111111111111",
                    "123456",
                    self.settings(),
                )

            self.add_challenge(session)
            challenge = session.get(
                StudentEmailOtpChallenge,
                "challenge-for-verification",
            )
            challenge.consumed_at = datetime.now(timezone.utc)
            session.commit()
            with self.assertRaises(StudentOtpVerificationError):
                verify_student_email_otp(
                    session,
                    "11111111-1111-1111-1111-111111111111",
                    "123456",
                    self.settings(),
                )

            challenge.consumed_at = None
            challenge.invalidated_at = datetime.now(timezone.utc)
            session.commit()
            with self.assertRaises(StudentOtpVerificationError):
                verify_student_email_otp(
                    session,
                    "11111111-1111-1111-1111-111111111111",
                    "123456",
                    self.settings(),
                )

            challenge.invalidated_at = None
            challenge.attempt_count = self.settings().STUDENT_EMAIL_OTP_MAX_ATTEMPTS
            session.commit()
            with self.assertRaises(StudentOtpVerificationError):
                verify_student_email_otp(
                    session,
                    "11111111-1111-1111-1111-111111111111",
                    "123456",
                    self.settings(),
                )

    def test_active_caller_transaction_is_rejected_without_rollback(self) -> None:
        with self.session_factory() as session:
            student = session.get(Student, 11)
            student.name = "Caller-owned verification change"

            with self.assertRaises(StudentOtpTransactionError):
                verify_student_email_otp(
                    session,
                    "11111111-1111-1111-1111-111111111111",
                    "123456",
                    self.settings(),
                )

            self.assertTrue(session.in_transaction())
            self.assertEqual(student.name, "Caller-owned verification change")


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
        nullable_migration = load_nullable_migration()
        from alembic.migration import MigrationContext
        from alembic.operations import Operations

        def run_migration(target, operation: str) -> None:
            with engine.begin() as connection:
                context = MigrationContext.configure(connection)
                with Operations.context(context):
                    getattr(target, operation)()

        run_migration(migration, "upgrade")
        run_migration(nullable_migration, "upgrade")
        with engine.begin() as connection:
            connection.execute(insert(students).values(id=1))
            otp = Table("student_email_otp_challenges", MetaData(), autoload_with=engine)
            self.assertTrue(otp.c.last_sent_at.nullable)
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
        run_migration(nullable_migration, "downgrade")
        run_migration(migration, "downgrade")

        self.assertNotIn(
            "student_email_otp_challenges",
            inspect(engine).get_table_names(),
        )
        self.assertIn("students", inspect(engine).get_table_names())
        engine.dispose()


if __name__ == "__main__":
    unittest.main()
