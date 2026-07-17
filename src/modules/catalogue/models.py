import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class BDLandingPage(Base):
    __tablename__ = "bd_landing_pages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    display_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    package_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    price_bdt: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    published: Mapped[bool] = mapped_column(default=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
