import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Enum, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"


class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # No column-level unique=True here — superseded by the case-insensitive
    # functional unique index below, which is strictly stronger (anything
    # that violates plain case-sensitive uniqueness also violates a
    # case-insensitive one, so keeping both would be redundant).
    email: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[AdminRole] = mapped_column(
        Enum(AdminRole, native_enum=False), nullable=False, default=AdminRole.ADMIN
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Enforced at the database level, not just in application code, so a
    # race between two concurrent "create admin" requests can't both slip
    # past an app-level check-then-insert and create Admin@x.com /
    # admin@x.com as two distinct accounts.
    __table_args__ = (Index("admin_users_email_lower_idx", func.lower(email), unique=True),)
