import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.modules.admin_auth.models import AdminRole, AdminUser
from src.modules.admin_auth.security import hash_password
from src.modules.admin_users.exceptions import (
    AdminNotFoundError,
    DuplicateEmailError,
    SelfActionNotAllowedError,
)
from src.modules.audit.models import AuditAction
from src.modules.audit.service import log_action


def list_admins(db: Session) -> list[AdminUser]:
    return list(db.scalars(select(AdminUser).order_by(AdminUser.created_at.asc())))


def _get_admin(db: Session, admin_id: uuid.UUID) -> AdminUser:
    admin = db.get(AdminUser, admin_id)
    if admin is None:
        raise AdminNotFoundError(str(admin_id))
    return admin


def create_admin(db: Session, actor: AdminUser, email: str, password: str) -> AdminUser:
    # Normalized to lowercase for storage, and looked up case-insensitively
    # against whatever case existing rows already have — Admin@x.com and
    # admin@x.com must never coexist as distinct accounts. The DB-level
    # functional unique index (admin_users_email_lower_idx) is the real
    # guarantee against a race between two concurrent creates; this check
    # is just for a clean 409 instead of a raw IntegrityError.
    email = email.strip().lower()
    existing = db.scalar(select(AdminUser).where(func.lower(AdminUser.email) == email))
    if existing is not None:
        raise DuplicateEmailError("An admin with this email already exists.")

    admin = AdminUser(
        email=email,
        password_hash=hash_password(password),
        role=AdminRole.ADMIN,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    log_action(db, actor.id, AuditAction.ADMIN_CREATED, target_admin_id=admin.id)
    return admin


def update_admin(db: Session, actor: AdminUser, admin_id: uuid.UUID, email: str) -> AdminUser:
    admin = _get_admin(db, admin_id)

    email = email.strip().lower()
    existing = db.scalar(select(AdminUser).where(func.lower(AdminUser.email) == email))
    if existing is not None and existing.id != admin_id:
        raise DuplicateEmailError("An admin with this email already exists.")

    admin.email = email
    db.commit()
    db.refresh(admin)
    log_action(db, actor.id, AuditAction.ADMIN_UPDATED, target_admin_id=admin.id)
    return admin


def enable_admin(db: Session, admin_id: uuid.UUID) -> AdminUser:
    admin = _get_admin(db, admin_id)
    admin.is_active = True
    db.commit()
    db.refresh(admin)
    return admin


def disable_admin(db: Session, actor: AdminUser, admin_id: uuid.UUID) -> AdminUser:
    if admin_id == actor.id:
        raise SelfActionNotAllowedError("You cannot disable your own account.")

    admin = _get_admin(db, admin_id)
    admin.is_active = False
    db.commit()
    db.refresh(admin)
    log_action(db, actor.id, AuditAction.ADMIN_DISABLED, target_admin_id=admin.id)
    return admin


def reset_password(db: Session, actor: AdminUser, admin_id: uuid.UUID, new_password: str) -> AdminUser:
    admin = _get_admin(db, admin_id)
    admin.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(admin)
    log_action(db, actor.id, AuditAction.PASSWORD_RESET, target_admin_id=admin.id)
    return admin


def delete_admin(db: Session, actor: AdminUser, admin_id: uuid.UUID) -> None:
    if admin_id == actor.id:
        raise SelfActionNotAllowedError("You cannot delete your own account.")

    admin = _get_admin(db, admin_id)
    db.delete(admin)
    db.commit()
