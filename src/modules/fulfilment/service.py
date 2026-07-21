import logging

from src.modules.checkout.models import Order

logger = logging.getLogger(__name__)


def allocate_package(order: Order) -> None:
    """Stub — intentionally not implemented. The real "Package Allocation
    API" / "Guest Checkout" API (docs/PHASE_4.md's external dependency)
    has no documented endpoint or payload shape anywhere in this project,
    and building the Guest Checkout integration is owned by the Backend
    Team, not this phase of work. Rather than fabricate a fake
    integration or temporary workaround, this logs the intent clearly so
    the real call is a single, obvious place to fill in once the Backend
    Team's API is documented — the same approach this project took with
    Transfi itself before a real Postman collection existed.

    Raises on failure so the caller (webhooks/service.py) can catch it and
    keep payment/fulfilment as separate concerns — a failure here must
    never affect Order.status. This exception-on-failure contract is the
    one thing a real implementation must preserve; everything else about
    the function body is expected to change once the Backend Team's API
    is documented.
    """
    logger.info(
        "Package allocation requested (stub — no real Fulfilment API "
        "documented yet): order_id=%s landing_page_id=%s customer_email=%s",
        order.id,
        order.landing_page_id,
        order.customer_email,
    )
