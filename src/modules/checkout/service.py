import re
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.integrations.package_system.client import fetch_storefront_package
from src.integrations.transfi.exceptions import TransfiRequestError
from src.integrations.transfi.service import initiate_payment as transfi_initiate_payment
from src.modules.catalogue.models import BDLandingPage
from src.modules.checkout.exceptions import OrderNotFoundError, PackageUnavailableError
from src.modules.checkout.models import Order, OrderLifecycleStatus, OrderStatus
from src.modules.checkout.schemas import OrderCreate, OrderOut, OrderStatusOut


def _plain_text(html: str | None, fallback: str) -> str:
    if not html:
        return fallback
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:500] or fallback


def initiate_payment(db: Session, payload: OrderCreate) -> OrderOut:
    entry = db.scalar(
        select(BDLandingPage).where(BDLandingPage.package_id == payload.package_id)
    )
    if entry is None or not entry.published:
        raise PackageUnavailableError(payload.package_id)

    # Fetch the latest package details live — the same rule this project has
    # followed since Phase 1: never rely on stale/cached upstream data.
    storefront = fetch_storefront_package(payload.package_id)
    variant_id = storefront.plan.variant_id if storefront.plan else None
    title = storefront.title or entry.package_id

    # Generated explicitly (rather than left to the column's default) so
    # `reference_id` can be set to the same value in the same statement —
    # a mirror of `id`, never a second independently-generated identity.
    order_id = uuid.uuid4()

    order = Order(
        id=order_id,
        reference_id=str(order_id),
        landing_page_id=entry.id,
        variant_id=variant_id,
        customer_name=payload.name,
        customer_email=payload.email,
        # Stored in full international format; the raw local number (without
        # +880) is what gets sent to Transfi, which carries the country code
        # separately as `phoneCode`.
        customer_phone=f"+880{payload.phone}",
        # Our own BDT catalogue price is always the source of truth for the
        # amount charged — never the Package System's own price fields, and
        # never anything trusted from the client request.
        price_bdt=entry.price_bdt,
        payment_provider="transfi",
        payment_status=OrderStatus.PENDING.value,
        order_status=OrderLifecycleStatus.PENDING,
        # Lightweight historical snapshot — package details otherwise
        # always come live from the Package System API and are never
        # stored permanently; this is the one deliberate exception,
        # scoped to what was actually purchased at this moment. No `slug`
        # field — nothing in the Package System's response has one, so
        # it's left out rather than invented.
        package_snapshot={
            "package_id": entry.package_id,
            "title": title,
            "thumbnail": storefront.thumbnail_url,
            "selling_price_bdt": str(entry.price_bdt),
        },
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    try:
        result = transfi_initiate_payment(
            order_reference=str(order.id),
            amount=float(entry.price_bdt),
            package_title=title,
            package_description=_plain_text(storefront.overview_html, title),
            package_thumbnail=storefront.thumbnail_url,
            customer_name=payload.name,
            customer_email=payload.email,
            customer_phone=payload.phone,
        )
    except TransfiRequestError:
        # The order must not be silently lost if Transfi's call fails — leave
        # a clearly failed, auditable record rather than deleting the row or
        # leaving it ambiguously PENDING forever. Retrying is explicitly out
        # of scope for this phase.
        order.status = OrderStatus.FAILED
        order.payment_status = OrderStatus.FAILED.value
        order.order_status = OrderLifecycleStatus.PAYMENT_FAILED
        db.commit()
        raise

    order.payment_reference = result.payment_reference
    db.commit()

    return OrderOut(
        order_id=order.id,
        package_id=entry.package_id,
        title=title,
        price_bdt=order.price_bdt,
        status=order.status.value,
        payment_url=result.payment_url,
        created_at=order.created_at,
    )


def get_order_status(db: Session, order_id: uuid.UUID) -> OrderStatusOut:
    order = db.get(Order, order_id)
    if order is None:
        raise OrderNotFoundError(str(order_id))

    landing_page = db.get(BDLandingPage, order.landing_page_id)
    title = landing_page.package_id if landing_page else str(order.landing_page_id)
    try:
        if landing_page:
            title = fetch_storefront_package(landing_page.package_id).title or title
    except Exception:
        pass

    return OrderStatusOut(
        order_id=order.id,
        reference_id=order.id,
        payment_status=order.status.value,
        package_allocation_status=order.fulfilment_status.value,
        package_title=title,
        amount_bdt=order.price_bdt,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )
