"""add admin role, is_active, and audit_logs

Revision ID: 89899fa92660
Revises: a3e133f0b3fd
Create Date: 2026-07-16 16:59:54.161379

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89899fa92660'
down_revision: Union[str, Sequence[str], None] = 'a3e133f0b3fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "admin_users",
        sa.Column("role", sa.String(), nullable=False, server_default=sa.text("'ADMIN'")),
    )
    op.add_column(
        "admin_users",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    # Any admin row that existed before roles existed was created via the manual
    # seed script — treat it as the first SUPER_ADMIN.
    op.execute("UPDATE admin_users SET role = 'SUPER_ADMIN'")

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("actor_admin_id", sa.Uuid(as_uuid=True), sa.ForeignKey("admin_users.id"), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("target_admin_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("audit_logs")
    op.drop_column("admin_users", "is_active")
    op.drop_column("admin_users", "role")
