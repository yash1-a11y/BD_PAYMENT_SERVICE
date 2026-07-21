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
    # Both admin FKs use ON DELETE SET NULL — audit_logs is a historical
    # record, so deleting an admin must never fail or cascade-delete past
    # audit rows; it should just lose that specific actor/target identity.
    # See migration 28641e6c7568 for why this was added/corrected.
    actor_admin_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction, native_enum=False), nullable=False)
    target_admin_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
