from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session # Session is a class that represents a database session. It is used to interact with the database and perform CRUD operations.

from app.database.connection import get_db
from app.models.teacher import Teacher
from app.schemas.teacher import (
    TeacherLogin,
    TeacherRegister,
    TeacherResponse,
    TeacherTokenResponse,
)
from app.services.auth import (
    create_access_token,
    create_teacher,
    get_current_teacher,
    get_teacher_by_username,
    teacher_login,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post(
    "/teacher/register",
    response_model=TeacherResponse,
    status_code=status.HTTP_201_CREATED
    )
def register_teacher(teacher: TeacherRegister, db: Session = Depends(get_db)):# Depends(get_db) is required to get the database session from the dependency injection system of FastAPI. It will call the get_db function and provide the database session to the register_teacher function.
    existing_teacher = get_teacher_by_username(db, teacher.username)
    if existing_teacher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    new_teacher = create_teacher(db, teacher.username, teacher.name, teacher.password)
    return new_teacher

@router.post(
    "/teacher/login",
    response_model=TeacherTokenResponse,
)
def login_teacher(teacher: TeacherLogin, db: Session = Depends(get_db)):
    logged_in_teacher = teacher_login(db, teacher.username, teacher.password)
    if not logged_in_teacher:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    return TeacherTokenResponse(
        id=logged_in_teacher.id,
        username=logged_in_teacher.username,
        name=logged_in_teacher.name,
        access_token=create_access_token(logged_in_teacher),
        token_type="bearer",
    )


@router.get(
    "/teacher/me",
    response_model=TeacherResponse,
)
def get_teacher_profile(
    current_teacher: Teacher = Depends(get_current_teacher),
):
    return current_teacher
