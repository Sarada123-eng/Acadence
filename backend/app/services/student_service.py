from sqlalchemy.orm import Session

from app.models.student import Student


def create_student(db: Session, name: str) -> Student:
    student = Student(
        name=name,
        face_embedding=None,
        voice_embedding=None,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student
