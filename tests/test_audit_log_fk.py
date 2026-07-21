"""Regression test for the audit_logs FK fix (migration 28641e6c7568).

Uses its own SQLite engine with foreign-key enforcement explicitly turned
on (SQLite ignores FK constraints by default, unlike Postgres, which is
why the pre-existing actor_admin_id bug this migration also fixes was
never caught by the shared db_session fixture) — deliberately isolated
from tests/conftest.py rather than changing its shared engine, since
enabling FK enforcement project-wide is a separate, larger decision.

The real target behavior was already proven against a live Postgres
instance directly (DELETE succeeds, both columns become NULL); this test
exists so the same guarantee is also covered by the automated suite.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.base import Base
from src.modules.admin_auth.models import AdminRole, AdminUser
from src.modules.admin_auth.security import hash_password
from src.modules.audit.models import AuditAction, AuditLog


def _fk_enforced_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)()


def test_deleting_admin_with_audit_history_sets_columns_null_not_error():
    db = _fk_enforced_session()

    admin = AdminUser(
        email="fk-test@example.com",
        password_hash=hash_password("secret123"),
        role=AdminRole.ADMIN,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    login_log = AuditLog(actor_admin_id=admin.id, action=AuditAction.LOGIN, target_admin_id=None)
    created_log = AuditLog(actor_admin_id=None, action=AuditAction.ADMIN_CREATED, target_admin_id=admin.id)
    db.add_all([login_log, created_log])
    db.commit()

    # Before the fix, this raised sqlite3.IntegrityError (actor_admin_id
    # had no ON DELETE clause) and target_admin_id had no FK at all to
    # even enforce. Both are now ON DELETE SET NULL.
    db.delete(admin)
    db.commit()

    db.refresh(login_log)
    db.refresh(created_log)
    assert login_log.actor_admin_id is None
    assert created_log.target_admin_id is None

    db.close()
