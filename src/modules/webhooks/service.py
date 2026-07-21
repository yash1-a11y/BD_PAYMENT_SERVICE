import json
import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import update
from sqlalchemy.orm import Session

from src.config.settings import get_settings
from src.modules.checkout.models import FulfilmentStatus, Order, OrderStatus
from src.modules.fulfilment.service import allocate_package
from src.modules.webhooks import security
from src.modules.webhooks.exceptions import InvalidWebhookSignatureError
from src.modules.webhooks.models import WebhookLog

logger = logging.getLogger(__name__)

SIGNATURE_HEADER = "x-transfi-hmac-hash"

# No enumerated real values are documented — seeded per the prompt's own
# example, case-insensitive. Extend here as real webhook deliveries reveal
# more values; unrecognized values are logged and safely ignored, never a
# crash.
_STATUS_MAP = {
    "SUCCESS": OrderStatus.PAID,
    "PAID": OrderStatus.PAID,
    "COMPLETED": OrderStatus.PAID,
    "FAILED": OrderStatus.FAILED,
    "FAIL": OrderStatus.FAILED,
    "DECLINED": OrderStatus.FAILED,
    "CANCELLED": OrderStatus.CANCELLED,
    "CANCELED": OrderStatus.CANCELLED,
}

# Substrings checked case-insensitively against `entityType` — real values
# aren't documented ("entityType": "...") so this stays a loose allowlist
# rather than an exact match, per the spec's own "be flexible" instruction.
_ORDER_ENTITY_HINTS = ("order", "payment", "invoice")

# Tried in this order against the parsed payload; the first candidate that
# both exists and matches a real Order.id wins. Values are not required to
# look like a UUID before being tried — an invalid/non-UUID candidate is
# just skipped, not treated as a hard error.
_ORDER_ID_CANDIDATES = (
    ("order", "customerOrderId"),
    ("order", "merchantOrderId"),
    ("order", "orderId"),
    (None, "entityId"),
)


