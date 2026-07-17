import uuid

from sqlalchemy.orm import Session

from src.modules.audit.models import AuditAction, AuditLog


def log_action(
    db: Session,
    actor_admin_id: uuid.UUID | None,
    action: AuditAction,
    target_admin_id: uuid.UUID | None = None,
) -> None:
    db.add(AuditLog(actor_admin_id=actor_admin_id, action=action, target_admin_id=target_admin_id))
    db.commit()
