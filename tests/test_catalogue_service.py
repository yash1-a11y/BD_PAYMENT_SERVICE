from decimal import Decimal

import pytest

from src.integrations.package_system.client import PackageDetails
from src.modules.catalogue import service
from src.modules.catalogue.exceptions import (
    DuplicatePackageIdError,
    InvalidPriceError,
    PackageNotEligibleError,
)
from src.modules.catalogue.models import BDLandingPage


def _fake_package(package_id="3937", published=True):
    return PackageDetails(
        package_id=package_id,
        title="Test Package",
        category="BANKING",
        validity_months=12,
        thumbnail_url="https://example.com/thumb.jpg",
        india_mrp=4999,
        published=published,
    )


def test_create_rejects_ineligible_package(db_session, monkeypatch):
    monkeypatch.setattr(
        service, "fetch_package", lambda package_id: _fake_package(published=False)
    )
    with pytest.raises(PackageNotEligibleError):
        service.create_catalogue_entry(db_session, "3937", Decimal("1499"), False)


def test_create_succeeds_for_eligible_package(db_session, monkeypatch):
    monkeypatch.setattr(service, "fetch_package", lambda package_id: _fake_package())
    entry = service.create_catalogue_entry(db_session, "3937", Decimal("1499"), True)
    assert entry.package_id == "3937"
    assert entry.display_order == 1
    assert entry.display_code == "LP-0001"
    assert entry.title == "Test Package"


def test_create_rejects_duplicate_package_id(db_session, monkeypatch):
    monkeypatch.setattr(service, "fetch_package", lambda package_id: _fake_package())
    service.create_catalogue_entry(db_session, "3937", Decimal("1499"), True)
    with pytest.raises(DuplicatePackageIdError):
        service.create_catalogue_entry(db_session, "3937", Decimal("999"), True)


def test_create_rejects_non_positive_price(db_session, monkeypatch):
    monkeypatch.setattr(service, "fetch_package", lambda package_id: _fake_package())
    with pytest.raises(InvalidPriceError):
        service.create_catalogue_entry(db_session, "3937", Decimal("0"), True)


def test_update_rejects_non_positive_price(db_session, monkeypatch):
    monkeypatch.setattr(service, "fetch_package", lambda package_id: _fake_package())
    entry = service.create_catalogue_entry(db_session, "3937", Decimal("1499"), True)
    with pytest.raises(InvalidPriceError):
        service.update_catalogue_entry(db_session, entry.id, Decimal("-5"), True)


def test_update_cannot_change_package_id(db_session, monkeypatch):
    monkeypatch.setattr(service, "fetch_package", lambda package_id: _fake_package())
    entry = service.create_catalogue_entry(db_session, "3937", Decimal("1499"), True)
    updated = service.update_catalogue_entry(db_session, entry.id, Decimal("1999"), False)
    assert updated.package_id == "3937"


def test_next_display_code_handles_digit_width_boundary(db_session, monkeypatch):
    # "LP-9999".desc() as a STRING sorts AFTER "LP-10000" (since '9' > '1'
    # at that character position) — with only one row this comparison
    # never actually triggers, so both rows below must exist for the old
    # string-ordered implementation to get it wrong: it would pick
    # "LP-9999" as "last" and compute "LP-10000" again, colliding with the
    # row that already has that code.
    db_session.add_all(
        [
            BDLandingPage(
                display_code="LP-9999",
                package_id="boundary-test-1",
                price_bdt=Decimal("100"),
                published=True,
                display_order=1,
            ),
            BDLandingPage(
                display_code="LP-10000",
                package_id="boundary-test-2",
                price_bdt=Decimal("100"),
                published=True,
                display_order=2,
            ),
        ]
    )
    db_session.commit()

    monkeypatch.setattr(service, "fetch_package", lambda package_id: _fake_package(package_id))
    entry = service.create_catalogue_entry(db_session, "next-after-boundary", Decimal("100"), True)

    assert entry.display_code == "LP-10001"


def test_reorder_persists_display_order(db_session, monkeypatch):
    monkeypatch.setattr(
        service,
        "fetch_package",
        lambda package_id: _fake_package(package_id=package_id),
    )
    first = service.create_catalogue_entry(db_session, "1001", Decimal("100"), True)
    second = service.create_catalogue_entry(db_session, "1002", Decimal("200"), True)

    service.reorder_catalogue(db_session, [second.id, first.id])

    entries = service.list_catalogue(db_session)
    assert [e.package_id for e in entries] == ["1002", "1001"]
