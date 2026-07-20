import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


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
