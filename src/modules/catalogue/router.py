import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.integrations.package_system.client import PackageNotFoundError
from src.middleware.auth import get_current_admin
from src.modules.catalogue import service
from src.modules.catalogue.exceptions import (
    CatalogueEntryNotFoundError,
    DuplicatePackageIdError,
    InvalidPriceError,
    PackageNotEligibleError,
)
from src.modules.catalogue.schemas import (
    CatalogueCreate,
    CatalogueOut,
    CatalogueUpdate,
    PackageLookupOut,
    ReorderRequest,
)

router = APIRouter(
    prefix="/bd-admin/api",
    tags=["catalogue"],
    dependencies=[Depends(get_current_admin)],
)


def _field_error(status_code: int, field: str, message: str) -> HTTPException:
    return HTTPException(status_code, detail=[{"field": field, "message": message}])


@router.get("/landing-pages", response_model=list[CatalogueOut])
def list_landing_pages(search: str | None = None, db: Session = Depends(get_db)):
    return service.list_catalogue(db, search)


@router.get("/package-lookup/{package_id}", response_model=PackageLookupOut)
def package_lookup(package_id: str):
    try:
        package = service.lookup_package(package_id)
    except PackageNotFoundError:
        raise _field_error(
            status.HTTP_404_NOT_FOUND,
            "package_id",
            "Package ID not found in the package system. Check the ID and fetch again.",
        )

    return PackageLookupOut(
        package_id=package.package_id,
        title=package.title,
        category=package.category,
        validity_months=package.validity_months,
        thumbnail_url=package.thumbnail_url,
        india_mrp=package.india_mrp,
        source_published=package.is_eligible,
    )


@router.post("/landing-pages", response_model=CatalogueOut, status_code=status.HTTP_201_CREATED)
def create_landing_page(payload: CatalogueCreate, db: Session = Depends(get_db)):
    try:
        return service.create_catalogue_entry(
            db, payload.package_id, payload.price_bdt, payload.published
        )
    except InvalidPriceError as exc:
        raise _field_error(status.HTTP_422_UNPROCESSABLE_ENTITY, "price_bdt", str(exc))
    except DuplicatePackageIdError as exc:
        raise _field_error(status.HTTP_409_CONFLICT, "package_id", str(exc))
    except PackageNotFoundError:
        raise _field_error(
            status.HTTP_404_NOT_FOUND,
            "package_id",
            "Package ID not found in the package system. Check the ID and fetch again.",
        )
    except PackageNotEligibleError as exc:
        raise _field_error(status.HTTP_422_UNPROCESSABLE_ENTITY, "package_id", str(exc))


@router.put("/landing-pages/reorder", status_code=status.HTTP_200_OK)
def reorder_landing_pages(payload: ReorderRequest, db: Session = Depends(get_db)):
    try:
        service.reorder_catalogue(db, payload.orderedIds)
    except CatalogueEntryNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Landing page not found.")
    return {"success": True}


@router.put("/landing-pages/{entry_id}", response_model=CatalogueOut)
def update_landing_page(entry_id: uuid.UUID, payload: CatalogueUpdate, db: Session = Depends(get_db)):
    try:
        return service.update_catalogue_entry(db, entry_id, payload.price_bdt, payload.published)
    except InvalidPriceError as exc:
        raise _field_error(status.HTTP_422_UNPROCESSABLE_ENTITY, "price_bdt", str(exc))
    except CatalogueEntryNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Landing page not found.")


@router.delete("/landing-pages/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_landing_page(entry_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        service.delete_catalogue_entry(db, entry_id)
    except CatalogueEntryNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Landing page not found.")


@router.put("/landing-pages/{entry_id}/publish", response_model=CatalogueOut)
def publish_landing_page(entry_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return service.set_published(db, entry_id, True)
    except CatalogueEntryNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Landing page not found.")


@router.put("/landing-pages/{entry_id}/unpublish", response_model=CatalogueOut)
def unpublish_landing_page(entry_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return service.set_published(db, entry_id, False)
    except CatalogueEntryNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Landing page not found.")
