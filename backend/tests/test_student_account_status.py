import importlib.util
import os
import unittest
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, insert, select
from sqlalchemy.exc import IntegrityError

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from app.models.student import (
    LEGACY_UNVERIFIED_STATUS,
    STUDENT_ACCOUNT_STATUSES,
    Student,
)


MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "7d3e5f9a2b14_enforce_student_account_status.py"
)


def load_migration():
    spec = importlib.util.spec_from_file_location("student_status_migration", MIGRATION_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load student status migration.")
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return migration


class StudentAccountStatusTests(unittest.TestCase):
    def test_model_declares_the_named_status_constraint(self) -> None:
        constraints = {
            constraint.name: constraint
            for constraint in Student.__table__.constraints
        }
        self.assertIn("ck_students_account_status", constraints)
        self.assertEqual(
            constraints["ck_students_account_status"].sqltext.text,
            (
                "account_status IN "
                "('legacy_unverified', 'pending_verification', 'active', "
                "'suspended', 'deactivated')"
            ),
        )


class StudentAccountStatusMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        metadata = MetaData()
        self.students = Table(
            "students",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(100), nullable=False),
            Column(
                "account_status",
                String(32),
                nullable=False,
                server_default=LEGACY_UNVERIFIED_STATUS,
            ),
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
        return Table("students", MetaData(), autoload_with=self.engine)

    def test_all_supported_statuses_are_accepted(self) -> None:
        self.run_migration("upgrade")
        students = self.reflected_students()

        with self.engine.begin() as connection:
            connection.execute(
                students.insert(),
                [
                    {"id": index + 1, "name": status, "account_status": status}
                    for index, status in enumerate(STUDENT_ACCOUNT_STATUSES)
                ],
            )

        with self.engine.connect() as connection:
            statuses = connection.execute(
                select(students.c.account_status).order_by(students.c.id)
            ).scalars().all()
        self.assertEqual(statuses, list(STUDENT_ACCOUNT_STATUSES))

    def test_unsupported_status_is_rejected(self) -> None:
        self.run_migration("upgrade")
        students = self.reflected_students()

        with self.engine.begin() as connection:
            with self.assertRaises(IntegrityError):
                connection.execute(
                    students.insert().values(
                        id=1,
                        name="Invalid",
                        account_status="unknown",
                    )
                )

    def test_legacy_status_remains_valid(self) -> None:
        self.run_migration("upgrade")
        students = self.reflected_students()

        with self.engine.begin() as connection:
            connection.execute(
                students.insert().values(
                    id=1,
                    name="Legacy",
                    account_status=LEGACY_UNVERIFIED_STATUS,
                )
            )

        with self.engine.connect() as connection:
            self.assertEqual(
                connection.execute(select(students.c.account_status)).scalar_one(),
                LEGACY_UNVERIFIED_STATUS,
            )

    def test_downgrade_removes_the_constraint(self) -> None:
        self.run_migration("upgrade")
        self.run_migration("downgrade")
        students = self.reflected_students()

        with self.engine.begin() as connection:
            connection.execute(
                students.insert().values(
                    id=1,
                    name="Invalid after downgrade",
                    account_status="unknown",
                )
            )


if __name__ == "__main__":
    unittest.main()
