from sqlalchemy import select

from src.modules.audit.models import AuditAction, AuditLog


def test_regular_admin_forbidden_from_admin_users(client, regular_auth_headers):
    response = client.get("/bd-admin/api/admins", headers=regular_auth_headers)
    assert response.status_code == 403


def test_super_admin_can_list_admins(client, auth_headers, seeded_admin):
    response = client.get("/bd-admin/api/admins", headers=auth_headers)
    assert response.status_code == 200
    emails = [a["email"] for a in response.json()]
    assert "admin@adda247.com" in emails


def test_create_admin_forces_admin_role(client, auth_headers, db_session):
    response = client.post(
        "/bd-admin/api/admins",
        headers=auth_headers,
        json={"email": "new-admin@adda247.com", "password": "pass1234"},
    )
    assert response.status_code == 201
    assert response.json()["role"] == "ADMIN"

    log = db_session.scalar(
        select(AuditLog).where(AuditLog.action == AuditAction.ADMIN_CREATED)
    )
    assert log is not None


def test_create_admin_rejects_duplicate_email(client, auth_headers, seeded_admin):
    response = client.post(
        "/bd-admin/api/admins",
        headers=auth_headers,
        json={"email": "admin@adda247.com", "password": "pass1234"},
    )
    assert response.status_code == 409


def test_update_admin_logs_audit(client, auth_headers, seeded_regular_admin, db_session):
    response = client.put(
        f"/bd-admin/api/admins/{seeded_regular_admin.id}",
        headers=auth_headers,
        json={"email": "renamed@adda247.com"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "renamed@adda247.com"

    log = db_session.scalar(
        select(AuditLog).where(AuditLog.action == AuditAction.ADMIN_UPDATED)
    )
    assert log is not None


def test_disable_admin_logs_audit(client, auth_headers, seeded_regular_admin, db_session):
    response = client.patch(
        f"/bd-admin/api/admins/{seeded_regular_admin.id}/disable", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    log = db_session.scalar(
        select(AuditLog).where(AuditLog.action == AuditAction.ADMIN_DISABLED)
    )
    assert log is not None


def test_super_admin_cannot_disable_self(client, auth_headers, seeded_admin):
    response = client.patch(
        f"/bd-admin/api/admins/{seeded_admin.id}/disable", headers=auth_headers
    )
    assert response.status_code == 400


def test_super_admin_cannot_delete_self(client, auth_headers, seeded_admin):
    response = client.delete(f"/bd-admin/api/admins/{seeded_admin.id}", headers=auth_headers)
    assert response.status_code == 400


def test_reset_password_logs_audit(client, auth_headers, seeded_regular_admin, db_session):
    response = client.post(
        f"/bd-admin/api/admins/{seeded_regular_admin.id}/reset-password",
        headers=auth_headers,
        json={"new_password": "newpass123"},
    )
    assert response.status_code == 200

    log = db_session.scalar(
        select(AuditLog).where(AuditLog.action == AuditAction.PASSWORD_RESET)
    )
    assert log is not None


def test_delete_admin(client, auth_headers, seeded_regular_admin):
    response = client.delete(
        f"/bd-admin/api/admins/{seeded_regular_admin.id}", headers=auth_headers
    )
    assert response.status_code == 204

    response = client.get("/bd-admin/api/admins", headers=auth_headers)
    emails = [a["email"] for a in response.json()]
    assert "staff@adda247.com" not in emails
