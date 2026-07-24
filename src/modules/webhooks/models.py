import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base
from src.modules.checkout.models import JSONVariant


class WebhookLog(Base):
    """Every Transfi webhook delivery, traceable for debugging — persisted
    regardless of how processing turns out (invalid signature, unknown
    order, successfully processed, etc.)."""

    __tablename__ = "webhook_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    headers: Mapped[dict] = mapped_column(JSON, nullable=False)
    raw_body: Mapped[str] = mapped_column(Text, nullable=False)
    signature_header: Mapped[str | None] = mapped_column(String, nullable=True)
    signature_valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String, nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    processing_result: Mapped[str] = mapped_column(String, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class WebhookEvent(Base):
    """A second, independent record of webhook deliveries — added
    alongside WebhookLog (which keeps being written exactly as before,
    unchanged), not replacing it. WebhookLog is this project's original,
    full-fidelity debugging trail (raw headers/body, every processing
    outcome); WebhookEvent is the new production-schema table
    (docs/postgres_rds.md), deliberately independent of `orders` — no FK
    here, matching WebhookLog's own precedent of resolving order linkage
    from payload content rather than a hard foreign key."""

    __tablename__ = "webhook_events"
    __table_args__ = (
        Index(
            "uq_webhook_events_provider_event_id",
            "provider",
            "event_id",
            unique=True,
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String, nullable=False, default="transfi")
    event_type: Mapped[str | None] = mapped_column(String, nullable=True)
    event_id: Mapped[str | None] = mapped_column(String, nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)
    processed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
