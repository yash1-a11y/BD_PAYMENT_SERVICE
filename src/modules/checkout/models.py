import enum
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base

# Real Postgres JSONB (indexable, queryable) in production; falls back to
# plain JSON so the test suite's SQLite engine — a deliberate, separate
# testing-infrastructure choice, not something this schema work touches —
# can still create the same tables. `postgresql.JSONB` alone doesn't
# compile against SQLite at all.
JSONVariant = JSON().with_variant(JSONB(), "postgresql")


class OrderStatus(str, enum.Enum):
    # Payment status only. Set by Phase 4's webhook handling.
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class FulfilmentStatus(str, enum.Enum):
    # A deliberately separate concern from OrderStatus (payment) — a
    # fulfilment failure must never roll back or change payment status;
    # the payment already happened regardless of whether provisioning the
    # purchased course succeeded.
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class OrderLifecycleStatus(str, enum.Enum):
    """The new, higher-level `orders.order_status` field — distinct from
    OrderStatus (payment-only) and FulfilmentStatus (fulfilment-only).
    Combines both into one overall lifecycle view, set exclusively by
    webhooks/service.py (the one place that already sees both outcomes in
    the same call)."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"  # paid, fulfilment attempt in progress
    COMPLETED = "COMPLETED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    FULFILLMENT_FAILED = "FULFILLMENT_FAILED"
    CANCELLED = "CANCELLED"


class Order(Base):
    __tablename__ = "orders"

    # This id IS the order reference sent to Transfi as customerOrderId —
    # deliberately not paired with a second generated reference value.
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    landing_page_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bd_landing_pages.id"), nullable=False
    )
    variant_id: Mapped[str | None] = mapped_column(String, nullable=True)
    customer_name: Mapped[str] = mapped_column(String, nullable=False)
    customer_email: Mapped[str] = mapped_column(String, nullable=False)
    customer_phone: Mapped[str] = mapped_column(String, nullable=False)
    price_bdt: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False), nullable=False, default=OrderStatus.PENDING
    )
    fulfilment_status: Mapped[FulfilmentStatus] = mapped_column(
        Enum(FulfilmentStatus, native_enum=False),
        nullable=False,
        default=FulfilmentStatus.PENDING,
    )

    # --- Production/RDS schema expansion (docs/postgres_rds.md) ---
    # Added via migration b3c4d5e6f7a8 on top of the existing columns
    # above, which stay authoritative for existing code (checkout API
    # responses, webhook processing, the admin dashboard) — nothing here
    # replaces them. `payment_status`/`order_status` are kept live-synced
    # by webhooks/service.py going forward.

    # A string alias of `id`, not a second generated identifier — keeps
    # Phase 4's "don't generate a second separate reference value"
    # decision intact while satisfying this schema's literal field name.
    reference_id: Mapped[str | None] = mapped_column(String, nullable=True)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="BDT")
    # Denormalized copy of `status`'s value, for reporting/joins against
    # payment_transactions without needing the enum type — kept in sync
    # by webhooks/service.py, never the other source of truth for the
    # existing `status` column or the checkout API's response shape.
    payment_status: Mapped[str | None] = mapped_column(String, nullable=True)
    order_status: Mapped[OrderLifecycleStatus | None] = mapped_column(
        Enum(OrderLifecycleStatus, native_enum=False), nullable=True
    )
    payment_provider: Mapped[str] = mapped_column(String, nullable=False, default="transfi")
    # The payment provider's own stable reference for this order (e.g.
    # Transfi's invoiceId) — not assumed to be any one specific field
    # name; see transfi/service.py::initiate_payment for how this is
    # resolved defensively from whichever identifier the provider's
    # response actually contains.
    payment_reference: Mapped[str | None] = mapped_column(String, nullable=True)
    # Lightweight point-in-time snapshot of what was actually purchased
    # (package_id/title/thumbnail/selling_price_bdt), captured at checkout
    # time — package details are otherwise never stored permanently (they
    # always come live from the Package System API), but an order's
    # historical record must stay accurate even if the live catalogue
    # entry later changes or is removed.
    package_snapshot: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)
    # The raw webhook payload Transfi sent for the delivery that last
    # transitioned this order's status — for debugging/audit; WebhookLog
    # already stores every delivery in full, this is just the one that
    # mattered for this specific order, denormalized for quick access.
    gateway_response: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
