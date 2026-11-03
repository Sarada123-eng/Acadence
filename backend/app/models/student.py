from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.database.connection import Base
from app.models.associations import classroom_students, student_subjects

if TYPE_CHECKING:
    from app.models.classroom import Classroom
    from app.models.subject import Subject


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
        )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
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