from sqlalchemy import Column, DateTime, ForeignKey, Table, func

from app.database.connection import Base


student_subjects = Table(
    "student_subjects",
    Base.metadata,
    Column(
        "student_id",
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "subject_id",
        ForeignKey("subjects.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


classroom_students = Table(
    "classroom_students",
    Base.metadata,
    Column(
        "classroom_id",
        ForeignKey("classrooms.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "student_id",
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "joined_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
)
