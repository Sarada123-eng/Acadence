"""add pending student registration fields

Revision ID: 8e4f6a1b2c39
Revises: 7d3e5f9a2b14
Create Date: 2026-11-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8e4f6a1b2c39"
down_revision: Union[str, Sequence[str], None] = "7d3e5f9a2b14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "students",
        sa.Column("registration_reference", sa.String(length=36), nullable=True),
    )
    op.add_column(
        "students",
        sa.Column(
            "pending_registration_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.create_index(
        "uq_students_registration_reference",
        "students",
        ["registration_reference"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "uq_students_registration_reference",
        table_name="students",
    )
    op.drop_column("students", "pending_registration_expires_at")
    op.drop_column("students", "registration_reference")
