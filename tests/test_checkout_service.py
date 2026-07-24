import uuid
from decimal import Decimal

import pytest

from src.integrations.package_system.client import Plan, StorefrontPackage
from src.integrations.transfi.exceptions import TransfiRequestError
from src.integrations.transfi.service import PaymentInitiationResult
from src.modules.catalogue.models import BDLandingPage
from src.modules.checkout import service
from src.modules.checkout.exceptions import OrderNotFoundError, PackageUnavailableError
from src.modules.checkout.models import Order, OrderLifecycleStatus, OrderStatus
from src.modules.checkout.schemas import OrderCreate


def _fake_storefront(package_id="3937", variant_id="v1"):
    return StorefrontPackage(
        package_id=package_id,
        title="Test Package",
        thumbnail_url="https://example.com/thumb.jpg",
        demo_url=None,
        language="Bengali",
        live_classes_count=10,
        video_count=0,
        has_video_content=False,
        schedule=None,
        plan=Plan(
            variant_id=variant_id,
            title="12 months",
            validity=12,
            validity_unit="MONTH",
            validity_title="12 months",
        )
        if variant_id
        else None,
        highlights=[],
        exam_badges=[],
        faculties=[],
        overview_html="<p>Overview</p>",
        sections=[],
        faqs=[],
        testimonials=[],
        published=True,
    )


def _seed_landing_page(db_session, package_id="3937", price=Decimal("1499"), published=True):
    entry = BDLandingPage(
        display_code=f"LP-{package_id}",
        package_id=package_id,
        price_bdt=price,
        published=published,
        display_order=1,
    )
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)
    return entry


def _order_payload(package_id="3937"):
    return OrderCreate(
        package_id=package_id,
        name="Jane Doe",
        email="jane@example.com",
        phone="1712345678",
    )


def _patch_transfi(
    monkeypatch, payment_url="https://checkout.transfi.com/pay/abc123", payment_reference="inv_abc123"
):
    monkeypatch.setattr(
        service,
        "transfi_initiate_payment",
        lambda **kwargs: PaymentInitiationResult(
            payment_url=payment_url, payment_reference=payment_reference
        ),
    )


def test_initiate_payment_succeeds_for_published_package(db_session, monkeypatch):
    monkeypatch.setattr(
        service, "fetch_storefront_package", lambda package_id: _fake_storefront(package_id)
    )
    _patch_transfi(monkeypatch)
    _seed_landing_page(db_session, price=Decimal("1499"))

    order = service.initiate_payment(db_session, _order_payload())

    assert isinstance(order.order_id, uuid.UUID)
    assert order.package_id == "3937"
    assert order.price_bdt == Decimal("1499")
    assert order.status == "PENDING"
    assert order.payment_url == "https://checkout.transfi.com/pay/abc123"


def test_initiate_payment_stores_normalized_phone_and_variant(db_session, monkeypatch):
    monkeypatch.setattr(
        service,
        "fetch_storefront_package",
        lambda package_id: _fake_storefront(package_id, variant_id="variant-42"),
    )
    _patch_transfi(monkeypatch)
    _seed_landing_page(db_session)

    order_out = service.initiate_payment(db_session, _order_payload())

    order_row = db_session.get(Order, order_out.order_id)
    assert order_row.customer_phone == "+8801712345678"
    assert order_row.variant_id == "variant-42"


def test_initiate_payment_rejects_unpublished_package(db_session, monkeypatch):
    monkeypatch.setattr(
        service, "fetch_storefront_package", lambda package_id: _fake_storefront(package_id)
    )
    _patch_transfi(monkeypatch)
    _seed_landing_page(db_session, published=False)

    with pytest.raises(PackageUnavailableError):
        service.initiate_payment(db_session, _order_payload())


