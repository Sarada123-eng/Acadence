import os
import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from app.models.classroom import Classroom
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.routers.classroom import (
    create_subject_classroom,
    create_teacher_subject,
    list_teacher_classrooms,
)
from app.schemas.classroom import ClassroomCreate, SubjectCreate
from app.services.auth import get_current_teacher
from app.services.classroom_service import create_classroom


class ClassroomAuthorizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.teacher = Teacher(
            id=7,
            username="teacher7",
            name="Teacher Seven",
            password_hash="not-used",
        )
        self.other_teacher = Teacher(
            id=8,
            username="teacher8",
            name="Teacher Eight",
            password_hash="not-used",
        )
        self.db = Mock()

    def test_subject_creation_without_token_returns_401(self) -> None:
        with self.assertRaisesRegex(Exception, "Could not validate teacher credentials"):
            get_current_teacher(None, self.db)

    def test_classroom_creation_without_token_returns_401(self) -> None:
        with self.assertRaisesRegex(Exception, "Could not validate teacher credentials"):
            get_current_teacher(None, self.db)

    def test_classroom_listing_without_token_returns_401(self) -> None:
        with self.assertRaisesRegex(Exception, "Could not validate teacher credentials"):
            get_current_teacher(None, self.db)

    def test_authenticated_teacher_creates_subject_without_path_identity(self) -> None:
        subject = Subject(
            id=12,
            name="Mathematics",
            subject_code="MATH101",
            section="",
            teacher_id=self.teacher.id,
        )
        with patch("app.routers.classroom.create_subject", return_value=subject) as create:
            result = create_teacher_subject(
                SubjectCreate(name="Mathematics", subject_code="MATH101"),
                self.teacher,
                self.db,
            )

        self.assertIs(result, subject)
        self.assertEqual(create.call_args.args[1], self.teacher.id)

    def test_authenticated_teacher_creates_own_classroom(self) -> None:
        classroom = Classroom(
            id=20,
            name="Section A",
            section=None,
            subject_id=12,
            join_code="join-code",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        with patch("app.routers.classroom.create_classroom", return_value=classroom) as create:
            result = create_subject_classroom(
                12,
                ClassroomCreate(name="Section A"),
                self.teacher,
                self.db,
            )

        self.assertIs(result, classroom)
        self.assertEqual(create.call_args.args[4], self.teacher.id)

    def test_teacher_cannot_create_classroom_for_another_teacher(self) -> None:
        subject = Subject(
            id=99,
            name="Other subject",
            subject_code="OTHER101",
            section="",
            teacher_id=self.other_teacher.id,
        )
        self.db.get.return_value = subject
        with self.assertRaises(PermissionError):
            create_classroom(self.db, 99, "Other section", None, self.teacher.id)

        with patch(
            "app.routers.classroom.create_classroom",
            side_effect=PermissionError("You do not own this subject."),
        ):
            with self.assertRaisesRegex(Exception, "You do not own this subject"):
                create_subject_classroom(
                    99,
                    ClassroomCreate(name="Other section"),
                    self.teacher,
                    self.db,
                )

    def test_teacher_lists_only_own_classrooms(self) -> None:
        classrooms = [
            Classroom(
                id=20,
                name="Section A",
                section=None,
                subject_id=12,
                join_code="join-code",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        ]
        with patch(
            "app.routers.classroom.get_teacher_classrooms",
            return_value=classrooms,
        ) as list_classrooms:
            result = list_teacher_classrooms(self.teacher, self.db)

        self.assertEqual(result, classrooms)
        list_classrooms.assert_called_once_with(self.db, self.teacher.id)

    def test_invalid_token_is_rejected(self) -> None:
        from fastapi.security import HTTPAuthorizationCredentials

        with self.assertRaisesRegex(Exception, "Could not validate teacher credentials"):
            get_current_teacher(
                HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials="invalid-token",
                ),
                self.db,
            )


if __name__ == "__main__":
    unittest.main()
