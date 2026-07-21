from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.modules.webhooks import service
from src.modules.webhooks.exceptions import InvalidWebhookSignatureError
from src.modules.webhooks.schemas import WebhookAck

router = APIRouter(prefix="/api/bd/webhooks", tags=["webhooks"])


@router.post("/transfi", response_model=WebhookAck)
async def receive_transfi_webhook(request: Request, db: Session = Depends(get_db)):
    # Raw bytes read before any JSON parsing — these are the exact bytes
    # Transfi signed, and the only bytes that can be verified against the
    # signature. Never re-serialize/parse-then-reserialize before this.
    raw_body = await request.body()
    headers = dict(request.headers)

    try:
        service.process_transfi_webhook(db, raw_body, headers)
    except InvalidWebhookSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature.")

    return WebhookAck()
