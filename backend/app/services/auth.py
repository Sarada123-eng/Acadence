from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.teacher import Teacher

password_hasher = PasswordHasher()

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