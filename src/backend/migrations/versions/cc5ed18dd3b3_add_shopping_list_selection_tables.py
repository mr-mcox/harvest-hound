"""add_shopping_list_selection_tables

Revision ID: cc5ed18dd3b3
Revises: 0f0aaec8a7e5
Create Date: 2025-12-21 09:21:26.942325

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cc5ed18dd3b3"
down_revision: str | Sequence[str] | None = "0f0aaec8a7e5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create ShoppingListSelection table
    op.create_table(
        "shoppinglistselection",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("ingredient_name", sa.String(), nullable=False),
        sa.Column("checked", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["planningsession.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "session_id",
            "ingredient_name",
            name="uq_shoppinglistselection_session_ingredient",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("shoppinglistselection")
