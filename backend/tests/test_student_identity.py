import importlib.util
import os
import unittest
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import JSON, Column, Integer, MetaData, String, Table, create_engine, insert, select
from sqlalchemy.exc import IntegrityError

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from app.models.student import (
    Student,
    normalize_email,
    normalize_student_id,
)


MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "6c2d4e8f1a90_add_student_identity_fields.py"
)


def load_migration():
    spec = importlib.util.spec_from_file_location("student_identity_migration", MIGRATION_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load student identity migration.")
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return migration


class StudentIdentityModelTests(unittest.TestCase):
    def test_identity_fields_are_nullable_without_an_account_status_default(self) -> None:
        columns = Student.__table__.c

        for column_name in (
            "institutional_student_id",
            "normalized_student_id",
            "institutional_email",
            "normalized_email",
            "email_verified_at",
            "identity_verified_at",
        ):
            self.assertTrue(columns[column_name].nullable)

        self.assertFalse(columns.account_status.nullable)
        self.assertIsNone(columns.account_status.default)
        self.assertIsNone(columns.account_status.server_default)

    def test_normalization_preserves_identifiers_and_is_deterministic(self) -> None:
        self.assertEqual(normalize_student_id("  Ab-001  "), "Ab-001")
        self.assertEqual(normalize_email("  Student@Example.edu "), "student@example.edu")

    def test_existing_biometric_columns_and_relationships_remain(self) -> None:
        columns = Student.__table__.c
        self.assertIsNotNone(columns.face_embedding)
        self.assertIsNotNone(columns.voice_embedding)
        self.assertIn("subjects", Student.__mapper__.relationships)
        self.assertIn("classrooms", Student.__mapper__.relationships)


class StudentIdentityMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        metadata = MetaData()
        self.students = Table(
            "students",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(100), nullable=False),
            Column("face_embedding", JSON, nullable=True),
            Column("voice_embedding", JSON, nullable=True),
        )
        metadata.create_all(self.engine)
        self.migration = load_migration()

    def tearDown(self) -> None:
        self.engine.dispose()

    def run_migration(self, operation: str) -> None:
        with self.engine.begin() as connection:
            context = MigrationContext.configure(connection)
            with Operations.context(context):
                getattr(self.migration, operation)()

    def reflected_students(self) -> Table:
        metadata = MetaData()
        return Table("students", metadata, autoload_with=self.engine)

    def test_upgrade_preserves_existing_rows_and_assigns_legacy_status(self) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                insert(self.students).values(
                    id=1,
                    name="Legacy Student",
                    face_embedding=[0.1, 0.2],
                    voice_embedding=[0.3, 0.4],
                )
            )

        self.run_migration("upgrade")

        students = self.reflected_students()
        with self.engine.connect() as connection:
            row = connection.execute(select(students)).mappings().one()

        self.assertEqual(row["name"], "Legacy Student")
        self.assertEqual(row["face_embedding"], [0.1, 0.2])
        self.assertEqual(row["voice_embedding"], [0.3, 0.4])
        self.assertEqual(row["account_status"], "legacy_unverified")
        self.assertIsNone(row["institutional_student_id"])
        self.assertIsNone(row["normalized_email"])

    def test_duplicate_non_null_normalized_values_are_rejected(self) -> None:
        self.run_migration("upgrade")
        students = self.reflected_students()

        with self.engine.begin() as connection:
            connection.execute(
                students.insert().values(
                    id=1,
                    name="First",
                    normalized_student_id="s001",
                )
            )
            with self.assertRaises(IntegrityError):
                connection.execute(
                    students.insert().values(
                        id=2,
                        name="Second",
                        normalized_student_id="s001",
                    )
                )

    def test_duplicate_non_null_normalized_email_is_rejected(self) -> None:
        self.run_migration("upgrade")
        students = self.reflected_students()

        with self.engine.begin() as connection:
            connection.execute(
                students.insert().values(
                    id=1,
                    name="First",
                    normalized_email="first@example.edu",
                )
            )
            with self.assertRaises(IntegrityError):
                connection.execute(
                    students.insert().values(
                        id=2,
                        name="Second",
                        normalized_email="first@example.edu",
                    )
                )

    def test_multiple_null_identity_values_are_allowed(self) -> None:
        self.run_migration("upgrade")
        students = self.reflected_students()

        with self.engine.begin() as connection:
            connection.execute(
                students.insert(),
                [
                    {"id": 1, "name": "First"},
                    {"id": 2, "name": "Second"},
                ],
            )

        with self.engine.connect() as connection:
            count = connection.execute(select(students.c.id)).all()
        self.assertEqual(len(count), 2)

    def test_downgrade_removes_only_new_identity_columns(self) -> None:
        self.run_migration("upgrade")
        self.run_migration("downgrade")

        with self.engine.connect() as connection:
            columns = {column["name"] for column in connection.dialect.get_columns(connection, "students")}

        self.assertEqual(
            columns,
            {"id", "name", "face_embedding", "voice_embedding"},
        )


if __name__ == "__main__":
    unittest.main()
