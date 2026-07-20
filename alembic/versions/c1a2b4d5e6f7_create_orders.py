"""create orders

Revision ID: c1a2b4d5e6f7
Revises: 89899fa92660
Create Date: 2026-07-20 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1a2b4d5e6f7'
down_revision: Union[str, Sequence[str], None] = '89899fa92660'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "orders",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("reference_id", sa.String(), nullable=False),
        sa.Column(
            "landing_page_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("bd_landing_pages.id"),
            nullable=False,
        ),
        sa.Column("customer_name", sa.String(), nullable=False),
        sa.Column("customer_email", sa.String(), nullable=False),
        sa.Column("customer_phone", sa.String(), nullable=False),
        sa.Column("price_bdt", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'PENDING'")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("reference_id", name="uq_orders_reference_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("orders")
