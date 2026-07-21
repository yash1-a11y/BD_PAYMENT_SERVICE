import re
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints, field_validator

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

# Local Bangladesh mobile number, without the +880 country code — exactly
# 10 digits, starting with 1 (e.g. "1712345678").
_LOCAL_PHONE_PATTERN = re.compile(r"^1\d{9}$")


class OrderCreate(BaseModel):
    package_id: NonEmptyStr
    name: NonEmptyStr
    email: EmailStr
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        value = value.strip()
        if not _LOCAL_PHONE_PATTERN.match(value):
            raise ValueError(
                "Phone number must be exactly 10 digits, starting with 1 "
                "(e.g. 1712345678), without the +880 prefix."
            )
        return value


class OrderOut(BaseModel):
    order_id: uuid.UUID
    package_id: str
    title: str
    price_bdt: Decimal
    status: str
    payment_url: str
    created_at: datetime


class OrderStatusOut(BaseModel):
    order_id: uuid.UUID
    # Order.id IS the Transfi reference (Phase 4 deliberately avoided a
    # second generated value) — exposed under both names since Phase 5's
    # spec calls for `referenceId` in this response.
    reference_id: uuid.UUID
    payment_status: str
    package_allocation_status: str
    package_title: str
    amount_bdt: Decimal
    created_at: datetime
    updated_at: datetime
