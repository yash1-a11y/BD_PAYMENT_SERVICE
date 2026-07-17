import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class AuditAction(str, enum.Enum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    ADMIN_CREATED = "ADMIN_CREATED"
    ADMIN_UPDATED = "ADMIN_UPDATED"
    ADMIN_DISABLED = "ADMIN_DISABLED"
    PASSWORD_RESET = "PASSWORD_RESET"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    actor_admin_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("admin_users.id"), nullable=True
    )
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction, native_enum=False), nullable=False)
    target_admin_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
