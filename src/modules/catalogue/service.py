import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.integrations.package_system.client import PackageDetails, fetch_package
from src.modules.catalogue.exceptions import (
    CatalogueEntryNotFoundError,
    DuplicatePackageIdError,
    InvalidPriceError,
    PackageNotEligibleError,
)
from src.modules.catalogue.models import BDLandingPage
from src.modules.catalogue.schemas import CatalogueOut


def to_catalogue_out(
    entry: BDLandingPage, package: PackageDetails | None = None
) -> CatalogueOut:
    title = category = None
    validity_months = None
    try:
        package = package or fetch_package(entry.package_id)
        title, category, validity_months = (
            package.title,
            package.category,
            package.validity_months,
        )
    except Exception:
        pass

    return CatalogueOut(
        id=entry.id,
        display_code=entry.display_code,
        package_id=entry.package_id,
        price_bdt=entry.price_bdt,
        published=entry.published,
        display_order=entry.display_order,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
        title=title,
        category=category,
        validity_months=validity_months,
    )


def list_catalogue(db: Session, search: str | None = None) -> list[CatalogueOut]:
    query = select(BDLandingPage).order_by(BDLandingPage.display_order.asc())
    entries = [to_catalogue_out(entry) for entry in db.scalars(query)]

    if search:
        needle = search.lower()
        entries = [
            e
            for e in entries
            if needle in e.package_id.lower()
            or needle in e.display_code.lower()
            or (e.title and needle in e.title.lower())
        ]
    return entries


def lookup_package(package_id: str) -> PackageDetails:
    return fetch_package(package_id)


def _validate_price(price_bdt: Decimal) -> None:
    if price_bdt <= 0:
        raise InvalidPriceError("Enter a price greater than 0.")


def _next_display_code(db: Session) -> str:
    # Computed numerically, not via a string ORDER BY — "LP-0099".desc()
    # is a lexicographic string comparison, which is only correct while
    # every code has the same digit width. Once a 5th digit is needed
    # ("LP-10000" after "LP-9999"), "LP-9999" > "LP-10000" as strings
    # (since '9' > '1' at that position), so the old code would compute
    # "LP-10000" again and fail on the unique constraint. Fetching just
    # this one column and taking max() in Python is correct regardless of
    # digit width, and this table is small (a course catalog), so there's
    # no need for a more complex SQL expression.
    codes = db.scalars(select(BDLandingPage.display_code)).all()
    if not codes:
        return "LP-0001"
    last_number = max(int(code.split("-")[1]) for code in codes)
    return f"LP-{last_number + 1:04d}"


def create_catalogue_entry(
    db: Session, package_id: str, price_bdt: Decimal, published: bool
) -> CatalogueOut:
    _validate_price(price_bdt)

    existing = db.scalar(select(BDLandingPage).where(BDLandingPage.package_id == package_id))
    if existing is not None:
        raise DuplicatePackageIdError(
            "A landing page for this package already exists."
        )

    package = fetch_package(package_id)
    if not package.is_eligible:
        raise PackageNotEligibleError(
            "This package exists but isn't published in the package system yet."
        )

    max_order = db.scalar(select(BDLandingPage).order_by(BDLandingPage.display_order.desc()))
    next_order = (max_order.display_order + 1) if max_order else 1

    entry = BDLandingPage(
        display_code=_next_display_code(db),
        package_id=package_id,
        price_bdt=price_bdt,
        published=published,
        display_order=next_order,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return to_catalogue_out(entry, package)


def _get_entry(db: Session, entry_id: uuid.UUID) -> BDLandingPage:
    entry = db.get(BDLandingPage, entry_id)
    if entry is None:
        raise CatalogueEntryNotFoundError(str(entry_id))
    return entry


def update_catalogue_entry(
    db: Session, entry_id: uuid.UUID, price_bdt: Decimal, published: bool
) -> CatalogueOut:
    _validate_price(price_bdt)
    entry = _get_entry(db, entry_id)
    entry.price_bdt = price_bdt
    entry.published = published
    db.commit()
    db.refresh(entry)
    return to_catalogue_out(entry)


def delete_catalogue_entry(db: Session, entry_id: uuid.UUID) -> None:
    entry = _get_entry(db, entry_id)
    db.delete(entry)
    db.commit()


def set_published(db: Session, entry_id: uuid.UUID, published: bool) -> CatalogueOut:
    entry = _get_entry(db, entry_id)
    entry.published = published
    db.commit()
    db.refresh(entry)
    return to_catalogue_out(entry)


def reorder_catalogue(db: Session, ordered_ids: list[uuid.UUID]) -> None:
    for position, entry_id in enumerate(ordered_ids, start=1):
        entry = _get_entry(db, entry_id)
        entry.display_order = position
    db.commit()
