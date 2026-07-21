"""create webhook_logs, add orders.fulfilment_status

Revision ID: f4a5b6c7d8e9
Revises: e3f4a5b6c7d8
Create Date: 2026-07-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4a5b6c7d8e9'
down_revision: Union[str, Sequence[str], None] = 'e3f4a5b6c7d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "orders",
        sa.Column(
            "fulfilment_status",
            sa.String(),
            nullable=False,
            server_default=sa.text("'PENDING'"),
        ),
    )

    op.create_table(
        "webhook_logs",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("headers", sa.JSON(), nullable=False),
        sa.Column("raw_body", sa.Text(), nullable=False),
        sa.Column("signature_header", sa.String(), nullable=True),
        sa.Column("signature_valid", sa.Boolean(), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=True),
        sa.Column("entity_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("processing_result", sa.String(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("webhook_logs")
    op.drop_column("orders", "fulfilment_status")
