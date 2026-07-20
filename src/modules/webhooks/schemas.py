from pydantic import BaseModel


class WebhookAck(BaseModel):
    """Deliberately minimal — Transfi only needs a 2xx to stop retrying.
    No strict request-body schema exists for the incoming webhook itself:
    the documented payload may carry additional/unknown fields, so parsing
    is done defensively in service.py via plain dict .get() calls rather
    than a rigid Pydantic model that could reject a slightly different real
    payload shape."""

    received: bool = True
