import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt

from app.database.connection import settings
from app.models.teacher import Teacher
from app.services.auth import create_access_token, get_current_teacher


class TeacherJwtTests(unittest.TestCase):
    def setUp(self) -> None:
        self.teacher = Teacher(
            id=7,
            username="teacher7",
            name="Teacher Seven",
            password_hash="not-used",
        )
        self.db = Mock()
        self.db.get.return_value = self.teacher

    def credentials_for(self, token: str) -> HTTPAuthorizationCredentials:
        return HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token,
        )

    def test_create_access_token_contains_teacher_claims(self) -> None:
        token = create_access_token(self.teacher)
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        self.assertEqual(payload["sub"], "7")
        self.assertEqual(payload["role"], "teacher")
        self.assertIn("exp", payload)

    def test_valid_token_returns_teacher_from_database(self) -> None:
        token = create_access_token(self.teacher)

        result = get_current_teacher(
            self.credentials_for(token),
            self.db,
        )

        self.assertIs(result, self.teacher)
        self.db.get.assert_called_once_with(Teacher, 7)

    def test_missing_token_returns_401(self) -> None:
        with self.assertRaises(HTTPException) as context:
            get_current_teacher(None, self.db)

        self.assertEqual(context.exception.status_code, 401)

    def test_expired_token_returns_401(self) -> None:
        token = jwt.encode(
            {
                "sub": "7",
                "role": "teacher",
                "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        with self.assertRaises(HTTPException) as context:
            get_current_teacher(self.credentials_for(token), self.db)

        self.assertEqual(context.exception.status_code, 401)

    def test_invalid_token_returns_401(self) -> None:
        with self.assertRaises(HTTPException) as context:
            get_current_teacher(
                self.credentials_for("not-a-jwt"),
                self.db,
            )

        self.assertEqual(context.exception.status_code, 401)

    def test_wrong_role_returns_401(self) -> None:
        token = jwt.encode(
            {
                "sub": "7",
                "role": "student",
                "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        with self.assertRaises(HTTPException) as context:
            get_current_teacher(self.credentials_for(token), self.db)

        self.assertEqual(context.exception.status_code, 401)

    def test_deleted_teacher_returns_401(self) -> None:
        self.db.get.return_value = None
        token = create_access_token(self.teacher)

        with self.assertRaises(HTTPException) as context:
            get_current_teacher(self.credentials_for(token), self.db)

        self.assertEqual(context.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
