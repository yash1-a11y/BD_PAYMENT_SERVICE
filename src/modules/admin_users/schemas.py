import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class AdminOut(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None

    model_config = {"from_attributes": True}


class AdminCreate(BaseModel):
    email: EmailStr
    password: str


class AdminUpdate(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    new_password: str
