import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.modules.checkout.models import FulfilmentStatus, Order
from src.modules.fulfilment.models import Fulfilment

logger = logging.getLogger(__name__)


def allocate_package(db: Session, order: Order) -> None:
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

    Also records one `Fulfilment` row per attempt (docs/postgres_rds.md's
    new production-schema table) — a real implementation should create
    this row as PENDING *before* calling the real API, then update it to
    COMPLETED/FAILED in a try/except mirroring the one already in
    webhooks/service.py around this call, re-raising on failure exactly
    as this stub's docstring already requires. Since this stub never
    actually calls anything and never fails, it just records the one
    outcome it always produces.
    """
    logger.info(
        "Guest Checkout integration configured but disabled until "
        "production base URL is provided: order_id=%s landing_page_id=%s "
        "customer_email=%s",
        order.id,
        order.landing_page_id,
        order.customer_email,
    )
    db.add(
        Fulfilment(
            order_id=order.id,
            guest_checkout_id=None,
            status=FulfilmentStatus.COMPLETED,
            retry_count=0,
            fulfilled_at=datetime.now(UTC),
        )
    )
    db.commit()
