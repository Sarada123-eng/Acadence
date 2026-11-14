import importlib.util
import os
import unittest
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import (
    JSON,
    Column,
    CheckConstraint,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    insert,
    select,
)
from sqlalchemy.exc import IntegrityError

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from app.models.student import (
    STUDENT_ACCOUNT_STATUSES,
    Student,
)


MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "7d3e5f9a2b14_enforce_student_account_status.py"
)
RETIRE_MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "9f5a7c3d1e20_retire_legacy_student_status.py"
)


def load_migration():
    spec = importlib.util.spec_from_file_location("student_status_migration", MIGRATION_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load student status migration.")
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return migration


def load_retire_migration():
    spec = importlib.util.spec_from_file_location(
        "retire_student_status_migration",
        RETIRE_MIGRATION_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load legacy status retirement migration.")
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
                "('pending_verification', 'active', "
                "'suspended', 'deactivated')"
            ),
        )

    def test_legacy_status_is_not_supported(self) -> None:
        self.assertNotIn("legacy_unverified", STUDENT_ACCOUNT_STATUSES)


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
                server_default="legacy_unverified",
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


class LegacyStudentStatusRetirementMigrationTests(unittest.TestCase):
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
                server_default="legacy_unverified",
            ),
            Column("face_embedding", JSON, nullable=True),
            Column("voice_embedding", JSON, nullable=True),
            CheckConstraint(
                "account_status IN "
                "('legacy_unverified', 'pending_verification', 'active', "
                "'suspended', 'deactivated')",
                name="ck_students_account_status",
            ),
        )
        self.classroom_students = Table(
            "classroom_students",
            metadata,
            Column("classroom_id", Integer, primary_key=True),
            Column("student_id", Integer, primary_key=True),
        )
        self.student_subjects = Table(
            "student_subjects",
            metadata,
            Column("student_id", Integer, primary_key=True),
            Column("subject_id", Integer, primary_key=True),
        )
        self.attendance_logs = Table(
            "attendance_logs",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("student_id", Integer, nullable=False),
        )
        metadata.create_all(self.engine)
        self.migration = load_retire_migration()

    def tearDown(self) -> None:
        self.engine.dispose()

    def run_migration(self, operation: str) -> None:
        with self.engine.begin() as connection:
            context = MigrationContext.configure(connection)
            with Operations.context(context):
                getattr(self.migration, operation)()

    def test_upgrade_deactivates_legacy_students_and_preserves_data(self) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                insert(self.students).values(
                    id=7,
                    name="Legacy Student",
                    face_embedding=[0.1, 0.2],
                    voice_embedding=[0.3, 0.4],
                )
            )
            connection.execute(
                insert(self.classroom_students).values(classroom_id=1, student_id=7)
            )
            connection.execute(
                insert(self.student_subjects).values(subject_id=2, student_id=7)
            )
            connection.execute(
                insert(self.attendance_logs).values(id=3, student_id=7)
            )

        self.run_migration("upgrade")
        students = Table("students", MetaData(), autoload_with=self.engine)
        with self.engine.connect() as connection:
            row = connection.execute(select(students)).mappings().one()
            self.assertEqual(row["account_status"], "deactivated")
            self.assertEqual(row["face_embedding"], [0.1, 0.2])
            self.assertEqual(row["voice_embedding"], [0.3, 0.4])
            self.assertIsNone(students.c.account_status.server_default)
            self.assertEqual(
                connection.execute(select(self.classroom_students)).all(),
                [(1, 7)],
            )
            self.assertEqual(
                connection.execute(select(self.student_subjects)).all(),
                [(7, 2)],
            )
            self.assertEqual(
                connection.execute(select(self.attendance_logs)).all(),
                [(3, 7)],
            )

        with self.engine.connect() as connection:
            with self.assertRaises(IntegrityError):
                with connection.begin():
                    connection.execute(
                        students.insert().values(
                            id=8,
                            name="Invalid",
                            account_status="legacy_unverified",
                        )
                    )

    def test_downgrade_restores_legacy_status_constraint_and_default(self) -> None:
        self.run_migration("upgrade")
        self.run_migration("downgrade")
        students = Table("students", MetaData(), autoload_with=self.engine)

        self.assertEqual(
            str(students.c.account_status.server_default.arg).strip("'"),
            "legacy_unverified",
        )
        with self.engine.begin() as connection:
            connection.execute(
                students.insert().values(
                    id=1,
                    name="Legacy",
                    account_status="legacy_unverified",
                )
            )


if __name__ == "__main__":
    unittest.main()
