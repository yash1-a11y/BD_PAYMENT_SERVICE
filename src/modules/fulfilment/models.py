import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base
from src.modules.checkout.models import FulfilmentStatus, JSONVariant


class Fulfilment(Base):
    """One row per Guest Checkout allocation attempt for an order — the
    richer, retry-aware home for what `orders.fulfilment_status` (a
    single current value) already tracks; that column stays exactly as
    it is, read/written by webhooks/service.py unchanged, since this
    table adds history/detail rather than replacing it. Written by
    fulfilment/service.py::allocate_package on every attempt.
    `guest_checkout_id` stays NULL until the real Guest Checkout API
    (src/integrations/guest_checkout/, prepared but not yet enabled) is
    actually called — see docs/guest_checkout_integration.md."""

    __tablename__ = "fulfilments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), nullable=False)
    guest_checkout_id: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[FulfilmentStatus] = mapped_column(
        Enum(FulfilmentStatus, native_enum=False),
        nullable=False,
        default=FulfilmentStatus.PENDING,
    )
    response_payload: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fulfilled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
