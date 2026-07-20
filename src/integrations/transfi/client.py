import httpx

from src.integrations.transfi.exceptions import TransfiRequestError


def create_payment_invoice(base_url: str, path: str, headers: dict, body: str) -> dict:
    """Pure HTTP transport — no business logic. `body` must be the exact string
    that was signed (do not re-serialize it here; that could change byte
    layout and invalidate the signature)."""
    try:
        response = httpx.post(f"{base_url}{path}", headers=headers, content=body, timeout=15)
    except httpx.RequestError as exc:
        raise TransfiRequestError(f"Network error calling Transfi: {exc}") from exc

    if response.status_code >= 400:
        raise TransfiRequestError(
            f"Transfi API returned {response.status_code}: {response.text[:500]}"
        )
    return response.json()
