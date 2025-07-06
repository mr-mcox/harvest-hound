"""
Database schema definitions using SQLAlchemy Core.

Defines read model tables with proper indexes as per ADR-005.
Uses SQLAlchemy Core for persistence ignorance and database independence.
"""
from typing import Union

from sqlalchemy import (
    MetaData,
    Table,
    Column,
    String,
    Float,
    Integer,
    Boolean,
    Index,
    create_engine,
)
from sqlalchemy.engine import Engine, Connection

# Global metadata instance for all tables
metadata = MetaData()

# Read model tables following ADR-005 flat structure
inventory_item_views = Table(
    "inventory_item_views",
    metadata,
    Column("store_id", String, nullable=False),
    Column("ingredient_id", String, nullable=False),
    Column("ingredient_name", String, nullable=False),
    Column("store_name", String, nullable=False),
    Column("quantity", Float, nullable=False),
    Column("unit", String, nullable=False),
    Column("notes", String, nullable=True),
    Column("added_at", String, nullable=False),
    # Primary key for upsert behavior
    Index("pk_inventory_item_views", "store_id", "ingredient_id", unique=True),
    # Indexes for common query patterns per ADR-005
    Index("idx_inventory_views_ingredient_name", "ingredient_name"),
    Index("idx_inventory_views_store_name", "store_name"),
    Index("idx_inventory_views_ingredient_id", "ingredient_id"),
)

store_views = Table(
    "store_views",
    metadata,
    Column("store_id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("description", String, nullable=False, default=""),
    Column("infinite_supply", Boolean, nullable=False, default=False),
    Column("item_count", Integer, nullable=False, default=0),
    Column("created_at", String, nullable=False),
    # Index for common query patterns
    Index("idx_store_views_name", "name"),
)


def create_tables(engine: Union[Engine, Connection]) -> None:
    """Create all read model tables."""
    metadata.create_all(engine)


def drop_tables(engine: Union[Engine, Connection]) -> None:
    """Drop all read model tables (for testing)."""
    metadata.drop_all(engine)