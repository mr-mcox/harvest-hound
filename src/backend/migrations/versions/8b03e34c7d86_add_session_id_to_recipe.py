"""add_session_id_to_recipe

Revision ID: 8b03e34c7d86
Revises: 3bc027834eaa
Create Date: 2025-12-08 14:55:00.862797

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8b03e34c7d86"
down_revision: str | Sequence[str] | None = "3bc027834eaa"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table("recipe", schema=None) as batch_op:
        batch_op.add_column(sa.Column("session_id", sa.Uuid(), nullable=True))
        batch_op.create_foreign_key(
            "fk_recipe_session",
            "planningsession",
            ["session_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # Backfill session_id from criterion -> session relationship
    op.execute("""
        UPDATE recipe
        SET session_id = (
            SELECT session_id
            FROM mealcriterion
            WHERE mealcriterion.id = recipe.criterion_id
        )
        WHERE criterion_id IS NOT NULL
    """)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("recipe", schema=None) as batch_op:
        batch_op.drop_constraint("fk_recipe_session", type_="foreignkey")
        batch_op.drop_column("session_id")
