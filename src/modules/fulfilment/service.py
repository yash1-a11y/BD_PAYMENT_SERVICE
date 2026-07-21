import logging

from src.modules.checkout.models import Order

logger = logging.getLogger(__name__)


def allocate_package(order: Order) -> None:
    """Stub — intentionally not implemented. Building the Guest Checkout
    integration is owned by the Backend Team, not this phase of work.
    The integration itself is now prepared (URL construction, headers,
    authentication, payload generation — see
    src/integrations/guest_checkout/ and
    docs/guest_checkout_integration.md) but deliberately not wired in
    here: the shared staging endpoint is expected to change once this
    service is deployed, so this function still does not call it. Rather
    than fabricate a fake integration or a temporary workaround, this
    logs the intent clearly so flipping it on is a single, obvious
    change once the backend team shares the real production base URL —
    the same approach this project took with Transfi itself before a
    real Postman collection existed.

    Raises on failure so the caller (webhooks/service.py) can catch it and
    keep payment/fulfilment as separate concerns — a failure here must
    never affect Order.status. This exception-on-failure contract is the
    one thing a real implementation must preserve; everything else about
    the function body is expected to change once this is enabled.
    """
    logger.info(
        "Guest Checkout integration configured but disabled until "
        "production base URL is provided: order_id=%s landing_page_id=%s "
        "customer_email=%s",
        order.id,
        order.landing_page_id,
        order.customer_email,
    )
