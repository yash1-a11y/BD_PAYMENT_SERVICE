import hashlib
import hmac


def generate_signature(secret_key: str, method: str, path: str, timestamp: str, body: str) -> str:
    """HMAC-SHA256 over METHOD + PATH + TIMESTAMP + BODY, per Transfi's documented
    signing scheme.

    ASSUMPTIONS not pinned down by the spec text — verify against Transfi's real
    docs once available, since a mismatch on any of these silently invalidates
    every signature:
    - `timestamp` is epoch milliseconds as a string (set by the caller).
    - `body` is the exact compact-JSON string that will be sent on the wire
      (the caller must sign and send the identical bytes — this function does
      not serialize anything itself).
    - The digest is returned as lowercase hex (not base64).
    """
    message = f"{method}{path}{timestamp}{body}"
    return hmac.new(
        secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
    ).hexdigest()
