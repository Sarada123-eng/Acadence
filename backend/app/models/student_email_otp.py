from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.models.student import Student


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StudentEmailOtpChallenge(Base):
    __tablename__ = "student_email_otp_challenges"
    __table_args__ = (
        CheckConstraint(
            "attempt_count >= 0",
            name="ck_student_email_otp_attempt_count_non_negative",
        ),
        UniqueConstraint(
            "student_id",
            name="uq_student_email_otp_challenges_student_id",
        ),
        Index(
            "ix_student_email_otp_challenges_expires_at",
            "expires_at",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )

    otp_digest: Mapped[str] = mapped_column(String(64), nullable=False)

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    attempt_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    last_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    invalidated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    student: Mapped[Student] = relationship(
        "Student",
        back_populates="email_otp_challenge",
    )
