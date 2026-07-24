"""case insensitive unique index on admin_users email

Revision ID: b88b82b2fe7a
Revises: 28641e6c7568
Create Date: 2026-07-21 17:30:39.523118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b88b82b2fe7a'
down_revision: Union[str, Sequence[str], None] = '28641e6c7568'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the old plain (case-sensitive) unique constraint first — if any
    # existing rows are case-variant duplicates (e.g. "Admin@x.com" and
    # "admin@x.com"), normalizing them to the same lowercase value below
    # would otherwise violate it mid-migration.
    #
    # Batch mode — SQLite's Alembic dialect has no support for ALTER of
    # constraints at all (only a copy-and-move strategy, which batch mode
    # provides); on Postgres, batch mode compiles down to the exact same
    # direct ALTER statement, so this is a no-op behavior change there
    # (already applied and verified against the real dev Postgres
    # container).
    with op.batch_alter_table("admin_users") as batch_op:
        batch_op.drop_constraint("uq_admin_users_email", type_="unique")

    # Normalize existing data. Application code (admin_users/service.py,
    # admin_auth/service.py) now also normalizes on every future write and
    # looks up case-insensitively regardless, but keeping stored data
    # consistent is good practice on its own.
    op.execute("UPDATE admin_users SET email = LOWER(email)")

    # The real guarantee: case-insensitive uniqueness enforced by the
    # database itself, matching src/modules/admin_auth/models.py. If any
    # genuine case-variant duplicates existed before this migration, this
    # step fails loudly here rather than silently allowing them going
    # forward — they must be resolved manually before this can apply.
    op.create_index(
        "admin_users_email_lower_idx",
        "admin_users",
        [sa.text("LOWER(email)")],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("admin_users_email_lower_idx", table_name="admin_users")
    with op.batch_alter_table("admin_users") as batch_op:
        batch_op.create_unique_constraint("uq_admin_users_email", ["email"])
