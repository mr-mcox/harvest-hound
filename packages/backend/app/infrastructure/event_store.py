import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from ..events.domain_events import (
    DomainEvent,
    IngredientCreated,
    InventoryItemAdded,
    StoreCreated,
)
from ..projections.registry import ProjectionRegistry
from .database import events, create_tables

if TYPE_CHECKING:
    from .event_bus import EventBus


class EventStore:
    """SQLAlchemy-based event store for domain events."""

    def __init__(self, session: Session, projection_registry: Optional[ProjectionRegistry] = None, event_bus: Optional["EventBus"] = None):
        self.session = session
        self.projection_registry = projection_registry
        self.event_bus = event_bus
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

        # Trigger projection registry (external to transaction for safety)
        if self.projection_registry is not None:
            try:
                self.projection_registry.handle(event)
            except Exception as e:
                # In production, this would use proper logging
                # For now, we don't want projection failures to break event storage
                pass
        
        # Publish to event bus if available (async operation)
        if self.event_bus is not None:
            try:
                # Schedule async publish - create task if event loop is running
                loop = asyncio.get_running_loop()
                loop.create_task(self.event_bus.publish(event))
            except RuntimeError:
                # No event loop running, skip async publish for now
                # In production, this would use proper async context
                pass
            except Exception as e:
                # In production, this would use proper logging
                # For now, we don't want event bus failures to break event storage
                pass

    def load_events(self, stream_id: str) -> List[Dict[str, Any]]:
        """Load all events for a stream in chronological order."""
        stmt = select(events.c.event_type, events.c.event_data, events.c.timestamp).where(
            events.c.stream_id == stream_id
        ).order_by(events.c.timestamp)
        
        result = self.session.execute(stmt)
        
        event_list: List[Dict[str, Any]] = []
        for row in result:
            event_list.append({
                "event_type": row.event_type,
                "event_data": json.loads(row.event_data),
                "timestamp": row.timestamp,
            })

        return event_list

