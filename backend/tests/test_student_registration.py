import os
import unittest
from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

import httpx2 as httpx

from alembic.migration import MigrationContext
from alembic.operations import Operations
from app.database.connection import Settings, get_db
from app.main import app
from app.models.student import PENDING_VERIFICATION_STATUS, Student
from app.routers import students as students_router
from app.services.student_service import (
    StudentRegistrationConfigurationError,
    register_pending_student,
)


MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "8e4f6a1b2c39_add_pending_student_registration_fields.py"
)


def load_pending_registration_migration():
    spec = importlib.util.spec_from_file_location(
        "pending_registration_migration",
        MIGRATION_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load pending registration migration.")
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return migration


class StudentRegistrationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db = Mock()
        self.db.scalars.return_value.all.return_value = []
        self.settings = Settings(
            DATABASE_URL="sqlite+pysqlite:///:memory:",
            JWT_SECRET_KEY="test-only-secret",
            STUDENT_ALLOWED_EMAIL_DOMAINS="example.edu",
            PENDING_REGISTRATION_EXPIRE_MINUTES=30,
        )

    def test_valid_registration_creates_pending_student(self) -> None:
        student = register_pending_student(
            self.db,
            " Student Name ",
            " 001A ",
            " Student@Example.edu ",
            self.settings,
        )

        self.assertEqual(student.name, "Student Name")
        self.assertEqual(student.institutional_student_id, "001A")
        self.assertEqual(student.normalized_student_id, "001A")
        self.assertEqual(student.institutional_email, "Student@Example.edu")
        self.assertEqual(student.normalized_email, "student@example.edu")
        self.assertEqual(student.account_status, PENDING_VERIFICATION_STATUS)
        self.assertIsNone(student.email_verified_at)
        self.assertIsNone(student.identity_verified_at)
        self.assertIsNotNone(student.registration_reference)
        self.assertIsNotNone(student.pending_registration_expires_at)
        self.assertEqual(self.db.add.call_count, 1)

    def test_missing_domain_configuration_fails_closed(self) -> None:
        settings = Settings(
            DATABASE_URL="sqlite+pysqlite:///:memory:",
            JWT_SECRET_KEY="test-only-secret",
            STUDENT_ALLOWED_EMAIL_DOMAINS="",
        )

        with self.assertRaises(StudentRegistrationConfigurationError):
            register_pending_student(
                self.db,
                "Student Name",
                "S001",
                "student@example.edu",
                settings,
            )

    def test_identical_unexpired_pending_registration_is_idempotent(self) -> None:
        existing = Student(
            name="Student Name",
            institutional_student_id="S001",
            normalized_student_id="S001",
            institutional_email="student@example.edu",
            normalized_email="student@example.edu",
            registration_reference="existing-reference",
            pending_registration_expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=10),
            account_status=PENDING_VERIFICATION_STATUS,
        )
        self.db.scalars.return_value.all.return_value = [existing]

        result = register_pending_student(
            self.db,
            "Student Name",
            "S001",
            "student@example.edu",
            self.settings,
        )

        self.assertIs(result, existing)
        self.db.add.assert_not_called()
        self.db.commit.assert_not_called()

    def test_expired_pending_registration_is_reused_without_memberships(self) -> None:
        existing = Student(
            name="Old Name",
            institutional_student_id="S001",
            normalized_student_id="S001",
            institutional_email="old@example.edu",
            normalized_email="old@example.edu",
            registration_reference="old-reference",
            pending_registration_expires_at=datetime.now(timezone.utc)
            - timedelta(minutes=1),
            account_status=PENDING_VERIFICATION_STATUS,
        )
        self.db.scalars.return_value.all.return_value = [existing]

        result = register_pending_student(
            self.db,
            "New Name",
            "S001",
            "new@example.edu",
            self.settings,
        )

        self.assertIs(result, existing)
        self.assertEqual(result.name, "New Name")
        self.assertEqual(result.normalized_email, "new@example.edu")
        self.assertNotEqual(result.registration_reference, "old-reference")
        self.db.commit.assert_called_once()


class StudentRegistrationApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.db = Mock()
        app.dependency_overrides[get_db] = lambda: self.db

    async def asyncTearDown(self) -> None:
        app.dependency_overrides.clear()

    async def request(self, method: str, path: str, **kwargs) -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.request(method, path, **kwargs)

    async def test_valid_registration_endpoint_returns_no_internal_student_id(self) -> None:
        pending_student = Student(
            id=42,
            registration_reference="12345678-1234-5678-1234-567812345678",
            account_status=PENDING_VERIFICATION_STATUS,
            pending_registration_expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=30),
        )
        with patch.object(
            students_router,
            "register_pending_student",
            return_value=pending_student,
        ):
            response = await self.request(
                "POST",
                "/students/registrations",
                json={
                    "name": "Student Name",
                    "institutional_student_id": "S001",
                    "institutional_email": "student@example.edu",
                },
            )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(
            body["registration_reference"],
            "12345678-1234-5678-1234-567812345678",
        )
        self.assertEqual(body["account_status"], PENDING_VERIFICATION_STATUS)
        self.assertNotIn("id", body)

    async def test_name_only_registration_is_rejected(self) -> None:
        response = await self.request(
            "POST",
            "/students",
            json={"name": "Student Name"},
        )

        self.assertEqual(response.status_code, 410)

    async def test_invalid_registration_request_is_rejected(self) -> None:
        response = await self.request(
            "POST",
            "/students/registrations",
            json={
                "name": "Student Name",
                "institutional_student_id": "S001",
                "institutional_email": "not-an-email",
            },
        )

        self.assertEqual(response.status_code, 422)

    async def test_missing_domain_configuration_returns_safe_error(self) -> None:
        with patch.object(
            students_router,
            "register_pending_student",
            side_effect=StudentRegistrationConfigurationError(
                "Student registration is not configured."
            ),
        ):
            response = await self.request(
                "POST",
                "/students/registrations",
                json={
                    "name": "Student Name",
                    "institutional_student_id": "S001",
                    "institutional_email": "student@example.edu",
                },
            )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Student registration is not configured.")


class PendingRegistrationMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine

        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        metadata = MetaData()
        self.students = Table(
            "students",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(100), nullable=False),
        )
        metadata.create_all(self.engine)
        self.migration = load_pending_registration_migration()

    def tearDown(self) -> None:
        self.engine.dispose()

    def run_migration(self, operation: str) -> None:
        with self.engine.begin() as connection:
            context = MigrationContext.configure(connection)
            with Operations.context(context):
                getattr(self.migration, operation)()

    def test_upgrade_and_downgrade_preserve_existing_student_data(self) -> None:
        from sqlalchemy import MetaData, Table, insert, select

        with self.engine.begin() as connection:
            connection.execute(
                insert(self.students).values(
                    id=1,
                    name="Legacy Student",
                )
            )

        self.run_migration("upgrade")
        upgraded = Table("students", MetaData(), autoload_with=self.engine)
        with self.engine.connect() as connection:
            row = connection.execute(select(upgraded)).mappings().one()
        self.assertEqual(row["name"], "Legacy Student")
        self.assertIsNone(row["registration_reference"])
        self.assertIsNone(row["pending_registration_expires_at"])

        self.run_migration("downgrade")
        downgraded = Table("students", MetaData(), autoload_with=self.engine)
        self.assertEqual(
            set(downgraded.columns.keys()),
            {
                "id",
                "name",
            },
        )


if __name__ == "__main__":
    unittest.main()
