import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from sqlalchemy import JSON, Column, Integer, MetaData, String, Table, create_engine, insert

from app.models.student import (
    ACTIVE_STATUS,
    DEACTIVATED_STATUS,
    PENDING_VERIFICATION_STATUS,
    SUSPENDED_STATUS,
)
from app.repositories.biometric_repository import (
    get_classroom_biometric_embeddings,
)


class BiometricRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        metadata = MetaData()
        self.students = Table(
            "students",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(100), nullable=False),
            Column("account_status", String(32), nullable=False),
            Column("face_embedding", JSON, nullable=True),
            Column("voice_embedding", JSON, nullable=True),
        )
        self.classroom_memberships = Table(
            "classroom_students",
            metadata,
            Column("classroom_id", Integer, primary_key=True),
            Column("student_id", Integer, primary_key=True),
        )
        metadata.create_all(self.engine)

    def tearDown(self) -> None:
        self.engine.dispose()

    def add_student(
        self,
        student_id: int,
        account_status: str,
        classroom_id: int,
        face_embedding: list[float] | None = None,
        voice_embedding: list[float] | None = None,
    ) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                insert(self.students).values(
                    id=student_id,
                    name=f"Student {student_id}",
                    account_status=account_status,
                    face_embedding=face_embedding,
                    voice_embedding=voice_embedding,
                )
            )
            connection.execute(
                insert(self.classroom_memberships).values(
                    classroom_id=classroom_id,
                    student_id=student_id,
                )
            )

    def test_returns_only_active_classroom_members(self) -> None:
        self.add_student(
            1,
            ACTIVE_STATUS,
            classroom_id=10,
            face_embedding=[0.1],
            voice_embedding=[0.2],
        )
        self.add_student(
            2,
            PENDING_VERIFICATION_STATUS,
            classroom_id=10,
            face_embedding=[0.3],
            voice_embedding=[0.4],
        )
        self.add_student(
            3,
            SUSPENDED_STATUS,
            classroom_id=10,
            face_embedding=[0.5],
            voice_embedding=[0.6],
        )
        self.add_student(
            4,
            DEACTIVATED_STATUS,
            classroom_id=10,
            face_embedding=[0.7],
            voice_embedding=[0.8],
        )
        self.add_student(
            5,
            ACTIVE_STATUS,
            classroom_id=11,
            face_embedding=[0.9],
            voice_embedding=[1.0],
        )
        self.add_student(
            6,
            ACTIVE_STATUS,
            classroom_id=10,
            voice_embedding=[1.1],
        )

        with self.engine.connect() as connection:
            candidates = get_classroom_biometric_embeddings(
                connection,
                classroom_id=10,
            )

        self.assertEqual(
            candidates,
            [
                (1, [0.1], [0.2]),
                (6, None, [1.1]),
            ],
        )

    def test_empty_or_ineligible_classrooms_return_empty(self) -> None:
        self.add_student(
            1,
            SUSPENDED_STATUS,
            classroom_id=10,
            face_embedding=[0.1],
            voice_embedding=[0.2],
        )

        with self.engine.connect() as connection:
            self.assertEqual(
                get_classroom_biometric_embeddings(connection, 10),
                [],
            )
            self.assertEqual(
                get_classroom_biometric_embeddings(connection, 99),
                [],
            )


if __name__ == "__main__":
    unittest.main()
