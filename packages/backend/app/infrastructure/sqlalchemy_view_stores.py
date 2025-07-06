"""
SQLAlchemy Core-based view stores for read model persistence.

Implementation follows ADR-005 recommendations for better schema management,
type safety, and database independence using SQLAlchemy Core.
"""
from typing import List
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from ..models.read_models import InventoryItemView, StoreView
from .database import inventory_item_views, store_views, create_tables


class InventoryItemViewStore:
    """
    SQLAlchemy Core-based store for InventoryItemView read models.
    
    Provides denormalized storage optimized for UI queries following ADR-005
    recommendations for persistence ignorance and type safety.
    """
    
    def __init__(self, session: Session):
        self.session = session
        # Ensure tables exist (for testing with in-memory databases)
        if session.bind is not None:
            create_tables(session.bind)
    
    def save_inventory_item_view(self, view: InventoryItemView) -> None:
        """Save or update an inventory item view using upsert."""
        # Use SQLite upsert for clean conflict resolution
        stmt = sqlite_insert(inventory_item_views).values(
            store_id=str(view.store_id),
            ingredient_id=str(view.ingredient_id),
            ingredient_name=view.ingredient_name,
            store_name=view.store_name,
            quantity=view.quantity,
            unit=view.unit,
            notes=view.notes,
            added_at=view.added_at.isoformat(),
        )
        
        # Update all fields on conflict (upsert behavior)
        stmt = stmt.on_conflict_do_update(
            index_elements=["store_id", "ingredient_id"],
            set_=dict(
                ingredient_name=stmt.excluded.ingredient_name,
                store_name=stmt.excluded.store_name,
                quantity=stmt.excluded.quantity,
                unit=stmt.excluded.unit,
                notes=stmt.excluded.notes,
                added_at=stmt.excluded.added_at,
            )
        )
        
        self.session.execute(stmt)
        self.session.commit()
    
    def get_by_ingredient_id(self, ingredient_id: UUID) -> List[InventoryItemView]:
        """Get all inventory item views for a specific ingredient."""
        stmt = select(inventory_item_views).where(
            inventory_item_views.c.ingredient_id == str(ingredient_id)
        ).order_by(inventory_item_views.c.added_at)
        
        result = self.session.execute(stmt)
        
        views = []
        for row in result:
            view = InventoryItemView(
                store_id=UUID(row.store_id),
                ingredient_id=UUID(row.ingredient_id),
                ingredient_name=row.ingredient_name,
                store_name=row.store_name,
                quantity=row.quantity,
                unit=row.unit,
                notes=row.notes,
                added_at=row.added_at,  # Pydantic will parse ISO string
            )
            views.append(view)
        
        return views
    
    def get_all_for_store(self, store_id: UUID) -> List[InventoryItemView]:
        """Get all inventory item views for a specific store."""
        stmt = select(inventory_item_views).where(
            inventory_item_views.c.store_id == str(store_id)
        ).order_by(inventory_item_views.c.added_at)
        
        result = self.session.execute(stmt)
        
        views = []
        for row in result:
            view = InventoryItemView(
                store_id=UUID(row.store_id),
                ingredient_id=UUID(row.ingredient_id),
                ingredient_name=row.ingredient_name,
                store_name=row.store_name,
                quantity=row.quantity,
                unit=row.unit,
                notes=row.notes,
                added_at=row.added_at,
            )
            views.append(view)
        
        return views


class StoreViewStore:
    """
    SQLAlchemy Core-based store for StoreView read models.
    
    Provides denormalized storage with computed fields for efficient store queries
    following ADR-005 patterns for type-safe SQL generation.
    """
    
    def __init__(self, session: Session):
        self.session = session
        # Ensure tables exist (for testing with in-memory databases)
        if session.bind is not None:
            create_tables(session.bind)
    
    def save_store_view(self, view: StoreView) -> None:
        """Save or update a store view using upsert."""
        # Use SQLite upsert for clean conflict resolution
        stmt = sqlite_insert(store_views).values(
            store_id=str(view.store_id),
            name=view.name,
            description=view.description,
            infinite_supply=view.infinite_supply,
            item_count=view.item_count,
            created_at=view.created_at.isoformat(),
        )
        
        # Update all fields on conflict (upsert behavior)
        stmt = stmt.on_conflict_do_update(
            index_elements=["store_id"],
            set_=dict(
                name=stmt.excluded.name,
                description=stmt.excluded.description,
                infinite_supply=stmt.excluded.infinite_supply,
                item_count=stmt.excluded.item_count,
                created_at=stmt.excluded.created_at,
            )
        )
        
        self.session.execute(stmt)
        self.session.commit()
    
    def get_by_store_id(self, store_id: UUID) -> StoreView | None:
        """Get store view by store ID."""
        stmt = select(store_views).where(
            store_views.c.store_id == str(store_id)
        )
        
        result = self.session.execute(stmt)
        row = result.fetchone()
        
        if row is None:
            return None
        
        return StoreView(
            store_id=UUID(row.store_id),
            name=row.name,
            description=row.description,
            infinite_supply=bool(row.infinite_supply),
            item_count=row.item_count,
            created_at=row.created_at,
        )
    
    def get_all_stores(self) -> List[StoreView]:
        """Get all store views ordered by creation date."""
        stmt = select(store_views).order_by(store_views.c.created_at)
        
        result = self.session.execute(stmt)
        
        views = []
        for row in result:
            view = StoreView(
                store_id=UUID(row.store_id),
                name=row.name,
                description=row.description,
                infinite_supply=bool(row.infinite_supply),
                item_count=row.item_count,
                created_at=row.created_at,
            )
            views.append(view)
        
        return views