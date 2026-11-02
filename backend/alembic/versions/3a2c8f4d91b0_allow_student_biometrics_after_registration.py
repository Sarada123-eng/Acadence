"""allow student biometrics after registration

Revision ID: 3a2c8f4d91b0
Revises: 1273d4fcf721
Create Date: 2026-09-28

"""
from typing import Sequence, Union

from alembic import op


revision: str = "3a2c8f4d91b0"
down_revision: Union[str, Sequence[str], None] = "1273d4fcf721"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("students", "face_embedding", nullable=True)
    op.alter_column("students", "voice_embedding", nullable=True)


def downgrade() -> None:
    op.alter_column("students", "voice_embedding", nullable=False)
    op.alter_column("students", "face_embedding", nullable=False)
