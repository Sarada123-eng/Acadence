import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.connection import Settings, settings
from app.models.student import PENDING_VERIFICATION_STATUS, Student
from app.models.student_email_otp import StudentEmailOtpChallenge
from app.services.email_service import (
    EmailConfigurationError,
    EmailDeliveryError,
    send_email,
)


class StudentOtpConfigurationError(RuntimeError):
    """Raised when OTP issuance is not configured safely."""


class StudentOtpValidationError(ValueError):
    """Raised when a student cannot receive an OTP challenge."""


def generate_student_email_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def create_student_email_otp_digest(
    otp: str,
    challenge_id: str,
    student_id: int,
    secret: str,
) -> str:
    message = f"{challenge_id}:{student_id}:{otp}".encode("utf-8")
    return hmac.new(
        secret.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()


def verify_student_email_otp_digest(
    otp: str,
    challenge: StudentEmailOtpChallenge,
    student_id: int,
    secret: str,
) -> bool:
    expected_digest = create_student_email_otp_digest(
        otp,
        challenge.id,
        student_id,
        secret,
    )
    return hmac.compare_digest(challenge.otp_digest, expected_digest)


def _validate_otp_configuration(app_settings: Settings) -> None:
    secret = app_settings.STUDENT_EMAIL_OTP_SECRET.strip()
    if len(secret.encode("utf-8")) < 32:
        raise StudentOtpConfigurationError(
            "Student email OTP is not configured safely."
        )


def _email_bodies(otp: str, expires_in_minutes: int) -> tuple[str, str]:
    text_body = (
        "Your Acadence email verification code is "
        f"{otp}.\n\nThis code expires in {expires_in_minutes} minutes. "
        "If you did not request verification, please ignore this message."
    )
    html_body = (
        "<p>Your Acadence email verification code is "
        f"<strong>{otp}</strong>.</p>"
        f"<p>This code expires in {expires_in_minutes} minutes. "
        "If you did not request verification, please ignore this message.</p>"
    )
    return text_body, html_body


async def issue_student_email_otp(
    db: Session,
    student: Student,
    app_settings: Settings = settings,
) -> dict[str, str]:
    if student.id is None:
        raise StudentOtpValidationError("Student does not exist.")

    persisted_student = db.get(Student, student.id)
    if persisted_student is None:
        raise StudentOtpValidationError("Student does not exist.")
    if persisted_student.account_status != PENDING_VERIFICATION_STATUS:
        raise StudentOtpValidationError(
            "Only pending students can receive an email verification code."
        )

    recipient = (persisted_student.institutional_email or "").strip()
    if not recipient:
        raise StudentOtpValidationError(
            "A valid institutional email is required for verification."
        )

    _validate_otp_configuration(app_settings)

    challenge_id = str(uuid4())
    otp = generate_student_email_otp()
    now = datetime.now(timezone.utc)
    challenge = db.scalar(
        select(StudentEmailOtpChallenge).where(
            StudentEmailOtpChallenge.student_id == persisted_student.id
        )
    )
    if challenge is None:
        challenge = StudentEmailOtpChallenge(
            id=challenge_id,
            student_id=persisted_student.id,
        )
        db.add(challenge)
    else:
        challenge.id = challenge_id

    challenge.otp_digest = create_student_email_otp_digest(
        otp,
        challenge_id,
        persisted_student.id,
        app_settings.STUDENT_EMAIL_OTP_SECRET.strip(),
    )
    challenge.expires_at = now + timedelta(
        minutes=app_settings.STUDENT_EMAIL_OTP_EXPIRE_MINUTES,
    )
    challenge.attempt_count = 0
    challenge.created_at = now
    challenge.last_sent_at = now
    challenge.consumed_at = None
    challenge.invalidated_at = None

    db.commit()
    db.refresh(challenge)

    text_body, html_body = _email_bodies(
        otp,
        app_settings.STUDENT_EMAIL_OTP_EXPIRE_MINUTES,
    )
    try:
        provider_message_id = await send_email(
            recipient,
            "Verify your Acadence email",
            text_body,
            html_body,
            app_settings,
        )
    except (EmailConfigurationError, EmailDeliveryError):
        challenge.invalidated_at = datetime.now(timezone.utc)
        try:
            db.commit()
        except SQLAlchemyError as compensation_error:
            db.rollback()
            raise EmailDeliveryError(
                "Email delivery failed and the OTP challenge could not be invalidated."
            ) from compensation_error
        raise

    return {
        "challenge_id": challenge.id,
        "provider_message_id": provider_message_id,
    }
