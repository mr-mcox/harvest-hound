import json
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from ..events.domain_events import (
    DomainEvent,
)
from .database import create_tables, events


class EventStore:
    """SQLAlchemy-based event store for domain events."""

    def __init__(self, session: Session):
        self.session = session
        # Ensure tables exist (for testing with in-memory databases)
        if session.bind is not None:
            create_tables(session.bind)

    def append_event(self, stream_id: str, event: DomainEvent) -> None:
        """Append a domain event to the specified stream."""
        event_type = event.__class__.__name__
        event_data = event.model_dump_json()
        timestamp = datetime.now().isoformat()

        # Insert event into event store
        stmt = insert(events).values(
            stream_id=stream_id,
            event_type=event_type,
            event_data=event_data,
            timestamp=timestamp,
        )
        self.session.execute(stmt)
        self.session.commit()

    def load_events(self, stream_id: str) -> List[Dict[str, Any]]:
        """Load all events for a stream in chronological order."""
        stmt = (
            select(events.c.event_type, events.c.event_data, events.c.timestamp)
            .where(events.c.stream_id == stream_id)
            .order_by(events.c.timestamp)
        )

        result = self.session.execute(stmt)

        event_list: List[Dict[str, Any]] = []
        for row in result:
            event_list.append(
                {
                    "event_type": row.event_type,
                    "event_data": json.loads(row.event_data),
                    "timestamp": row.timestamp,
                }
            )

        return event_list
