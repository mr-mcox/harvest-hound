import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List

from ..events.domain_events import DomainEvent


class EventStore:
    """SQLite-based event store for domain events."""

    def __init__(self, db_path: str = "events.db"):
        self.db_path = db_path
        self._ensure_table_exists()

    def _ensure_table_exists(self) -> None:
        """Create events table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
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

    def append_event(self, stream_id: str, event: DomainEvent) -> None:
        """Append a domain event to the specified stream."""
        event_type = event.__class__.__name__
        event_data = event.model_dump_json()
        timestamp = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO events (stream_id, event_type, event_data, timestamp)
                   VALUES (?, ?, ?, ?)""",
                (stream_id, event_type, event_data, timestamp),
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
