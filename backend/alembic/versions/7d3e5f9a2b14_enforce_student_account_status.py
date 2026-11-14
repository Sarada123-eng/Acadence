"""enforce student account status values

Revision ID: 7d3e5f9a2b14
Revises: 6c2d4e8f1a90
Create Date: 2026-11-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7d3e5f9a2b14"
down_revision: Union[str, Sequence[str], None] = "6c2d4e8f1a90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

STATUS_CHECK = (
    "account_status IN "
    "('legacy_unverified', 'pending_verification', 'active', "
    "'suspended', 'deactivated')"
)


def upgrade() -> None:
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table("students") as batch_op:
            batch_op.create_check_constraint(
                "ck_students_account_status",
                STATUS_CHECK,
            )
    else:
        op.create_check_constraint(
            "ck_students_account_status",
            "students",
            STATUS_CHECK,
        )


def downgrade() -> None:
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table("students") as batch_op:
            batch_op.drop_constraint("ck_students_account_status")
    else:
        op.drop_constraint(
            "ck_students_account_status",
            "students",
            type_="check",
        )
