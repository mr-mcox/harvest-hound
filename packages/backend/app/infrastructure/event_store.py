import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List

from ..events.domain_events import (
    DomainEvent,
    IngredientCreated,
    InventoryItemAdded,
    StoreCreated,
)


class EventStore:
    """SQLite-based event store for domain events."""

    def __init__(self, db_path: str = "events.db"):
        self.db_path = db_path
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

            # Update projection tables
            self._update_projections(conn, event)

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
