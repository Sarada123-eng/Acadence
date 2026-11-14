"""add student identity fields and account status

Revision ID: 6c2d4e8f1a90
Revises: 5f1a2c9d8e7b
Create Date: 2026-11-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6c2d4e8f1a90"
down_revision: Union[str, Sequence[str], None] = "5f1a2c9d8e7b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "students",
        sa.Column("institutional_student_id", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "students",
        sa.Column("normalized_student_id", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "students",
        sa.Column("institutional_email", sa.String(length=320), nullable=True),
    )
    op.add_column(
        "students",
        sa.Column("normalized_email", sa.String(length=320), nullable=True),
    )
    op.add_column(
        "students",
        sa.Column(
            "account_status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'legacy_unverified'"),
        ),
    )
    op.add_column(
        "students",
        sa.Column(
            "email_verified_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "students",
        sa.Column(
            "identity_verified_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.create_index(
        "uq_students_normalized_student_id",
        "students",
        ["normalized_student_id"],
        unique=True,
    )
    op.create_index(
        "uq_students_normalized_email",
        "students",
        ["normalized_email"],
        unique=True,
    )
    op.create_index(
        "ix_students_account_status",
        "students",
        ["account_status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_students_account_status", table_name="students")
    op.drop_index("uq_students_normalized_email", table_name="students")
    op.drop_index("uq_students_normalized_student_id", table_name="students")
    op.drop_column("students", "identity_verified_at")
    op.drop_column("students", "email_verified_at")
    op.drop_column("students", "account_status")
    op.drop_column("students", "normalized_email")
    op.drop_column("students", "institutional_email")
    op.drop_column("students", "normalized_student_id")
    op.drop_column("students", "institutional_student_id")
