from datetime import UTC, datetime, timedelta
from decimal import Decimal

from src.modules.admin_dashboard.service import get_dashboard_stats
from src.modules.catalogue.models import BDLandingPage
from src.modules.checkout.models import FulfilmentStatus, Order, OrderStatus
from src.modules.webhooks.models import WebhookLog


def _seed_landing_page(db_session, package_id="3937"):
    entry = BDLandingPage(
        display_code=f"LP-{package_id}",
        package_id=package_id,
        price_bdt=Decimal("1499"),
        published=True,
        display_order=1,
    )
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)
    return entry


def _seed_order(
    db_session,
    landing_page_id,
    *,
    status,
    fulfilment_status=FulfilmentStatus.PENDING,
    price_bdt=Decimal("1499"),
    created_at=None,
):
    order = Order(
        landing_page_id=landing_page_id,
        customer_name="Jane Doe",
        customer_email="jane@example.com",
        customer_phone="+8801712345678",
        price_bdt=price_bdt,
        status=status,
        fulfilment_status=fulfilment_status,
    )
    if created_at is not None:
        order.created_at = created_at
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


def _seed_webhook_log(db_session, *, signature_valid):
    log = WebhookLog(
        headers={},
        raw_body="{}",
        signature_valid=signature_valid,
        processing_result="processed" if signature_valid else "invalid_signature",
    )
    db_session.add(log)
    db_session.commit()
    return log


def test_get_dashboard_stats_counts_every_metric(db_session):
    landing_page = _seed_landing_page(db_session)

    now = datetime.now(UTC).replace(tzinfo=None)
    yesterday = now - timedelta(days=1)

    _seed_order(
        db_session,
        landing_page.id,
        status=OrderStatus.PAID,
        fulfilment_status=FulfilmentStatus.COMPLETED,
        price_bdt=Decimal("1499"),
        created_at=now,
    )
    _seed_order(
        db_session,
        landing_page.id,
        status=OrderStatus.PAID,
        fulfilment_status=FulfilmentStatus.FAILED,
        price_bdt=Decimal("2000"),
        created_at=now,
    )
    _seed_order(db_session, landing_page.id, status=OrderStatus.PENDING, created_at=now)
    _seed_order(db_session, landing_page.id, status=OrderStatus.FAILED, created_at=yesterday)
    _seed_order(db_session, landing_page.id, status=OrderStatus.CANCELLED, created_at=yesterday)

    # A PAID order from yesterday must not count toward today's revenue or
    # today's order count, even though it is PAID.
    _seed_order(
        db_session,
        landing_page.id,
        status=OrderStatus.PAID,
        fulfilment_status=FulfilmentStatus.COMPLETED,
        price_bdt=Decimal("9999"),
        created_at=yesterday,
    )

    _seed_webhook_log(db_session, signature_valid=True)
    _seed_webhook_log(db_session, signature_valid=True)
    _seed_webhook_log(db_session, signature_valid=False)

    stats = get_dashboard_stats(db_session)

    assert stats.total_orders == 6
    assert stats.paid == 3
    assert stats.pending == 1
    assert stats.failed == 1
    assert stats.cancelled == 1
    assert stats.guest_checkout_success_count == 2
    assert stats.guest_checkout_failure_count == 1
    assert stats.webhook_success_count == 2
    assert stats.webhook_failure_count == 1
    # Only the two PAID orders created "today" (now), not the PAID order
    # backdated to yesterday.
    assert stats.orders_today == 3
    assert stats.revenue_today_bdt == Decimal("3499")


def test_get_dashboard_stats_returns_zeroes_when_empty(db_session):
    stats = get_dashboard_stats(db_session)

    assert stats.total_orders == 0
    assert stats.paid == 0
    assert stats.webhook_success_count == 0
    assert stats.webhook_failure_count == 0
    assert stats.orders_today == 0
    assert stats.revenue_today_bdt == Decimal("0")


def test_dashboard_stats_endpoint_rejects_missing_token(client):
    response = client.get("/bd-admin/api/dashboard/stats")
    assert response.status_code == 401


def test_dashboard_stats_endpoint_forbidden_for_regular_admin(client, regular_auth_headers):
    response = client.get("/bd-admin/api/dashboard/stats", headers=regular_auth_headers)
    assert response.status_code == 403


def test_dashboard_stats_endpoint_ok_for_super_admin(client, auth_headers):
    response = client.get("/bd-admin/api/dashboard/stats", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total_orders"] == 0
    assert body["revenue_today_bdt"] == "0"
