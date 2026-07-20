import enum
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
