import httpx

from src.integrations.guest_checkout.exceptions import GuestCheckoutRequestError

# NOT CALLED ANYWHERE YET. This function is complete and ready to use, but
# src/modules/fulfilment/service.py::allocate_package deliberately does not
# import or invoke it — Guest Checkout is being prepared, not enabled, until
# the backend team shares a real (non-staging) base URL. See
# docs/guest_checkout_integration.md.


def call_guest_checkout(base_url: str, path: str, headers: dict, body: str) -> dict:
    """Pure HTTP transport — no business logic, matching the same separation
    already established in src/integrations/transfi/client.py. `body` must be
    the exact string produced by service.py's payload builder."""
    try:
        response = httpx.post(f"{base_url}{path}", headers=headers, content=body, timeout=15)
    except httpx.RequestError as exc:
        raise GuestCheckoutRequestError(f"Network error calling Guest Checkout API: {exc}") from exc

    if response.status_code >= 400:
        raise GuestCheckoutRequestError(
            f"Guest Checkout API returned {response.status_code}: {response.text[:500]}"
        )
    return response.json()
