"""ingredient identity constraints

Revision ID: 0f0aaec8a7e5
Revises: 9db1bb82b857
Create Date: 2025-12-21 07:20:42.349727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f0aaec8a7e5'
down_revision: Union[str, Sequence[str], None] = '9db1bb82b857'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Step 1: Convert soft-deleted items to quantity=0
    op.execute(
        "UPDATE inventoryitem SET quantity = 0 WHERE deleted_at IS NOT NULL"
    )

    # Step 2: Drop deleted_at column (removing soft-delete model)
    with op.batch_alter_table('inventoryitem', schema=None) as batch_op:
        batch_op.drop_column('deleted_at')

    # Step 3: Add UNIQUE constraint on (ingredient_name, unit)
    with op.batch_alter_table('inventoryitem', schema=None) as batch_op:
        batch_op.create_unique_constraint(
            'uq_inventoryitem_ingredient_name_unit',
            ['ingredient_name', 'unit']
        )


def downgrade() -> None:
    """Downgrade schema."""
    # Step 1: Drop UNIQUE constraint
    with op.batch_alter_table('inventoryitem', schema=None) as batch_op:
        batch_op.drop_constraint(
            'uq_inventoryitem_ingredient_name_unit',
            type_='unique'
        )

    # Step 2: Add back deleted_at column
    with op.batch_alter_table('inventoryitem', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('deleted_at', sa.DateTime(), nullable=True)
        )

    # Step 3: Restore soft-delete state (set deleted_at for zero-quantity items)
    op.execute(
        "UPDATE inventoryitem SET deleted_at = CURRENT_TIMESTAMP WHERE quantity = 0"
    )
