"""add postgres rds production schema

Revision ID: b18bd9478755
Revises: b88b82b2fe7a
Create Date: 2026-07-24 07:41:11.548141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'b18bd9478755'
down_revision: Union[str, Sequence[str], None] = 'b88b82b2fe7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Matches src/modules/checkout/models.py::JSONVariant — real Postgres
# JSONB in production, generic JSON elsewhere (only relevant to
# Base.metadata.create_all() in tests; this migration itself only ever
# runs against Postgres).
_JSONB = sa.JSON().with_variant(JSONB(), "postgresql")


def upgrade() -> None:
    """Upgrade schema."""
    # --- orders: additive columns only, nothing existing dropped/renamed ---
    with op.batch_alter_table("orders") as batch_op:
        # Re-adds a column of the same name/shape Phase 4 deliberately
        # dropped (see e3f4a5b6c7d8) — this time as a plain alias of
        # `id`, backfilled below, not an independently generated value,
        # so that earlier "no second reference" decision still holds in
        # spirit.
        batch_op.add_column(sa.Column("reference_id", sa.String(), nullable=True))
        batch_op.add_column(
            sa.Column("currency", sa.String(), nullable=False, server_default="BDT")
        )
        batch_op.add_column(sa.Column("payment_status", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("order_status", sa.String(), nullable=True))
        batch_op.add_column(
            sa.Column("payment_provider", sa.String(), nullable=False, server_default="transfi")
        )
        batch_op.add_column(sa.Column("payment_reference", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("package_snapshot", _JSONB, nullable=True))
        batch_op.add_column(sa.Column("gateway_response", _JSONB, nullable=True))
        batch_op.create_unique_constraint("uq_orders_reference_id", ["reference_id"])

    op.create_index("ix_orders_payment_status", "orders", ["payment_status"])
    op.create_index("ix_orders_order_status", "orders", ["order_status"])

    # Backfill existing rows — going forward, webhooks/service.py and
    # checkout/service.py keep these live-synced (see docs/database_schema.md).
    op.execute("UPDATE orders SET reference_id = id::text")
    op.execute("UPDATE orders SET payment_status = status")
    op.execute(
        """
        UPDATE orders SET order_status = CASE
            WHEN status = 'PAID' AND fulfilment_status = 'COMPLETED' THEN 'COMPLETED'
            WHEN status = 'PAID' AND fulfilment_status = 'FAILED' THEN 'FULFILLMENT_FAILED'
            WHEN status = 'PAID' THEN 'PROCESSING'
            WHEN status = 'FAILED' THEN 'PAYMENT_FAILED'
            WHEN status = 'CANCELLED' THEN 'CANCELLED'
            ELSE 'PENDING'
        END
        """
    )

    # --- payment_transactions ---
    op.create_table(
        "payment_transactions",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "order_id", sa.Uuid(as_uuid=True), sa.ForeignKey("orders.id"), nullable=False
        ),
        sa.Column("provider", sa.String(), nullable=False, server_default="transfi"),
        sa.Column("transaction_id", sa.String(), nullable=True),
        sa.Column("invoice_id", sa.String(), nullable=True),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(), nullable=False, server_default="BDT"),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("request_payload", _JSONB, nullable=True),
        sa.Column("response_payload", _JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_payment_transactions_order_id", "payment_transactions", ["order_id"]
    )
    op.create_index(
        "ix_payment_transactions_invoice_id", "payment_transactions", ["invoice_id"]
    )
    op.create_index("ix_payment_transactions_status", "payment_transactions", ["status"])

    # --- webhook_events (independent of orders — no FK, per spec) ---
    op.create_table(
        "webhook_events",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("provider", sa.String(), nullable=False, server_default="transfi"),
        sa.Column("event_type", sa.String(), nullable=True),
        sa.Column("event_id", sa.String(), nullable=True),
        sa.Column("payload", _JSONB, nullable=True),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "provider", "event_id", name="uq_webhook_events_provider_event_id"
        ),
    )
    op.create_index("ix_webhook_events_event_type", "webhook_events", ["event_type"])
    op.create_index("ix_webhook_events_processed", "webhook_events", ["processed"])
    op.create_index("ix_webhook_events_created_at", "webhook_events", ["created_at"])

    # --- fulfilments ---
    op.create_table(
        "fulfilments",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "order_id", sa.Uuid(as_uuid=True), sa.ForeignKey("orders.id"), nullable=False
        ),
        sa.Column("guest_checkout_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="PENDING"),
        sa.Column("response_payload", _JSONB, nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fulfilled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_fulfilments_order_id", "fulfilments", ["order_id"])
    op.create_index("ix_fulfilments_status", "fulfilments", ["status"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("fulfilments")
    op.drop_table("webhook_events")
    op.drop_table("payment_transactions")

    op.drop_index("ix_orders_order_status", table_name="orders")
    op.drop_index("ix_orders_payment_status", table_name="orders")

    with op.batch_alter_table("orders") as batch_op:
        batch_op.drop_constraint("uq_orders_reference_id", type_="unique")
        batch_op.drop_column("gateway_response")
        batch_op.drop_column("package_snapshot")
        batch_op.drop_column("payment_reference")
        batch_op.drop_column("payment_provider")
        batch_op.drop_column("order_status")
        batch_op.drop_column("payment_status")
        batch_op.drop_column("currency")
        batch_op.drop_column("reference_id")
