from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.database.connection import Base
from app.models.associations import student_subjects
from app.models.teacher import Teacher

if TYPE_CHECKING:
    from app.models.classroom import Classroom
    from app.models.student import Student

class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(
        primary_key=True, 
        index=True
        )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
        )

    subject_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
        )

    section: Mapped[str] = mapped_column(
        String(20),
        nullable=False
        )

    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id", ondelete="SET NULL"),
        nullable=True
        )

    teacher: Mapped["Teacher | None"] = relationship(
        back_populates="subjects"
        )

    students: Mapped[list["Student"]] = relationship(
        secondary=student_subjects,
        back_populates="subjects",
        passive_deletes=True,
    )

    classrooms: Mapped[list["Classroom"]] = relationship(
        back_populates="subject",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )