from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.connection import Settings, settings
from app.models.student import ACTIVE_STATUS, PENDING_VERIFICATION_STATUS, Student
from app.models.student import normalize_email, normalize_student_id


class StudentNotEligibleError(ValueError):
    """Raised when a pending student uses an existing student operation."""


class StudentRegistrationConfigurationError(RuntimeError):
    """Raised when registration cannot run with safe server configuration."""


class StudentRegistrationValidationError(ValueError):
    """Raised when registration input cannot be accepted."""


GENERIC_REGISTRATION_CONFLICT = (
    "Registration could not be completed. Use the existing account or contact support."
)


def ensure_student_can_use_existing_features(student: Student) -> None:
    if student.account_status != ACTIVE_STATUS:
        raise StudentNotEligibleError(
            "Student account is not active."
        )


def allowed_student_email_domains(
    app_settings: Settings = settings,
) -> set[str]:
    domains = {
        domain.strip().casefold().lstrip("@")
        for domain in app_settings.STUDENT_ALLOWED_EMAIL_DOMAINS.split(",")
        if domain.strip()
    }
    if not domains:
        raise StudentRegistrationConfigurationError(
            "Student registration is not configured."
        )
    return domains


def _has_established_student_data(student: Student) -> bool:
    return bool(
        student.face_embedding
        or student.voice_embedding
        or student.classrooms
        or student.subjects
    )


def _pending_registration_is_expired(
    student: Student,
    now: datetime,
) -> bool:
    return (
        student.account_status == PENDING_VERIFICATION_STATUS
        and (
            student.pending_registration_expires_at is None
            or student.pending_registration_expires_at <= now
        )
    )


def _prepare_expired_pending_registration(
    student: Student,
    now: datetime,
) -> None:
    if not _pending_registration_is_expired(student, now):
        return
    if _has_established_student_data(student):
        raise ValueError(GENERIC_REGISTRATION_CONFLICT)

    student.name = student.name.strip()
    student.institutional_student_id = None
    student.normalized_student_id = None
    student.institutional_email = None
    student.normalized_email = None
    student.registration_reference = None
    student.pending_registration_expires_at = None


def register_pending_student(
    db: Session,
    name: str,
    institutional_student_id: str,
    institutional_email: str,
    app_settings: Settings = settings,
) -> Student:
    normalized_student_id = normalize_student_id(institutional_student_id)
    normalized_email = normalize_email(institutional_email)
    if not normalized_student_id or not normalized_email:
        raise StudentRegistrationValidationError(
            "Registration identity values cannot be empty."
        )

    email_domain = normalized_email.rsplit("@", 1)[-1]
    if email_domain not in allowed_student_email_domains(app_settings):
        raise StudentRegistrationValidationError(
            "The institutional email domain is not allowed."
        )

    now = datetime.now(timezone.utc)
    matches = list(
        db.scalars(
            select(Student).where(
                or_(
                    Student.normalized_student_id == normalized_student_id,
                    Student.normalized_email == normalized_email,
                )
            )
        ).all()
    )

    reusable_student: Student | None = None
    if matches:
        if len(matches) != 1:
            raise ValueError(GENERIC_REGISTRATION_CONFLICT)

        existing = matches[0]
        same_identity = (
            existing.normalized_student_id == normalized_student_id
            and existing.normalized_email == normalized_email
        )
        if (
            same_identity
            and existing.account_status == PENDING_VERIFICATION_STATUS
            and not _pending_registration_is_expired(existing, now)
        ):
            return existing

        if (
            existing.account_status == PENDING_VERIFICATION_STATUS
            and _pending_registration_is_expired(existing, now)
        ):
            _prepare_expired_pending_registration(existing, now)
            reusable_student = existing
        else:
            raise ValueError(GENERIC_REGISTRATION_CONFLICT)

    expires_at = now + timedelta(
        minutes=app_settings.PENDING_REGISTRATION_EXPIRE_MINUTES,
    )
    student = reusable_student or Student(
        account_status=PENDING_VERIFICATION_STATUS,
    )
    student.name = name.strip()
    student.institutional_student_id = institutional_student_id.strip()
    student.normalized_student_id = normalized_student_id
    student.institutional_email = institutional_email.strip()
    student.normalized_email = normalized_email
    student.registration_reference = str(uuid4())
    student.pending_registration_expires_at = expires_at
    student.account_status = PENDING_VERIFICATION_STATUS
    student.email_verified_at = None
    student.identity_verified_at = None
    student.face_embedding = None
    student.voice_embedding = None
    if reusable_student is None:
        db.add(student)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(GENERIC_REGISTRATION_CONFLICT) from None
    db.refresh(student)
    return student
