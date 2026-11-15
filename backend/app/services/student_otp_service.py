import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import inspect as sqlalchemy_inspect
from sqlalchemy.orm import Session

from app.database.connection import Settings, settings
from app.models.student import ACTIVE_STATUS, PENDING_VERIFICATION_STATUS, Student
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


class StudentOtpPersistenceError(RuntimeError):
    """Raised when OTP challenge state cannot be persisted safely."""


class StudentOtpTransactionError(RuntimeError):
    """Raised when OTP issuance is called with an active Session transaction."""


class StudentOtpVerificationError(ValueError):
    """Raised when an OTP cannot be used to verify a registration."""


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


def _is_expired(value: datetime, now: datetime) -> bool:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value <= now


def verify_student_email_otp(
    db: Session,
    registration_reference: UUID | str,
    otp: str,
    app_settings: Settings = settings,
) -> dict[str, str]:
    """Verify an OTP and activate its pending Student atomically."""
    if db.in_transaction():
        raise StudentOtpTransactionError(
            "OTP verification requires a clean database session."
        )
    if len(otp) != 6 or not all("0" <= digit <= "9" for digit in otp):
        raise StudentOtpVerificationError("The verification code is invalid.")

    _validate_otp_configuration(app_settings)
    failed_attempt = False

    try:
        with db.begin():
            student = db.scalar(
                select(Student)
                .where(
                    Student.registration_reference
                    == str(registration_reference)
                )
                .with_for_update()
                .execution_options(populate_existing=True)
            )
            if student is None:
                raise StudentOtpVerificationError(
                    "The verification code is invalid or has expired."
                )

            challenge = db.scalar(
                select(StudentEmailOtpChallenge)
                .where(StudentEmailOtpChallenge.student_id == student.id)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
            now = datetime.now(timezone.utc)
            if (
                student.account_status != PENDING_VERIFICATION_STATUS
                or student.email_verified_at is not None
                or student.pending_registration_expires_at is None
                or _is_expired(student.pending_registration_expires_at, now)
            ):
                raise StudentOtpVerificationError(
                    "The verification code is invalid or has expired."
                )
            if (
                challenge is None
                or challenge.last_sent_at is None
                or _is_expired(challenge.expires_at, now)
                or challenge.consumed_at is not None
                or challenge.invalidated_at is not None
                or challenge.attempt_count
                >= app_settings.STUDENT_EMAIL_OTP_MAX_ATTEMPTS
            ):
                raise StudentOtpVerificationError(
                    "The verification code is invalid or has expired."
                )

            if not verify_student_email_otp_digest(
                otp,
                challenge,
                student.id,
                app_settings.STUDENT_EMAIL_OTP_SECRET.strip(),
            ):
                challenge.attempt_count += 1
                if (
                    challenge.attempt_count
                    >= app_settings.STUDENT_EMAIL_OTP_MAX_ATTEMPTS
                ):
                    challenge.invalidated_at = now
                failed_attempt = True
            else:
                challenge.consumed_at = now
                student.email_verified_at = now
                student.account_status = ACTIVE_STATUS
    except StudentOtpVerificationError:
        raise
    except SQLAlchemyError as exc:
        raise StudentOtpPersistenceError(
            "The verification result could not be saved."
        ) from exc

    if failed_attempt:
        raise StudentOtpVerificationError(
            "The verification code is invalid or has expired."
        )

    return {
        "registration_reference": str(registration_reference),
        "account_status": ACTIVE_STATUS,
    }


async def issue_student_email_otp(
    db: Session,
    student: Student,
    app_settings: Settings = settings,
) -> dict[str, str]:
    """Issue an OTP using one transaction for the locked Student mutation.

    The caller must provide a clean Session. This service owns each database
    transaction it opens and never joins, commits, or rolls back a caller-
    owned transaction.

    The transaction is committed before the external email request, so the
    Student row lock is never held while waiting for the provider.
    """
    if db.in_transaction():
        raise StudentOtpTransactionError(
            "OTP issuance requires a clean database session."
        )

    student_identity = sqlalchemy_inspect(student).identity
    student_id = (
        student_identity[0]
        if student_identity is not None
        else student.id
    )
    if student_id is None:
        raise StudentOtpValidationError("Student does not exist.")

    _validate_otp_configuration(app_settings)

    challenge_id = str(uuid4())
    otp = generate_student_email_otp()
    now = datetime.now(timezone.utc)
    try:
        with db.begin():
            persisted_student = db.scalar(
                select(Student)
                .where(Student.id == student_id)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
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

            challenge = db.scalar(
                select(StudentEmailOtpChallenge).where(
                    StudentEmailOtpChallenge.student_id == student_id
                )
            )
            if challenge is None:
                challenge = StudentEmailOtpChallenge(
                    id=challenge_id,
                    student_id=student_id,
                )
                db.add(challenge)
            else:
                challenge.id = challenge_id

            challenge.otp_digest = create_student_email_otp_digest(
                otp,
                challenge_id,
                student_id,
                app_settings.STUDENT_EMAIL_OTP_SECRET.strip(),
            )
            challenge.expires_at = now + timedelta(
                minutes=app_settings.STUDENT_EMAIL_OTP_EXPIRE_MINUTES,
            )
            challenge.attempt_count = 0
            challenge.created_at = now
            challenge.last_sent_at = None
            challenge.consumed_at = None
            challenge.invalidated_at = None
    except (StudentOtpValidationError, StudentOtpConfigurationError):
        raise
    except IntegrityError as exc:
        raise StudentOtpPersistenceError(
            "The OTP challenge could not be saved."
        ) from exc
    except SQLAlchemyError as exc:
        raise StudentOtpPersistenceError(
            "The OTP challenge could not be saved."
        ) from exc

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
        try:
            if db.in_transaction():
                raise StudentOtpTransactionError(
                    "OTP delivery compensation requires a clean database session."
                )
            with db.begin():
                db.execute(
                    update(StudentEmailOtpChallenge)
                    .where(
                        StudentEmailOtpChallenge.id == challenge_id,
                        StudentEmailOtpChallenge.student_id == student_id,
                        StudentEmailOtpChallenge.consumed_at.is_(None),
                        StudentEmailOtpChallenge.invalidated_at.is_(None),
                    )
                    .values(invalidated_at=datetime.now(timezone.utc))
                )
        except SQLAlchemyError as compensation_error:
            raise EmailDeliveryError(
                "Email delivery failed and the OTP challenge could not be invalidated."
            ) from compensation_error
        raise

    try:
        if db.in_transaction():
            raise StudentOtpTransactionError(
                "OTP delivery status update requires a clean database session."
            )
        with db.begin():
            db.execute(
                update(StudentEmailOtpChallenge)
                .where(
                    StudentEmailOtpChallenge.id == challenge_id,
                    StudentEmailOtpChallenge.student_id == student_id,
                    StudentEmailOtpChallenge.consumed_at.is_(None),
                    StudentEmailOtpChallenge.invalidated_at.is_(None),
                )
                .values(last_sent_at=datetime.now(timezone.utc))
            )
    except SQLAlchemyError as exc:
        raise StudentOtpPersistenceError(
            "The OTP challenge delivery status could not be saved."
        ) from exc

    return {
        "challenge_id": challenge_id,
        "provider_message_id": provider_message_id,
    }
