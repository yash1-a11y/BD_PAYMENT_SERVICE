"""drop orders.reference_id — order.id is the Transfi reference, no second value

Revision ID: e3f4a5b6c7d8
Revises: d2e3f4a5b6c7
Create Date: 2026-07-20 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3f4a5b6c7d8'
down_revision: Union[str, Sequence[str], None] = 'd2e3f4a5b6c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("orders") as batch_op:
        batch_op.drop_constraint("uq_orders_reference_id", type_="unique")
        batch_op.drop_column("reference_id")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("orders") as batch_op:
        batch_op.add_column(sa.Column("reference_id", sa.String(), nullable=True))
        batch_op.create_unique_constraint("uq_orders_reference_id", ["reference_id"])
