import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

# Simple in-process fixed-window limiter — no Redis/queue, matching this
# project's existing small-scale, no-external-cache convention. Resets on
# process restart; fine for a single-instance deployment at this scale.
_WINDOW_SECONDS = 60
_MAX_REQUESTS = 5

_hits: dict[str, list[float]] = defaultdict(list)


def rate_limit_checkout(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - _WINDOW_SECONDS

    hits = _hits[client_ip]
    hits[:] = [t for t in hits if t > window_start]

    if len(hits) >= _MAX_REQUESTS:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many checkout attempts — please wait a moment and try again.",
        )
    hits.append(now)
