import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class CatalogueCreate(BaseModel):
    package_id: str
    price_bdt: Decimal
    published: bool = False


class CatalogueUpdate(BaseModel):
    price_bdt: Decimal
    published: bool


class CatalogueOut(BaseModel):
    id: uuid.UUID
    display_code: str
    package_id: str
    price_bdt: Decimal
    published: bool
    display_order: int
    created_at: datetime
    updated_at: datetime
    title: str | None = None
    category: str | None = None
    validity_months: int | None = None

    model_config = {"from_attributes": True}


class ReorderRequest(BaseModel):
    orderedIds: list[uuid.UUID]


class PackageLookupOut(BaseModel):
    package_id: str
    title: str
    category: str
    validity_months: int | None
    thumbnail_url: str | None
    india_mrp: float | None
    source_published: bool
