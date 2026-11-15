"""allow OTP challenges before provider acceptance

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-11-15

"""
from typing import Sequence, Union

from alembic import op


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    _alter_last_sent_nullable(True)


def downgrade() -> None:
    op.execute(
        "UPDATE student_email_otp_challenges "
        "SET last_sent_at = created_at "
        "WHERE last_sent_at IS NULL"
    )
    _alter_last_sent_nullable(False)


def _alter_last_sent_nullable(nullable: bool) -> None:
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table(
            "student_email_otp_challenges",
            recreate="always",
        ) as batch_op:
            batch_op.alter_column("last_sent_at", nullable=nullable)
    else:
        op.alter_column(
            "student_email_otp_challenges",
            "last_sent_at",
            nullable=nullable,
        )
