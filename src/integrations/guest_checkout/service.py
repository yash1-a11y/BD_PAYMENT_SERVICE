from src.config.settings import get_settings
from src.integrations.guest_checkout.schemas import GuestCheckoutPackageItem, GuestCheckoutRequest
from src.modules.checkout.models import Order

# NOT CALLED ANYWHERE YET. Everything in this file is complete and ready —
# URL construction, headers, authentication, payload generation — but
# src/modules/fulfilment/service.py::allocate_package deliberately does not
# import or invoke any of it. Guest Checkout is being prepared, not enabled,
# until the backend team shares a real (non-staging) base URL. See
# docs/guest_checkout_integration.md for the full picture.


def build_guest_checkout_payload(order: Order, package_id: str) -> GuestCheckoutRequest:
    """Maps an internal Order into the Guest Checkout API's expected request
    shape. Every customer/transaction field comes directly from the Order
    model — `package_id` is passed in explicitly because it lives on
    BDLandingPage, not on Order itself (Order only stores landing_page_id,
    a foreign key); resolving it here would mean this integration querying
    the database on its own, which keeps it from staying isolated from the
    checkout/webhook flow.

    order.id is reused as transactionId — the same "don't generate a second
    reference value" convention already established for Order.id acting as
    the Transfi reference too (see src/modules/checkout/schemas.py's
    OrderStatusOut.reference_id).

    This project currently sells exactly one package per order, so
    transactionPrice and the single packageList item's price/foreignPrice
    are all order.price_bdt — flagged here, not assumed silently, since a
    future multi-package order would need this revisited.

    foreignCurrency stays the schema's own "BDT" default since this app
    only ever transacts in BDT; there is no separate INR/foreign-currency
    conversion tracked anywhere in this codebase.
    """
    price = f"{order.price_bdt:.2f}"

    return GuestCheckoutRequest(
        name=order.customer_name,
        email=order.customer_email,
        mobile=order.customer_phone,
        transactionPrice=price,
        transactionId=str(order.id),
        packageList=[
            GuestCheckoutPackageItem(
                packageId=package_id,
                price=price,
                foreignPrice=price,
            )
        ],
    )


def build_url() -> str:
    """GUEST_CHECKOUT_BASE_URL and GUEST_CHECKOUT_ENDPOINT are deliberately
    separate settings (not one hardcoded combined URL) — the backend team
    said only the base URL changes between staging and production, but the
    endpoint path should stay independently configurable rather than
    hardcoded anywhere in this integration."""
    settings = get_settings()
    return f"{settings.guest_checkout_base_url}{settings.guest_checkout_endpoint}"


def build_headers() -> dict:
    """Headers for the Guest Checkout API — each one added independently,
    only if its underlying setting is actually populated. The real
    authentication scheme (whether JWT and Basic Auth are alternatives or
    used together, and the exact header names) has not been confirmed by
    the backend team yet — the header names below are placeholders,
    following this project's established precedent of flagging unconfirmed
    assumptions explicitly rather than guessing silently (see
    src/integrations/transfi/service.py's own payment-URL fallback
    comment for the same pattern)."""
    settings = get_settings()
    headers = {"Content-Type": "application/json"}

    if settings.guest_checkout_cp_origin:
        # Placeholder header name — not yet confirmed against the real API.
        headers["CP-Origin"] = settings.guest_checkout_cp_origin
    if settings.guest_checkout_jwt_token:
        headers["Authorization"] = f"Bearer {settings.guest_checkout_jwt_token}"
    if settings.guest_checkout_basic_auth:
        # Placeholder header name — GUEST_CHECKOUT_BASIC_AUTH's expected
        # format (raw credentials vs. already base64-encoded "user:pass")
        # is also unconfirmed; adjust once the backend team documents it.
        headers["X-Basic-Auth"] = settings.guest_checkout_basic_auth

    return headers
