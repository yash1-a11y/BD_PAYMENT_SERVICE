from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.modules.admin_dashboard.schemas import DashboardStatsOut
from src.modules.checkout.models import FulfilmentStatus, Order, OrderStatus
from src.modules.webhooks.models import WebhookLog


def _count(db: Session, *filters) -> int:
    return db.scalar(select(func.count()).select_from(Order).where(*filters)) or 0


def get_dashboard_stats(db: Session) -> DashboardStatsOut:
    # UTC calendar-day boundary — the same timezone convention already
    # used everywhere else in this app (every model's created_at is
    # datetime.now(UTC)); no new timezone handling introduced here.
    today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)

    total_orders = _count(db)
    paid = _count(db, Order.status == OrderStatus.PAID)
    pending = _count(db, Order.status == OrderStatus.PENDING)
    failed = _count(db, Order.status == OrderStatus.FAILED)
    cancelled = _count(db, Order.status == OrderStatus.CANCELLED)

    guest_checkout_success_count = _count(
        db, Order.fulfilment_status == FulfilmentStatus.COMPLETED
    )
    guest_checkout_failure_count = _count(db, Order.fulfilment_status == FulfilmentStatus.FAILED)

    # Webhook Success/Failure map directly onto the existing
    # WebhookLog.signature_valid boolean — the one field that
    # unambiguously means "a genuinely authenticated Transfi delivery" vs.
    # "rejected as inauthentic." No new categorization invented.
    webhook_success_count = (
        db.scalar(
            select(func.count()).select_from(WebhookLog).where(WebhookLog.signature_valid.is_(True))
        )
        or 0
    )
    webhook_failure_count = (
        db.scalar(
            select(func.count())
            .select_from(WebhookLog)
            .where(WebhookLog.signature_valid.is_(False))
        )
        or 0
    )

    orders_today = _count(db, Order.created_at >= today_start)

    # Revenue (Paid Orders Only) — a pending/failed/cancelled order was
    # never actually paid, so it's excluded entirely, not just re-labeled.
    revenue_today_bdt = (
        db.scalar(
            select(func.coalesce(func.sum(Order.price_bdt), 0)).where(
                Order.status == OrderStatus.PAID, Order.created_at >= today_start
            )
        )
        or Decimal("0")
    )

    return DashboardStatsOut(
        total_orders=total_orders,
        paid=paid,
        pending=pending,
        failed=failed,
        cancelled=cancelled,
        guest_checkout_success_count=guest_checkout_success_count,
        guest_checkout_failure_count=guest_checkout_failure_count,
        webhook_success_count=webhook_success_count,
        webhook_failure_count=webhook_failure_count,
        orders_today=orders_today,
        revenue_today_bdt=Decimal(revenue_today_bdt),
    )
