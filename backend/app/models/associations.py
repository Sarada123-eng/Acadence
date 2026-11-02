from sqlalchemy import Column, ForeignKey, Table

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
