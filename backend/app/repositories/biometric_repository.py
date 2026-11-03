from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.associations import classroom_students
from app.models.student import Student


def get_classroom_biometric_embeddings(
    db: Session,
    classroom_id: int,
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
            classroom_students,
            Student.id == classroom_students.c.student_id,
        )
        .where(classroom_students.c.classroom_id == classroom_id)
    )

    return list(db.execute(statement).all())
