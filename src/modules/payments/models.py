import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base
from src.modules.checkout.models import JSONVariant


class PaymentTransaction(Base):
    """A full payment attempt history for an order — one order may have
    multiple payment attempts (a failed delivery followed by a retry, or
    a provider resending a webhook), which `orders.status` alone (a
    single current value) can't represent. Written by
    webhooks/service.py on every processed delivery; not written by
    checkout/service.py itself, since a transaction only really exists
    once the provider confirms an outcome, not at order-creation time
    (see docs/database_schema.md for the full lifecycle)."""

    __tablename__ = "payment_transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=False, default="transfi")
    transaction_id: Mapped[str | None] = mapped_column(String, nullable=True)
    invoice_id: Mapped[str | None] = mapped_column(String, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="BDT")
    status: Mapped[str] = mapped_column(String, nullable=False)
    request_payload: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)
    response_payload: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