def _safe_str(value: object) -> str | None:
    """Payload fields aren't guaranteed to be strings (or even scalars) —
    coerce defensively so a value never breaks the WebhookLog columns it's
    stored in, whatever shape the real payload turns out to have."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value) if isinstance(value, (dict, list)) else str(value)


def _extract_order_id_candidates(payload: dict) -> list[str]:
    candidates = []
    for container_key, field_key in _ORDER_ID_CANDIDATES:
        container = payload.get(container_key, {}) if container_key else payload
        if not isinstance(container, dict):
            continue
        value = container.get(field_key)
        if value:
            candidates.append(str(value))
    return candidates


def _resolve_order(db: Session, payload: dict) -> Order | None:
    for candidate in _extract_order_id_candidates(payload):
        try:
            order_id = uuid.UUID(candidate)
        except (ValueError, AttributeError, TypeError):
            continue
        order = db.get(Order, order_id)
        if order is not None:
            return order
    return None


def _save_log(
    db: Session,
    *,
    headers: dict,
    raw_body: bytes,
    signature_valid: bool,
    processing_result: str,
    entity_type: str | None = None,
    entity_id: str | None = None,
    status: str | None = None,
    error_message: str | None = None,
) -> WebhookLog:
    log = WebhookLog(
        headers=dict(headers),
        raw_body=raw_body.decode("utf-8", errors="replace"),
        signature_header=headers.get(SIGNATURE_HEADER),
        signature_valid=signature_valid,
        entity_type=entity_type,
        entity_id=entity_id,
        status=status,
        processing_result=processing_result,
        error_message=error_message,
        processed_at=datetime.now(UTC),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def process_transfi_webhook(db: Session, raw_body: bytes, headers: dict) -> WebhookLog:
    settings = get_settings()
    lower_headers = {k.lower(): v for k, v in headers.items()}
    received_signature = lower_headers.get(SIGNATURE_HEADER, "")

    signature_valid = bool(received_signature) and security.verify_signature(
        raw_body, received_signature, settings.transfi_webhook_secret
    )
    if not signature_valid:
        _save_log(
            db,
            headers=lower_headers,
            raw_body=raw_body,
            signature_valid=False,
            processing_result="invalid_signature",
        )
        raise InvalidWebhookSignatureError()

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        return _save_log(
            db,
            headers=lower_headers,
            raw_body=raw_body,
            signature_valid=True,
            processing_result="invalid_json",
            error_message=str(exc),
        )

    logger.info("Webhook received (entity_id=%s)", _safe_str(payload.get("entityId")))

    entity_type = _safe_str(payload.get("entityType"))
    entity_id = _safe_str(payload.get("entityId"))
    webhook_status = _safe_str(payload.get("status"))

    if not isinstance(entity_type, str) or not any(
        hint in entity_type.lower() for hint in _ORDER_ENTITY_HINTS
    ):
        return _save_log(
            db,
            headers=lower_headers,
            raw_body=raw_body,
            signature_valid=True,
            processing_result="ignored_entity_type",
            entity_type=entity_type,
            entity_id=entity_id,
            status=webhook_status,
        )

    order = _resolve_order(db, payload)
    if order is None:
        logger.warning("Transfi webhook: no matching order found (entity_id=%s)", entity_id)
        return _save_log(
            db,
            headers=lower_headers,
            raw_body=raw_body,
            signature_valid=True,
            processing_result="order_not_found",
            entity_type=entity_type,
            entity_id=entity_id,
            status=webhook_status,
        )

    mapped_status = (
        _STATUS_MAP.get(webhook_status.upper()) if isinstance(webhook_status, str) else None
    )
    if mapped_status is None:
        logger.warning("Transfi webhook: unrecognized status %r for order %s", webhook_status, order.id)
        return _save_log(
            db,
            headers=lower_headers,
            raw_body=raw_body,
            signature_valid=True,
            processing_result="unknown_status",
            entity_type=entity_type,
            entity_id=entity_id,
            status=webhook_status,
        )

    # Idempotent, race-safe status transition: a single conditional UPDATE
    # (compare-and-swap on `status != PAID`) replaces the previous
    # read-then-write check, which had a window between reading
    # order.status and committing the change — two concurrent or retried
    # deliveries for the same order could both read "not yet PAID" and
    # both proceed, double-triggering fulfilment below. The UPDATE's WHERE
    # clause is evaluated and applied atomically by the database itself,
    # so only the delivery that actually flips the row (rowcount == 1) can
    # continue past this point; a delivery that loses the race — because
    # another one, concurrently or on an earlier retry, already committed
    # PAID — sees rowcount == 0 and is treated exactly like any other
    # repeat delivery for an already-paid order always was: logged and
    # returned without ever reaching fulfilment. This holds across the 2
    # backend replicas in k8s too, since it's enforced by the database,
    # not by in-process state.
    result = db.execute(
        update(Order)
        .where(Order.id == order.id, Order.status != OrderStatus.PAID)
        .values(status=mapped_status)
    )
    db.commit()

    if result.rowcount == 0:
        return _save_log(
            db,
            headers=lower_headers,
            raw_body=raw_body,
            signature_valid=True,
            processing_result="already_paid",
            entity_type=entity_type,
            entity_id=entity_id,
            status=webhook_status,
        )

    if mapped_status == OrderStatus.PAID:
        logger.info("Payment success for order %s", order.id)
    elif mapped_status == OrderStatus.FAILED:
        logger.info("Payment failure for order %s", order.id)

    error_message = None
    if mapped_status == OrderStatus.PAID:
        try:
            allocate_package(order)
        except Exception as exc:  # noqa: BLE001 — any fulfilment failure must be caught here
            order.fulfilment_status = FulfilmentStatus.FAILED
            error_message = str(exc)
            logger.exception("Guest checkout failed for order %s", order.id)
        else:
            order.fulfilment_status = FulfilmentStatus.COMPLETED
            logger.info("Guest checkout success for order %s", order.id)
        db.commit()

    return _save_log(
        db,
        headers=lower_headers,
        raw_body=raw_body,
        signature_valid=True,
        processing_result="processed",
        entity_type=entity_type,
        entity_id=entity_id,
        status=webhook_status,
        error_message=error_message,
    )
