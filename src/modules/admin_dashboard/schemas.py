from decimal import Decimal

from pydantic import BaseModel


class DashboardStatsOut(BaseModel):
    total_orders: int
    paid: int
    pending: int
    failed: int
    cancelled: int
    guest_checkout_success_count: int
    guest_checkout_failure_count: int
    webhook_success_count: int
    webhook_failure_count: int
    orders_today: int
    revenue_today_bdt: Decimal
