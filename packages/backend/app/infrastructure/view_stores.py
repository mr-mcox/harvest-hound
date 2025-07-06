"""
View stores for read model persistence using SQLite.

These stores provide efficient storage and retrieval of denormalized read models
following the SQLite pattern used in the existing EventStore.
"""
import sqlite3
from typing import List
from uuid import UUID

from ..models.read_models import InventoryItemView, StoreView


class InventoryItemViewStore:
    """
    SQLite-based store for InventoryItemView read models.
    
    Provides denormalized storage optimized for UI queries as per ADR-005.
    """
    
    def __init__(self, db_path: str = "read_models.db"):
        self.db_path = db_path
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self) -> None:
        """Create read model tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            self._ensure_tables_exist_in_connection(conn)
    
    def _ensure_tables_exist_in_connection(self, conn: sqlite3.Connection) -> None:
        """Create read model tables in given connection if they don't exist."""
        # Inventory item views table (denormalized)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory_item_views (
                store_id TEXT NOT NULL,
                ingredient_id TEXT NOT NULL,
                ingredient_name TEXT NOT NULL,
                store_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                notes TEXT,
                added_at TEXT NOT NULL,
                PRIMARY KEY (store_id, ingredient_id)
            )
            """
        )
        
        # Indexes for common query patterns
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_inventory_views_ingredient_name 
            ON inventory_item_views(ingredient_name)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_inventory_views_store_name 
            ON inventory_item_views(store_name)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_inventory_views_ingredient_id 
            ON inventory_item_views(ingredient_id)
            """
        )
    
    def save_inventory_item_view(self, view: InventoryItemView) -> None:
        """Save or update an inventory item view."""
        with sqlite3.connect(self.db_path) as conn:
            # Ensure tables exist in this connection
            self._ensure_tables_exist_in_connection(conn)
            
            conn.execute(
                """
                INSERT OR REPLACE INTO inventory_item_views
                (store_id, ingredient_id, ingredient_name, store_name, 
                 quantity, unit, notes, added_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(view.store_id),
                    str(view.ingredient_id),
                    view.ingredient_name,
                    view.store_name,
                    view.quantity,
                    view.unit,
                    view.notes,
                    view.added_at.isoformat(),
                ),
            )
    
    def get_by_ingredient_id(self, ingredient_id: UUID) -> List[InventoryItemView]:
        """Get all inventory item views for a specific ingredient."""
        with sqlite3.connect(self.db_path) as conn:
            self._ensure_tables_exist_in_connection(conn)
            cursor = conn.execute(
                """
                SELECT store_id, ingredient_id, ingredient_name, store_name,
                       quantity, unit, notes, added_at
                FROM inventory_item_views
                WHERE ingredient_id = ?
                ORDER BY added_at
                """,
                (str(ingredient_id),),
            )
            
            views = []
            for row in cursor.fetchall():
                view = InventoryItemView(
                    store_id=UUID(row[0]),
                    ingredient_id=UUID(row[1]),
                    ingredient_name=row[2],
                    store_name=row[3],
                    quantity=row[4],
                    unit=row[5],
                    notes=row[6],
                    added_at=row[7],  # Will be parsed by Pydantic
                )
                views.append(view)
            
            return views
    
    def get_all_for_store(self, store_id: UUID) -> List[InventoryItemView]:
        """Get all inventory item views for a specific store."""
        with sqlite3.connect(self.db_path) as conn:
            self._ensure_tables_exist_in_connection(conn)
            cursor = conn.execute(
                """
                SELECT store_id, ingredient_id, ingredient_name, store_name,
                       quantity, unit, notes, added_at
                FROM inventory_item_views
                WHERE store_id = ?
                ORDER BY added_at
                """,
                (str(store_id),),
            )
            
            views = []
            for row in cursor.fetchall():
                view = InventoryItemView(
                    store_id=UUID(row[0]),
                    ingredient_id=UUID(row[1]),
                    ingredient_name=row[2],
                    store_name=row[3],
                    quantity=row[4],
                    unit=row[5],
                    notes=row[6],
                    added_at=row[7],  # Will be parsed by Pydantic
                )
                views.append(view)
            
            return views


class StoreViewStore:
    """
    SQLite-based store for StoreView read models.
    
    Provides denormalized storage with computed fields for efficient store queries.
    """
    
    def __init__(self, db_path: str = "read_models.db"):
        self.db_path = db_path
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self) -> None:
        """Create read model tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            self._ensure_tables_exist_in_connection(conn)
    
    def _ensure_tables_exist_in_connection(self, conn: sqlite3.Connection) -> None:
        """Create read model tables in given connection if they don't exist."""
        # Store views table (denormalized with computed fields)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS store_views (
                store_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                infinite_supply BOOLEAN NOT NULL DEFAULT 0,
                item_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        
        # Indexes for common query patterns
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_store_views_name 
            ON store_views(name)
            """
        )
    
    def save_store_view(self, view: StoreView) -> None:
        """Save or update a store view."""
        with sqlite3.connect(self.db_path) as conn:
            self._ensure_tables_exist_in_connection(conn)
            conn.execute(
                """
                INSERT OR REPLACE INTO store_views
                (store_id, name, description, infinite_supply, item_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(view.store_id),
                    view.name,
                    view.description,
                    view.infinite_supply,
                    view.item_count,
                    view.created_at.isoformat(),
                ),
            )
    
    def get_by_store_id(self, store_id: UUID) -> StoreView | None:
        """Get store view by store ID."""
        with sqlite3.connect(self.db_path) as conn:
            self._ensure_tables_exist_in_connection(conn)
            cursor = conn.execute(
                """
                SELECT store_id, name, description, infinite_supply, item_count, created_at
                FROM store_views
                WHERE store_id = ?
                """,
                (str(store_id),),
            )
            
            row = cursor.fetchone()
            if row is None:
                return None
            
            return StoreView(
                store_id=UUID(row[0]),
                name=row[1],
                description=row[2],
                infinite_supply=bool(row[3]),
                item_count=row[4],
                created_at=row[5],  # Will be parsed by Pydantic
            )
    
    def get_all_stores(self) -> List[StoreView]:
        """Get all store views ordered by creation date."""
        with sqlite3.connect(self.db_path) as conn:
            self._ensure_tables_exist_in_connection(conn)
            cursor = conn.execute(
                """
                SELECT store_id, name, description, infinite_supply, item_count, created_at
                FROM store_views
                ORDER BY created_at
                """
            )
            
            views = []
            for row in cursor.fetchall():
                view = StoreView(
                    store_id=UUID(row[0]),
                    name=row[1],
                    description=row[2],
                    infinite_supply=bool(row[3]),
                    item_count=row[4],
                    created_at=row[5],  # Will be parsed by Pydantic
                )
                views.append(view)
            
            return views