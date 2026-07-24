"""fix audit_logs admin FK constraints

Revision ID: 28641e6c7568
Revises: f4a5b6c7d8e9
Create Date: 2026-07-21 17:26:24.921777

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '28641e6c7568'
down_revision: Union[str, Sequence[str], None] = 'f4a5b6c7d8e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # actor_admin_id's original FK (89899fa92660) had no ON DELETE
    # behavior, i.e. Postgres's default NO ACTION — meaning deleting any
    # admin who has ever performed an audited action (login, created/
    # updated/disabled another admin, reset a password) would fail with a
    # foreign-key violation. This was a real, previously-undetected bug:
    # masked in tests because SQLite never enforces foreign keys here
    # (no PRAGMA foreign_keys=ON is set), so test_delete_admin only ever
    # exercised a freshly-seeded admin with zero audit_logs rows against
    # it. Recreated with ON DELETE SET NULL so a deleted admin's
    # historical audit rows survive — audit_logs is a historical record,
    # not something that should block or cascade-delete an admin lifecycle
    # action — they simply lose that specific actor identity.
    op.drop_constraint("audit_logs_actor_admin_id_fkey", "audit_logs", type_="foreignkey")
    op.create_foreign_key(
        "audit_logs_actor_admin_id_fkey",
        "audit_logs",
        "admin_users",
        ["actor_admin_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # target_admin_id never had a FK constraint at all — any UUID could be
    # stored here, even one that doesn't correspond to a real admin. Added
    # now to match its sibling actor_admin_id, with the same ON DELETE
    # SET NULL behavior for the same reason.
    op.create_foreign_key(
        "audit_logs_target_admin_id_fkey",
        "audit_logs",
        "admin_users",
        ["target_admin_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("audit_logs_target_admin_id_fkey", "audit_logs", type_="foreignkey")
    op.drop_constraint("audit_logs_actor_admin_id_fkey", "audit_logs", type_="foreignkey")
    op.create_foreign_key(
        "audit_logs_actor_admin_id_fkey",
        "audit_logs",
        "admin_users",
        ["actor_admin_id"],
        ["id"],
    )
