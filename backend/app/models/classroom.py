from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.models.associations import classroom_students

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.subject import Subject


class Classroom(Base):
    __tablename__ = "classrooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    section: Mapped[str | None] = mapped_column(String(20), nullable=True)

    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    join_code: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    subject: Mapped["Subject"] = relationship(
        back_populates="classrooms",
    )

    students: Mapped[list["Student"]] = relationship(
        secondary=classroom_students,
        back_populates="classrooms",
        passive_deletes=True,
    )
