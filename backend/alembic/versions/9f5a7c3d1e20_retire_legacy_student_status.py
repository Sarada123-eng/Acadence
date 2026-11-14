"""retire legacy student status

Revision ID: 9f5a7c3d1e20
Revises: 8e4f6a1b2c39
Create Date: 2026-11-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9f5a7c3d1e20"
down_revision: Union[str, Sequence[str], None] = "8e4f6a1b2c39"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SUPPORTED_STATUS_CHECK = (
    "account_status IN "
    "('pending_verification', 'active', 'suspended', 'deactivated')"
)
LEGACY_STATUS_CHECK = (
    "account_status IN "
    "('legacy_unverified', 'pending_verification', 'active', "
    "'suspended', 'deactivated')"
)


def _alter_status_constraint(status_check: str, server_default: str | None) -> None:
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table("students", recreate="always") as batch_op:
            batch_op.drop_constraint("ck_students_account_status")
            batch_op.alter_column(
                "account_status",
                server_default=server_default,
            )
            batch_op.create_check_constraint(
                "ck_students_account_status",
                status_check,
            )
    else:
        op.drop_constraint(
            "ck_students_account_status",
            "students",
            type_="check",
        )
        op.alter_column(
            "students",
            "account_status",
            server_default=server_default,
        )
        op.create_check_constraint(
            "ck_students_account_status",
            "students",
            status_check,
        )


def upgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE students "
            "SET account_status = 'deactivated' "
            "WHERE account_status = 'legacy_unverified'"
        )
    )
    _alter_status_constraint(SUPPORTED_STATUS_CHECK, None)


def downgrade() -> None:
    _alter_status_constraint(LEGACY_STATUS_CHECK, "legacy_unverified")
