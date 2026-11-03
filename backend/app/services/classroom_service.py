import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.classroom import Classroom
from app.models.student import Student
from app.models.subject import Subject
from app.models.teacher import Teacher


def create_subject(
    db: Session,
    teacher_id: int,
    name: str,
    subject_code: str,
    section: str | None,
) -> Subject:
    if db.get(Teacher, teacher_id) is None:
        raise ValueError(f"Teacher with ID {teacher_id} does not exist.")

    subject = Subject(
        name=name,
        subject_code=subject_code,
        section=section or "",
        teacher_id=teacher_id,
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def create_classroom(
    db: Session,
    subject_id: int,
    name: str,
    section: str | None,
) -> Classroom:
    subject = db.get(Subject, subject_id)
    if subject is None:
        raise ValueError(f"Subject with ID {subject_id} does not exist.")

    classroom = Classroom(
        name=name,
        section=section,
        subject_id=subject_id,
        join_code=secrets.token_urlsafe(12),
    )
    db.add(classroom)
    db.commit()
    db.refresh(classroom)
    return classroom


def get_teacher_classrooms(db: Session, teacher_id: int) -> list[Classroom]:
    statement = (
        select(Classroom)
        .join(Classroom.subject)
        .where(Subject.teacher_id == teacher_id)
        .order_by(Classroom.id)
    )
    return list(db.scalars(statement).all())


def join_classroom(
    db: Session,
    join_code: str,
    student_id: int,
) -> tuple[Classroom, bool]:
    classroom = db.scalar(
        select(Classroom).where(
            Classroom.join_code == join_code,
            Classroom.is_active.is_(True),
        )
    )
    if classroom is None:
        raise ValueError("Classroom join code is invalid or inactive.")

    if db.get(Student, student_id) is None:
        raise ValueError(f"Student with ID {student_id} does not exist.")

    already_joined = any(
        student.id == student_id for student in classroom.students
    )
    if not already_joined:
        student = db.get(Student, student_id)
        if student is None:
            raise ValueError(f"Student with ID {student_id} does not exist.")
        classroom.students.append(student)
        db.commit()

    return classroom, not already_joined
