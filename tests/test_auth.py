from src.modules.admin_auth.security import create_access_token


def test_login_success(client, seeded_admin):
    response = client.post(
        "/bd-admin/api/auth/login",
        json={"email": "admin@adda247.com", "password": "secret123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["role"] == "SUPER_ADMIN"


def test_login_wrong_password(client, seeded_admin):
    response = client.post(
        "/bd-admin/api/auth/login",
        json={"email": "admin@adda247.com", "password": "wrong"},
    )
    assert response.status_code == 401


def test_protected_route_requires_auth(client):
    response = client.get("/bd-admin/api/landing-pages")
    assert response.status_code == 401


def test_protected_route_with_valid_token(client, auth_headers):
    response = client.get("/bd-admin/api/landing-pages", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_disabled_admin_cannot_log_in(client, seeded_admin, db_session):
    seeded_admin.is_active = False
    db_session.commit()

    response = client.post(
        "/bd-admin/api/auth/login",
        json={"email": "admin@adda247.com", "password": "secret123"},
    )
    assert response.status_code == 401


def test_disabled_admin_token_rejected(client, seeded_admin, db_session):
    token = create_access_token(seeded_admin.id)
    seeded_admin.is_active = False
    db_session.commit()

    response = client.get(
        "/bd-admin/api/landing-pages", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
