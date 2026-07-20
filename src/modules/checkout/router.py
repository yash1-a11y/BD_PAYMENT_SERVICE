import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.integrations.transfi.exceptions import TransfiRequestError
from src.modules.checkout import service
from src.modules.checkout.exceptions import OrderNotFoundError, PackageUnavailableError
from src.modules.checkout.rate_limit import rate_limit_checkout
from src.modules.checkout.schemas import OrderCreate, OrderOut, OrderStatusOut

router = APIRouter(prefix="/api/bd", tags=["checkout"])


@router.post(
    "/checkout/initiate",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_checkout)],
)
def initiate_checkout(payload: OrderCreate, db: Session = Depends(get_db)):
    try:
        return service.initiate_payment(db, payload)
    except PackageUnavailableError:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="This course isn't available for purchase right now."
        )
    except TransfiRequestError:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail="We couldn't reach the payment provider — please try again in a moment.",
        )


@router.get("/orders/{order_id}", response_model=OrderStatusOut)
def get_order(order_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return service.get_order_status(db, order_id)
    except OrderNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found.")
