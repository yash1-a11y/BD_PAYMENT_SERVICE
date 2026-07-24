import time
from dataclasses import dataclass

from src.config.settings import get_settings
from src.integrations.transfi import security
from src.integrations.transfi.client import create_payment_invoice
from src.integrations.transfi.exceptions import TransfiRequestError
from src.integrations.transfi.schemas import IndividualDetails, PaymentInvoiceRequest, ProductDetails

PAYMENT_INVOICE_PATH = "/checkout/payment-link/invoice"
API_VERSION = "v1"

# Tried in this order against the response's `data` object; first match
# wins. Not assumed to be any one specific field — Transfi's confirmed
# real response (Phase 3's Postman collection) only ever contains
# `invoiceId`, but this stays a candidate list, not a hardcoded lookup,
# in case a different Transfi endpoint/version exposes a different name
# for what is semantically "the provider's stable payment reference" —
# same defensive multi-candidate pattern already used in
# webhooks/service.py::_extract_order_id_candidates for a different field.
_PAYMENT_REFERENCE_CANDIDATES = ("invoiceId", "paymentId", "transactionId")


@dataclass
class PaymentInitiationResult:
    payment_url: str
    payment_reference: str | None


def _split_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split(maxsplit=1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return parts[0], parts[0]


def initiate_payment(
    *,
    order_reference: str,
    amount: float,
    package_title: str,
    package_description: str,
    package_thumbnail: str | None,
    customer_name: str,
    customer_email: str,
    customer_phone: str,
) -> PaymentInitiationResult:
    settings = get_settings()
    first_name, last_name = _split_name(customer_name)

    payload = PaymentInvoiceRequest(
        paymentLinkId=settings.transfi_payment_link_id,
        amount=f"{amount:.2f}",
        customerOrderId=order_reference,
        productDetails=ProductDetails(
            name=package_title,
            description=package_description,
            imageUrl=package_thumbnail,
        ),
        individual=IndividualDetails(
            firstName=first_name,
            lastName=last_name,
            email=customer_email,
            phone=customer_phone,
        ),
        successRedirectUrl=settings.transfi_success_url,
        failureRedirectUrl=settings.transfi_failure_url,
    )
    body = payload.model_dump_json()

    timestamp = str(int(time.time() * 1000))
    signature = security.generate_signature(
        settings.transfi_secret_key, "POST", PAYMENT_INVOICE_PATH, timestamp, body
    )

    headers = {
        "Content-Type": "application/json",
        "x-api-key": settings.transfi_public_key,
        "x-timestamp": timestamp,
        "x-signature": signature,
        "X-Api-Version": API_VERSION,
    }

    response = create_payment_invoice(
        settings.transfi_base_url, PAYMENT_INVOICE_PATH, headers, body
    )
    data = response.get("data") or {}

    # Confirmed real response shape (Transfi's own Postman example):
    # {"success": true, "data": {"invoiceId": ..., "status": ..., "amount": ...}}
    # No URL field is shown in that example at all. Try common URL key names
    # first in case the real sandbox response includes more than the
    # documented example; otherwise fall back to constructing a checkout
    # URL from invoiceId on the widget domain seen in the redirect URLs
    # (checkout-widget.transfi.com) — this fallback is an ASSUMPTION, not
    # confirmed, and needs verification against a real successful response.
    payment_url = data.get("paymentUrl") or data.get("url") or data.get("checkoutUrl")
    if not payment_url:
        invoice_id = data.get("invoiceId")
        if invoice_id:
            payment_url = f"https://checkout-widget.transfi.com/checkout/{invoice_id}"

    if not payment_url:
        raise TransfiRequestError(
            f"Transfi response did not contain a recognizable payment URL: {response!r}"
        )

    payment_reference = next(
        (data[key] for key in _PAYMENT_REFERENCE_CANDIDATES if data.get(key)), None
    )
    return PaymentInitiationResult(payment_url=payment_url, payment_reference=payment_reference)
