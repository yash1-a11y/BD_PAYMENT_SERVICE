import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.middleware.auth import require_super_admin
from src.modules.admin_auth.models import AdminUser
from src.modules.admin_users import service
from src.modules.admin_users.exceptions import (
    AdminNotFoundError,
    DuplicateEmailError,
    SelfActionNotAllowedError,
)
from src.modules.admin_users.schemas import AdminCreate, AdminOut, AdminUpdate, ResetPasswordRequest

router = APIRouter(
    prefix="/bd-admin/api/admins",
    tags=["admin-users"],
    dependencies=[Depends(require_super_admin)],
)


@router.get("", response_model=list[AdminOut])
def list_admins(db: Session = Depends(get_db)):
    return service.list_admins(db)


@router.post("", response_model=AdminOut, status_code=status.HTTP_201_CREATED)
def create_admin(
    payload: AdminCreate,
    actor: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    try:
        return service.create_admin(db, actor, payload.email, payload.password)
    except DuplicateEmailError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc))


@router.put("/{admin_id}", response_model=AdminOut)
def update_admin(
    admin_id: uuid.UUID,
    payload: AdminUpdate,
    actor: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    try:
        return service.update_admin(db, actor, admin_id, payload.email)
    except AdminNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Admin not found.")
    except DuplicateEmailError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch("/{admin_id}/enable", response_model=AdminOut)
def enable_admin(admin_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return service.enable_admin(db, admin_id)
    except AdminNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Admin not found.")


@router.patch("/{admin_id}/disable", response_model=AdminOut)
def disable_admin(
    admin_id: uuid.UUID,
    actor: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    try:
        return service.disable_admin(db, actor, admin_id)
    except AdminNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Admin not found.")
    except SelfActionNotAllowedError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/{admin_id}/reset-password", response_model=AdminOut)
def reset_password(
    admin_id: uuid.UUID,
    payload: ResetPasswordRequest,
    actor: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    try:
        return service.reset_password(db, actor, admin_id, payload.new_password)
    except AdminNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Admin not found.")


@router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin(
    admin_id: uuid.UUID,
    actor: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    try:
        service.delete_admin(db, actor, admin_id)
    except AdminNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Admin not found.")
    except SelfActionNotAllowedError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc))