def test_initiate_payment_rejects_nonexistent_package(db_session, monkeypatch):
    monkeypatch.setattr(
        service, "fetch_storefront_package", lambda package_id: _fake_storefront(package_id)
    )
    _patch_transfi(monkeypatch)

    with pytest.raises(PackageUnavailableError):
        service.initiate_payment(db_session, _order_payload(package_id="does-not-exist"))


def test_initiate_payment_snapshots_price_at_order_time(db_session, monkeypatch):
    monkeypatch.setattr(
        service, "fetch_storefront_package", lambda package_id: _fake_storefront(package_id)
    )
    _patch_transfi(monkeypatch)
    entry = _seed_landing_page(db_session, price=Decimal("1000"))

    order = service.initiate_payment(db_session, _order_payload())
    assert order.price_bdt == Decimal("1000")

    entry.price_bdt = Decimal("2000")
    db_session.commit()

    assert order.price_bdt == Decimal("1000")


def test_initiate_payment_marks_order_failed_on_transfi_error(db_session, monkeypatch):
    monkeypatch.setattr(
        service, "fetch_storefront_package", lambda package_id: _fake_storefront(package_id)
    )

    def _raise(**kwargs):
        raise TransfiRequestError("simulated Transfi outage")

    monkeypatch.setattr(service, "transfi_initiate_payment", _raise)
    _seed_landing_page(db_session)

    with pytest.raises(TransfiRequestError):
        service.initiate_payment(db_session, _order_payload())

    order_row = db_session.query(Order).one()
    assert order_row.status == OrderStatus.FAILED


def test_initiate_payment_populates_production_schema_fields(db_session, monkeypatch):
    monkeypatch.setattr(
        service, "fetch_storefront_package", lambda package_id: _fake_storefront(package_id)
    )
    _patch_transfi(monkeypatch, payment_reference="inv_xyz789")
    _seed_landing_page(db_session, package_id="3937", price=Decimal("1499"))

    order_out = service.initiate_payment(db_session, _order_payload())

    order_row = db_session.get(Order, order_out.order_id)
    assert order_row.reference_id == str(order_out.order_id)
    assert order_row.payment_provider == "transfi"
    assert order_row.payment_reference == "inv_xyz789"
    assert order_row.payment_status == "PENDING"
    assert order_row.order_status == OrderLifecycleStatus.PENDING
    assert order_row.currency == "BDT"
    assert order_row.package_snapshot == {
        "package_id": "3937",
        "title": "Test Package",
        "thumbnail": "https://example.com/thumb.jpg",
        "selling_price_bdt": "1499.00",
    }


def test_initiate_payment_transfi_failure_sets_payment_status_and_order_status(
    db_session, monkeypatch
):
    monkeypatch.setattr(
        service, "fetch_storefront_package", lambda package_id: _fake_storefront(package_id)
    )

    def _raise(**kwargs):
        raise TransfiRequestError("simulated Transfi outage")

    monkeypatch.setattr(service, "transfi_initiate_payment", _raise)
    _seed_landing_page(db_session)

    with pytest.raises(TransfiRequestError):
        service.initiate_payment(db_session, _order_payload())

    order_row = db_session.query(Order).one()
    assert order_row.payment_status == "FAILED"
    assert order_row.order_status == OrderLifecycleStatus.PAYMENT_FAILED


def test_get_order_status_returns_status(db_session, monkeypatch):
    monkeypatch.setattr(
        service, "fetch_storefront_package", lambda package_id: _fake_storefront(package_id)
    )
    _patch_transfi(monkeypatch)
    _seed_landing_page(db_session)
    order = service.initiate_payment(db_session, _order_payload())

    status_out = service.get_order_status(db_session, order.order_id)
    assert status_out.order_id == order.order_id
    assert status_out.reference_id == order.order_id
    assert status_out.payment_status == "PENDING"
    assert status_out.package_allocation_status == "PENDING"
    assert status_out.amount_bdt == Decimal("1499")


def test_get_order_status_rejects_unknown_order(db_session):
    with pytest.raises(OrderNotFoundError):
        service.get_order_status(db_session, uuid.uuid4())
