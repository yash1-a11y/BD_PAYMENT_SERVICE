from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.middleware.auth import get_current_admin
from src.modules.admin_auth.models import AdminUser
from src.modules.admin_auth.schemas import LoginRequest, LoginResponse
from src.modules.admin_auth.security import create_access_token
from src.modules.admin_auth.service import authenticate_admin
from src.modules.audit.models import AuditAction
from src.modules.audit.service import log_action

router = APIRouter(prefix="/bd-admin/api/auth", tags=["admin-auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    admin = authenticate_admin(db, payload.email, payload.password)
    if admin is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect")

    return LoginResponse(access_token=create_access_token(admin.id), role=admin.role.value)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)
) -> dict[str, bool]:
    log_action(db, admin.id, AuditAction.LOGOUT)
    return {"success": True}
