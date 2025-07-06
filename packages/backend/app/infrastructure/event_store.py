import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..events.domain_events import (
    DomainEvent,
    IngredientCreated,
    InventoryItemAdded,
    StoreCreated,
)
from ..projections.registry import ProjectionRegistry


class EventStore:
    """SQLite-based event store for domain events."""

    def __init__(self, db_path: str = "events.db", projection_registry: Optional[ProjectionRegistry] = None):
        self.db_path = db_path
        self.projection_registry = projection_registry
        self._ensure_table_exists()

    def _ensure_table_exists(self) -> None:
        """Create events table and projection tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            # Events table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stream_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_data TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_stream_id_timestamp
                ON events(stream_id, timestamp)
            """
            )

            # Projection tables
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ingredients (
                    ingredient_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    default_unit TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS stores (
                    store_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    infinite_supply BOOLEAN NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS inventory_items (
                    store_id TEXT NOT NULL,
                    ingredient_id TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    unit TEXT NOT NULL,
                    notes TEXT,
                    added_at TEXT NOT NULL,
                    PRIMARY KEY (store_id, ingredient_id),
                    FOREIGN KEY (store_id) REFERENCES stores(store_id),
                    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id)
                )
            """
            )

            # Current inventory view
            conn.execute(
                """
                CREATE VIEW IF NOT EXISTS current_inventory AS
                SELECT
                    s.store_id,
                    s.name as store_name,
                    ii.ingredient_id,
                    i.name as ingredient_name,
                    ii.quantity,
                    ii.unit,
                    ii.notes,
                    ii.added_at
                FROM inventory_items ii
                JOIN stores s ON ii.store_id = s.store_id
                JOIN ingredients i ON ii.ingredient_id = i.ingredient_id
            """
            )

    def append_event(self, stream_id: str, event: DomainEvent) -> None:
        """Append a domain event to the specified stream."""
        event_type = event.__class__.__name__
        event_data = event.model_dump_json()
        timestamp = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            # Append event to event store
            conn.execute(
                """INSERT INTO events (stream_id, event_type, event_data, timestamp)
                   VALUES (?, ?, ?, ?)""",
                (stream_id, event_type, event_data, timestamp),
            )

            # Keep legacy projection tables for backward compatibility
            self._update_projections(conn, event)

        # Trigger new projection registry (external to transaction for safety)
        if self.projection_registry is not None:
            try:
                self.projection_registry.handle(event)
            except Exception as e:
                # In production, this would use proper logging
                # For now, we don't want projection failures to break event storage
                pass

    def _update_projections(self, conn: sqlite3.Connection, event: DomainEvent) -> None:
        """Update projection tables based on domain events."""
        if isinstance(event, IngredientCreated):
            conn.execute(
                """INSERT OR REPLACE INTO ingredients
                   (ingredient_id, name, default_unit, created_at)
                   VALUES (?, ?, ?, ?)""",
                (
                    str(event.ingredient_id),
                    event.name,
                    event.default_unit,
                    event.created_at.isoformat(),
                ),
            )
        elif isinstance(event, StoreCreated):
            conn.execute(
                """INSERT OR REPLACE INTO stores
                   (store_id, name, description, infinite_supply, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    str(event.store_id),
                    event.name,
                    event.description,
                    event.infinite_supply,
                    event.created_at.isoformat(),
                ),
            )
        elif isinstance(event, InventoryItemAdded):
            conn.execute(
                """INSERT OR REPLACE INTO inventory_items
                   (store_id, ingredient_id, quantity, unit, notes, added_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    str(event.store_id),
                    str(event.ingredient_id),
                    event.quantity,
                    event.unit,
                    event.notes,
                    event.added_at.isoformat(),
                ),
            )

    def load_events(self, stream_id: str) -> List[Dict[str, Any]]:
        """Load all events for a stream in chronological order."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT event_type, event_data, timestamp FROM events
                   WHERE stream_id = ? ORDER BY timestamp""",
                (stream_id,),
            )

            events: List[Dict[str, Any]] = []
            for row in cursor.fetchall():
                event_type, event_data, timestamp = row
                events.append(
                    {
                        "event_type": event_type,
                        "event_data": json.loads(event_data),
                        "timestamp": timestamp,
                    }
                )

            return events

    def get_stores_with_item_count(self) -> List[Dict[str, Any]]:
        """Get list of all stores with their inventory item counts."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT
                    s.store_id,
                    s.name,
                    s.description,
                    s.infinite_supply,
                    s.created_at,
                    COALESCE(item_counts.item_count, 0) as item_count
                FROM stores s
                LEFT JOIN (
                    SELECT store_id, COUNT(*) as item_count
                    FROM inventory_items
                    GROUP BY store_id
                ) item_counts ON s.store_id = item_counts.store_id
                ORDER BY s.created_at"""
            )

            stores: List[Dict[str, Any]] = []
            for row in cursor.fetchall():
                stores.append(
                    {
                        "store_id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "infinite_supply": bool(row[3]),
                        "created_at": row[4],
                        "item_count": row[5],
                    }
                )

            return stores

    def get_store_inventory(self, store_id: str) -> List[Dict[str, Any]]:
        """Get inventory for a specific store with ingredient details."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT
                    ii.ingredient_id,
                    i.name as ingredient_name,
                    ii.quantity,
                    ii.unit,
                    ii.notes,
                    ii.added_at
                FROM inventory_items ii
                JOIN ingredients i ON ii.ingredient_id = i.ingredient_id
                WHERE ii.store_id = ?
                ORDER BY ii.added_at""",
                (store_id,),
            )

            inventory: List[Dict[str, Any]] = []
            for row in cursor.fetchall():
                inventory.append(
                    {
                        "ingredient_id": row[0],
                        "ingredient_name": row[1],
                        "quantity": row[2],
                        "unit": row[3],
                        "notes": row[4],
                        "added_at": row[5],
                    }
                )

            return inventory

    def get_ingredient_by_id(self, ingredient_id: str) -> Dict[str, Any] | None:
        """Get ingredient details by ID from projection table."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT ingredient_id, name, default_unit, created_at
                   FROM ingredients WHERE ingredient_id = ?""",
                (ingredient_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return {
                "ingredient_id": row[0],
                "name": row[1],
                "default_unit": row[2],
                "created_at": row[3],
            }
