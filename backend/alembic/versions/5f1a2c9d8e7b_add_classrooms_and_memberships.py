"""add classrooms and classroom memberships

Revision ID: 5f1a2c9d8e7b
Revises: 3a2c8f4d91b0
Create Date: 2026-11-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5f1a2c9d8e7b"
down_revision: Union[str, Sequence[str], None] = "3a2c8f4d91b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "classrooms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("section", sa.String(length=20), nullable=True),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("join_code", sa.String(length=64), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subjects.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("join_code"),
    )
    op.create_index(
        "ix_classrooms_id",
        "classrooms",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_classrooms_subject_id",
        "classrooms",
        ["subject_id"],
        unique=False,
    )
    op.create_index(
        "ix_classrooms_join_code",
        "classrooms",
        ["join_code"],
        unique=False,
    )

    op.create_table(
        "classroom_students",
        sa.Column("classroom_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["classroom_id"],
            ["classrooms.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["students.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("classroom_id", "student_id"),
    )
    op.create_index(
        "ix_classroom_students_student_id",
        "classroom_students",
        ["student_id"],
        unique=False,
    )

    connection = op.get_bind()
    subjects = connection.execute(
        sa.text(
            """
            SELECT id, name, section
            FROM subjects
            ORDER BY id
            """
        )
    ).mappings()

    for subject in subjects:
        legacy_name = subject["section"] or f"{subject['name']} Classroom"
        join_code = f"legacy-{subject['id']}"
        connection.execute(
            sa.text(
                """
                INSERT INTO classrooms (name, section, subject_id, join_code)
                VALUES (:name, :section, :subject_id, :join_code)
                """
            ),
            {
                "name": legacy_name,
                "section": subject["section"],
                "subject_id": subject["id"],
                "join_code": join_code,
            },
        )

    connection.execute(
        sa.text(
            """
            INSERT INTO classroom_students (classroom_id, student_id)
            SELECT c.id, ss.student_id
            FROM student_subjects ss
            JOIN classrooms c ON c.subject_id = ss.subject_id
            """
        )
    )


def downgrade() -> None:
    op.drop_index(
        "ix_classroom_students_student_id",
        table_name="classroom_students",
    )
    op.drop_table("classroom_students")
    op.drop_index("ix_classrooms_join_code", table_name="classrooms")
    op.drop_index("ix_classrooms_subject_id", table_name="classrooms")
    op.drop_index("ix_classrooms_id", table_name="classrooms")
    op.drop_table("classrooms")
