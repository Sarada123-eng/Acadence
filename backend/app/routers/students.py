from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.student import StudentCreate, StudentResponse
from app.services.student_service import create_student


router = APIRouter(
    prefix="/students",
    tags=["Students"],
)


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
) -> StudentResponse:
    created_student = create_student(db, student.name)

    return StudentResponse(
        id=created_student.id,
        name=created_student.name,
        face_embedding_enrolled=created_student.face_embedding is not None,
        voice_embedding_enrolled=created_student.voice_embedding is not None,
    )
