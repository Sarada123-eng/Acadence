from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.associations import student_subjects
from app.models.student import Student


def get_classroom_biometric_embeddings(
    db: Session,
    subject_id: int,
) -> list[tuple[int, list[float], list[float]]]:
    """
    Return biometric embeddings of students enrolled in a classroom.

    Each tuple contains:

        (
            student_id,
            face_embedding,
            voice_embedding,
        )
    """

    statement = (
        select(Student.id, Student.face_embedding, Student.voice_embedding)
        .join(
            student_subjects,
            Student.id == student_subjects.c.student_id,
        )
        .where(student_subjects.c.subject_id == subject_id)
    )

    return list(db.execute(statement).all())
