"""create admin_users and bd_landing_pages

Revision ID: a3e133f0b3fd
Revises: 
Create Date: 2026-07-16 13:28:25.122940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3e133f0b3fd'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "admin_users",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("email", name="uq_admin_users_email"),
    )

    op.create_table(
        "bd_landing_pages",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("display_code", sa.String(), nullable=False),
        sa.Column("package_id", sa.String(), nullable=False),
        sa.Column("price_bdt", sa.Numeric(10, 2), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("display_code", name="uq_bd_landing_pages_display_code"),
        sa.UniqueConstraint("package_id", name="uq_bd_landing_pages_package_id"),
        sa.CheckConstraint("price_bdt > 0", name="ck_bd_landing_pages_price_positive"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("bd_landing_pages")
    op.drop_table("admin_users")
