import hashlib
import hmac
import json
import uuid
from decimal import Decimal

import pytest

from src.config.settings import get_settings
from src.modules.catalogue.models import BDLandingPage
from src.modules.checkout.models import FulfilmentStatus, Order, OrderStatus
from src.modules.webhooks import service
from src.modules.webhooks.exceptions import InvalidWebhookSignatureError


def _sign(body: bytes) -> str:
    secret = get_settings().transfi_webhook_secret
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def _headers(body: bytes) -> dict:
    return {"Content-Type": "application/json", "X-Transfi-Hmac-Hash": _sign(body)}


def _seed_order(db_session, status=OrderStatus.PENDING, price=Decimal("1497")) -> Order:
    entry = BDLandingPage(
        display_code="LP-webhook-test",
        package_id="webhook-test-pkg",
        price_bdt=price,
        published=True,
        display_order=1,
    )
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)

    order = Order(
        landing_page_id=entry.id,
        customer_name="Jane Doe",
        customer_email="jane@example.com",
        customer_phone="+8801712345678",
        price_bdt=price,
        status=status,
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


def _payload(order_id: uuid.UUID, status: str, entity_type: str = "order") -> bytes:
    return json.dumps(
        {
            "entityType": entity_type,
            "entityId": "txn_123",
            "status": status,
            "user": {},
            "order": {"customerOrderId": str(order_id)},
        }
    ).encode("utf-8")


def test_valid_signature_accepted(db_session):
    order = _seed_order(db_session)
    body = _payload(order.id, "SUCCESS")
    log = service.process_transfi_webhook(db_session, body, _headers(body))
    assert log.signature_valid is True
    assert log.processing_result == "processed"


def test_invalid_signature_rejected(db_session):
    order = _seed_order(db_session)
    body = _payload(order.id, "SUCCESS")
    bad_headers = {"Content-Type": "application/json", "X-Transfi-Hmac-Hash": "0" * 64}
    with pytest.raises(InvalidWebhookSignatureError):
        service.process_transfi_webhook(db_session, body, bad_headers)

    db_session.refresh(order)
    assert order.status == OrderStatus.PENDING


def test_successful_payment_updates_order_and_calls_fulfilment(db_session, monkeypatch):
    called = []
    monkeypatch.setattr(
        "src.modules.webhooks.service.allocate_package", lambda o: called.append(o.id)
    )
    order = _seed_order(db_session)
    body = _payload(order.id, "SUCCESS")

    log = service.process_transfi_webhook(db_session, body, _headers(body))

    db_session.refresh(order)
    assert order.status == OrderStatus.PAID
    assert order.fulfilment_status == FulfilmentStatus.COMPLETED
    assert called == [order.id]
    assert log.processing_result == "processed"


def test_failed_payment_updates_order_without_fulfilment(db_session, monkeypatch):
    called = []
    monkeypatch.setattr(
        "src.modules.webhooks.service.allocate_package", lambda o: called.append(o.id)
    )
    order = _seed_order(db_session)
    body = _payload(order.id, "FAILED")

    service.process_transfi_webhook(db_session, body, _headers(body))

    db_session.refresh(order)
    assert order.status == OrderStatus.FAILED
    assert called == []


def test_duplicate_webhook_for_paid_order_is_idempotent(db_session, monkeypatch):
    called = []
    monkeypatch.setattr(
        "src.modules.webhooks.service.allocate_package", lambda o: called.append(o.id)
    )
    order = _seed_order(db_session, status=OrderStatus.PAID)
    body = _payload(order.id, "SUCCESS")

    log = service.process_transfi_webhook(db_session, body, _headers(body))

    assert log.processing_result == "already_paid"
    assert called == []


def test_unknown_order_id_logged_not_crashed(db_session):
    body = _payload(uuid.uuid4(), "SUCCESS")
    log = service.process_transfi_webhook(db_session, body, _headers(body))
    assert log.processing_result == "order_not_found"


def test_unknown_entity_type_ignored(db_session):
    order = _seed_order(db_session)
    body = _payload(order.id, "SUCCESS", entity_type="user_profile_update")
    log = service.process_transfi_webhook(db_session, body, _headers(body))
    assert log.processing_result == "ignored_entity_type"

    db_session.refresh(order)
    assert order.status == OrderStatus.PENDING


def test_unknown_status_logged_no_state_change(db_session):
    order = _seed_order(db_session)
    body = _payload(order.id, "SOME_NEW_STATUS_WE_DONT_KNOW")
    log = service.process_transfi_webhook(db_session, body, _headers(body))
    assert log.processing_result == "unknown_status"

    db_session.refresh(order)
    assert order.status == OrderStatus.PENDING


def test_extra_payload_fields_do_not_break_parsing(db_session):
    order = _seed_order(db_session)
    payload = {
        "entityType": "order",
        "entityId": "txn_999",
        "status": "SUCCESS",
        "user": {"unexpected": {"nested": "stuff"}},
        "order": {"customerOrderId": str(order.id), "somethingElse": [1, 2, 3]},
        "totallyUnexpectedTopLevelField": True,
    }
    body = json.dumps(payload).encode("utf-8")
    log = service.process_transfi_webhook(db_session, body, _headers(body))
    assert log.processing_result == "processed"


def test_malformed_payload_does_not_crash(db_session):
    body = b"{not valid json!!"
    log = service.process_transfi_webhook(db_session, body, _headers(body))
    assert log.processing_result == "invalid_json"


def test_fulfilment_failure_does_not_roll_back_payment_status(db_session, monkeypatch):
    def _raise(order):
        raise RuntimeError("simulated fulfilment outage")

    monkeypatch.setattr("src.modules.webhooks.service.allocate_package", _raise)
    order = _seed_order(db_session)
    body = _payload(order.id, "SUCCESS")

    log = service.process_transfi_webhook(db_session, body, _headers(body))

    db_session.refresh(order)
    assert order.status == OrderStatus.PAID
    assert order.fulfilment_status == FulfilmentStatus.FAILED
    assert log.error_message is not None
    assert log.processing_result == "processed"


def test_order_resolution_falls_back_to_top_level_entity_id(db_session):
    order = _seed_order(db_session)
    payload = {
        "entityType": "order",
        "entityId": str(order.id),
        "status": "SUCCESS",
        "user": {},
        "order": {},
    }
    body = json.dumps(payload).encode("utf-8")
    log = service.process_transfi_webhook(db_session, body, _headers(body))
    assert log.processing_result == "processed"

    db_session.refresh(order)
    assert order.status == OrderStatus.PAID
