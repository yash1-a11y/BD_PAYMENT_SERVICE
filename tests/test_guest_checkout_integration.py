import uuid
from decimal import Decimal

from src.integrations.guest_checkout.service import build_guest_checkout_payload
from src.modules.checkout.models import Order


def _order(price=Decimal("1499")) -> Order:
    return Order(
        id=uuid.uuid4(),
        landing_page_id=uuid.uuid4(),
        customer_name="Jane Doe",
        customer_email="jane@example.com",
        customer_phone="+8801712345678",
        price_bdt=price,
    )


def test_build_guest_checkout_payload_maps_order_fields():
    order = _order()

    payload = build_guest_checkout_payload(order, package_id="109857")

    assert payload.name == "Jane Doe"
    assert payload.email == "jane@example.com"
    assert payload.mobile == "+8801712345678"
    assert payload.transactionId == str(order.id)
    assert payload.transactionPrice == "1499.00"
    assert len(payload.packageList) == 1

    item = payload.packageList[0]
    assert item.packageId == "109857"
    assert item.price == "1499.00"
    assert item.foreignCurrency == "BDT"
    assert item.foreignPrice == "1499.00"


def test_build_guest_checkout_payload_never_hardcodes_customer_values():
    order_a = _order(price=Decimal("999"))
    order_b = _order(price=Decimal("2500"))

    payload_a = build_guest_checkout_payload(order_a, package_id="pkg-a")
    payload_b = build_guest_checkout_payload(order_b, package_id="pkg-b")

    assert payload_a.transactionId != payload_b.transactionId
    assert payload_a.transactionPrice == "999.00"
    assert payload_b.transactionPrice == "2500.00"
    assert payload_a.packageList[0].packageId == "pkg-a"
    assert payload_b.packageList[0].packageId == "pkg-b"
