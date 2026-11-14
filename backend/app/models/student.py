from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.database.connection import Base
from app.models.associations import classroom_students, student_subjects


LEGACY_UNVERIFIED_STATUS = "legacy_unverified"
PENDING_VERIFICATION_STATUS = "pending_verification"
ACTIVE_STATUS = "active"
SUSPENDED_STATUS = "suspended"
DEACTIVATED_STATUS = "deactivated"

STUDENT_ACCOUNT_STATUSES = (
    LEGACY_UNVERIFIED_STATUS,
    PENDING_VERIFICATION_STATUS,
    ACTIVE_STATUS,
    SUSPENDED_STATUS,
    DEACTIVATED_STATUS,
)


def normalize_student_id(value: str) -> str:
    """Normalize an institutional ID without assuming case-insensitive semantics."""
    return value.strip()


def normalize_email(value: str) -> str:
    """Normalize an email for case-insensitive lookup."""
    return value.strip().casefold()


if TYPE_CHECKING:
    from app.models.classroom import Classroom
    from app.models.subject import Subject


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        Index(
            "uq_students_normalized_student_id",
            "normalized_student_id",
            unique=True,
        ),
        Index(
            "uq_students_normalized_email",
            "normalized_email",
            unique=True,
        ),
        Index("ix_students_account_status", "account_status"),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
        )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
        )

    institutional_student_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    normalized_student_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    institutional_email: Mapped[str | None] = mapped_column(
        String(320),
        nullable=True,
    )

    normalized_email: Mapped[str | None] = mapped_column(
        String(320),
        nullable=True,
    )

    account_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=LEGACY_UNVERIFIED_STATUS,
        server_default=LEGACY_UNVERIFIED_STATUS,
        index=False,
    )

    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    identity_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    #  face embedding will be of the type JSONB, which is a binary representation of JSON data. This allows us to store the face embedding as a JSON object in the database, which can be easily serialized and deserialized.
    face_embedding: Mapped[list[float] | None] = mapped_column(
        JSONB,
        nullable=True
        )

    voice_embedding: Mapped[list[float] | None] = mapped_column(
        JSONB,
        nullable=True
        )

    subjects: Mapped[list["Subject"]] = relationship(
        secondary=student_subjects,
        back_populates="students",
        passive_deletes=True,
    )

    classrooms: Mapped[list["Classroom"]] = relationship(
        secondary=classroom_students,
        back_populates="students",
        passive_deletes=True,
    )