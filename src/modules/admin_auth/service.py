from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.modules.admin_auth.models import AdminUser
from src.modules.admin_auth.security import verify_password
from src.modules.audit.models import AuditAction
from src.modules.audit.service import log_action


def authenticate_admin(db: Session, email: str, password: str) -> AdminUser | None:
    # Case-insensitive lookup — matches regardless of how the email was
    # originally stored (this doesn't depend on a one-time data migration
    # to lowercase existing rows; new writes are normalized separately in
    # admin_users/service.py).
    admin = db.scalar(
        select(AdminUser).where(func.lower(AdminUser.email) == email.strip().lower())
    )
    if admin is None or not admin.is_active or not verify_password(password, admin.password_hash):
        return None

    admin.last_login_at = datetime.now(UTC)
    db.commit()
    log_action(db, admin.id, AuditAction.LOGIN)
    return admin
