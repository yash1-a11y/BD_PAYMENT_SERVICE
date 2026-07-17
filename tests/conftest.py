import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.app import app
from src.db.base import Base, get_db
from src.modules.admin_auth.models import AdminRole, AdminUser
from src.modules.admin_auth.security import create_access_token, hash_password


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def seeded_admin(db_session):
    admin = AdminUser(
        email="admin@adda247.com",
        password_hash=hash_password("secret123"),
        role=AdminRole.SUPER_ADMIN,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def seeded_regular_admin(db_session):
    admin = AdminUser(
        email="staff@adda247.com",
        password_hash=hash_password("secret123"),
        role=AdminRole.ADMIN,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def auth_headers(seeded_admin):
    token = create_access_token(seeded_admin.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def regular_auth_headers(seeded_regular_admin):
    token = create_access_token(seeded_regular_admin.id)
    return {"Authorization": f"Bearer {token}"}
