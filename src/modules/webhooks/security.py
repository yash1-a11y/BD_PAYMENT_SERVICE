import hashlib
import hmac


def verify_signature(raw_body: bytes, received_signature: str, secret: str) -> bool:
    """HMAC-SHA256 over the raw request body, per Transfi's documented webhook
    signing scheme — simpler than the Payment Invoice API's signing scheme
    (no method/path/timestamp concatenation, just the raw body).

    `raw_body` must be the exact bytes as received on the wire — never
    parsed-then-reserialized JSON, which could change byte layout and
    invalidate the signature."""
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received_signature)
