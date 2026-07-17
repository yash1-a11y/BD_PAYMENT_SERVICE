import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.modules.admin_auth.models import AdminRole, AdminUser
from src.modules.admin_auth.security import decode_access_token

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> AdminUser:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        admin_id = decode_access_token(credentials.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    admin = db.get(AdminUser, admin_id)
    if admin is None or not admin.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    return admin


def require_super_admin(admin: AdminUser = Depends(get_current_admin)) -> AdminUser:
    if admin.role != AdminRole.SUPER_ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Super admin access required")
    return admin
