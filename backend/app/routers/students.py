from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.student import (
    StudentCreate,
    StudentRegistrationCreate,
    StudentRegistrationResponse,
    StudentResponse,
)
from app.services.student_service import (
    StudentRegistrationConfigurationError,
    StudentRegistrationValidationError,
    register_pending_student,
)


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
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Name-only student registration is no longer available.",
    )


@router.post(
    "/registrations",
    response_model=StudentRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_pending_student_account(
    student: StudentRegistrationCreate,
    db: Session = Depends(get_db),
) -> StudentRegistrationResponse:
    try:
        created_student = register_pending_student(
            db,
            student.name,
            student.institutional_student_id,
            student.institutional_email,
        )
    except StudentRegistrationConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except StudentRegistrationValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return StudentRegistrationResponse(
        registration_reference=created_student.registration_reference,
        account_status=created_student.account_status,
        pending_registration_expires_at=created_student.pending_registration_expires_at,
    )
