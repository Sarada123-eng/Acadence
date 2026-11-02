from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.subject import Subject

class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(
        primary_key=True, 
        index=True
        )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
        )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
        )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
        )

    subjects: Mapped[list["Subject"]] = relationship(
        back_populates="teacher",
        passive_deletes=True # passive delete true means that when a teacher is deleted, the subjects associated with that teacher will not be deleted automatically. Instead, the foreign key in the subjects table will be set to NULL. This is useful if you want to keep the subjects in the database even if the teacher is deleted.
        )
    