"""add student email OTP challenges

Revision ID: a1b2c3d4e5f6
Revises: 9f5a7c3d1e20
Create Date: 2026-11-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "9f5a7c3d1e20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "student_email_otp_challenges",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("otp_digest", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invalidated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "attempt_count >= 0",
            name="ck_student_email_otp_attempt_count_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["students.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "student_id",
            name="uq_student_email_otp_challenges_student_id",
        ),
    )
    op.create_index(
        "ix_student_email_otp_challenges_expires_at",
        "student_email_otp_challenges",
        ["expires_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_student_email_otp_challenges_expires_at",
        table_name="student_email_otp_challenges",
    )
    op.drop_table("student_email_otp_challenges")
