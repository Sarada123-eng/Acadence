from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import Settings, get_db, settings
from app.models.teacher import Teacher

password_hasher = PasswordHasher()
bearer_scheme = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        password_hasher.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False

def get_teacher_by_username(db: Session, username: str) -> Teacher | None:
    teacher = db.execute(
        select(Teacher).where(Teacher.username == username)
    )
    return teacher.scalar_one_or_none() # scalar_one_or_none() returns the first result or None if no results were found. If more than one result is found, it raises an exception.

def create_teacher(db: Session, username: str, name: str, password: str) -> Teacher:
    password_hash = hash_password(password)
    new_teacher = Teacher(
        username=username,
        name=name,
        password_hash=password_hash
    )
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher) # refresh() reloads the instance from the database. This is useful if you want to get the auto-generated id of the new teacher.
    return new_teacher

def teacher_login(db: Session, username: str, password: str) -> Teacher | None:
    teacher = get_teacher_by_username(db, username)
    if teacher and verify_password(password, teacher.password_hash):
        return teacher
    return None


def create_access_token(
    teacher: Teacher,
    jwt_settings: Settings = settings,
) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    payload = {
        "sub": str(teacher.id),
        "role": "teacher",
        "exp": expires_at,
    }
    return jwt.encode(
        payload,
        jwt_settings.JWT_SECRET_KEY,
        algorithm=jwt_settings.JWT_ALGORITHM,
    )


def get_current_teacher(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Teacher:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate teacher credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("role") != "teacher":
            raise credentials_exception

        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.isdigit():
            raise credentials_exception

        teacher_id = int(subject)
    except (JWTError, ValueError):
        raise credentials_exception from None

    teacher = db.get(Teacher, teacher_id)
    if teacher is None:
        raise credentials_exception

    return teacher