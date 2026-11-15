from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.student import (
    StudentEmailOtpVerificationRequest,
    StudentEmailOtpVerificationResponse,
    StudentRegistrationCreate,
    StudentRegistrationResponse,
)
from app.services.student_service import (
    StudentRegistrationConfigurationError,
    StudentRegistrationValidationError,
    register_pending_student,
)
from app.services.email_service import EmailConfigurationError, EmailDeliveryError
from app.services.student_otp_service import (
    StudentOtpConfigurationError,
    StudentOtpPersistenceError,
    StudentOtpTransactionError,
    StudentOtpValidationError,
    StudentOtpVerificationError,
    issue_student_email_otp,
    verify_student_email_otp,
)


router = APIRouter(prefix="/students", tags=["Students"])


@router.post(
    "/registrations",
    response_model=StudentRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_pending_student_account(
    student: StudentRegistrationCreate,
    db: Session = Depends(get_db),
) -> StudentRegistrationResponse:
    """Create or reuse a pending registration and send a fresh verification OTP.

    Pending-registration retries intentionally have no cooldown yet; rate
    limiting is deferred to the resend/cooldown task.
    """
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

    try:
        db.commit()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration could not be completed.",
        ) from exc

    try:
        await issue_student_email_otp(db, created_student)
    except EmailConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email delivery is not configured.",
        ) from exc
    except EmailDeliveryError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Verification email could not be delivered.",
        ) from exc
    except StudentOtpConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email verification is not configured.",
        ) from exc
    except StudentOtpTransactionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except StudentOtpValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except StudentOtpPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification email could not be prepared.",
        ) from exc

    return StudentRegistrationResponse(
        registration_reference=created_student.registration_reference,
        account_status=created_student.account_status,
        pending_registration_expires_at=created_student.pending_registration_expires_at,
    )


@router.post(
    "/registrations/verify-email",
    response_model=StudentEmailOtpVerificationResponse,
)
def verify_student_registration_email(
    verification: StudentEmailOtpVerificationRequest,
    db: Session = Depends(get_db),
) -> StudentEmailOtpVerificationResponse:
    try:
        result = verify_student_email_otp(
            db,
            verification.registration_reference,
            verification.otp,
        )
    except StudentOtpVerificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except StudentOtpTransactionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except StudentOtpConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except StudentOtpPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification could not be completed.",
        ) from exc

    return StudentEmailOtpVerificationResponse(**result)
