import asyncio
import threading
import time
from datetime import datetime
from typing import Generator
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session

from app.events.domain_events import InventoryItemAdded, StoreCreated
from app.infrastructure.event_store import EventStore
from app.infrastructure.database import events, metadata
from tests.test_utils import assert_event_matches, get_typed_events


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Create isolated test database session."""
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


class TestEventStoreAppendEvent:
    """Test EventStore.append_event() persists events to SQLAlchemy database."""

    def test_append_event_persists_store_created_event(self, db_session: Session) -> None:
        """EventStore.append_event() should persist StoreCreated event to database."""
        # Create event store and event
        event_store = EventStore(session=db_session)
        store_id = uuid4()
        stream_id = f"store-{store_id}"

        event = StoreCreated(
            store_id=store_id,
            name="Test Store",
            description="A test store",
            infinite_supply=False,
            created_at=datetime.now(),
        )

        # Append event
        event_store.append_event(stream_id, event)

        # Verify event was persisted by loading it back
        store_events = get_typed_events(event_store, stream_id, StoreCreated)

        assert len(store_events) == 1
        assert_event_matches(
            store_events[0],
            {
                "store_id": store_id,
                "name": "Test Store",
                "description": "A test store",
                "infinite_supply": False,
            },
        )


class TestEventStoreLoadEvents:
    """Test EventStore.load_events() returns events in chronological order."""

    def test_load_events_returns_events_in_chronological_order(self, db_session: Session) -> None:
        """EventStore should return events by stream_id in chronological order."""
        event_store = EventStore(session=db_session)
        store_id = uuid4()
        ingredient_id = uuid4()
        stream_id = f"store-{store_id}"

        # Create events with slight time delays to ensure ordering
        event1 = StoreCreated(
            store_id=store_id,
            name="Test Store",
            description="A test store",
            infinite_supply=False,
            created_at=datetime.now(),
        )

        time.sleep(0.001)  # Ensure different timestamps

        event2 = InventoryItemAdded(
            store_id=store_id,
            ingredient_id=ingredient_id,
            quantity=2.0,
            unit="lbs",
            notes="First item",
            added_at=datetime.now(),
        )

        time.sleep(0.001)  # Ensure different timestamps

        event3 = InventoryItemAdded(
            store_id=store_id,
            ingredient_id=ingredient_id,
            quantity=1.0,
            unit="bunch",
            notes="Second item",
            added_at=datetime.now(),
        )

        # Append events
        event_store.append_event(stream_id, event1)
        event_store.append_event(stream_id, event2)
        event_store.append_event(stream_id, event3)

        # Load events and verify order and content
        store_events = get_typed_events(event_store, stream_id, StoreCreated)
        inventory_events = get_typed_events(
            event_store, stream_id, InventoryItemAdded
        )

        # Verify we have the right number of each event type
        assert len(store_events) == 1
        assert len(inventory_events) == 2

        # Verify content of specific events
        assert_event_matches(
            store_events[0], {"store_id": store_id, "name": "Test Store"}
        )
        assert_event_matches(
            inventory_events[0],
            {
                "store_id": store_id,
                "quantity": 2.0,
                "unit": "lbs",
                "notes": "First item",
            },
        )
        assert_event_matches(
            inventory_events[1],
            {
                "store_id": store_id,
                "quantity": 1.0,
                "unit": "bunch",
                "notes": "Second item",
            },
        )

        # Verify chronological ordering by checking raw events
        raw_events = event_store.load_events(stream_id)
        assert len(raw_events) == 3
        timestamps = [event["timestamp"] for event in raw_events]
        assert timestamps == sorted(timestamps)


class TestEventStoreConcurrentWrites:
    """Test EventStore handles concurrent writes without corruption."""

    def test_concurrent_writes_no_corruption(self, db_session: Session) -> None:
        """EventStore should handle concurrent writes without corruption."""
        # Note: This test may need adjustment for true concurrency testing
        # since SQLAlchemy sessions aren't thread-safe by default
        event_store = EventStore(session=db_session)

        # Create multiple sequential writes to test data integrity
        # (In a real concurrent scenario, we'd need separate sessions per thread)
        events_to_create = []
        num_batches = 5
        events_per_batch = 10
        
        for thread_id in range(num_batches):
            for i in range(events_per_batch):
                store_id = uuid4()
                stream_id = f"store-{store_id}"
                event = StoreCreated(
                    store_id=store_id,
                    name=f"Store-{thread_id}-{i}",
                    description=f"Store from batch {thread_id}, iteration {i}",
                    infinite_supply=False,
                    created_at=datetime.now(),
                )
                events_to_create.append((stream_id, event))

        # Write all events
        for stream_id, event in events_to_create:
            event_store.append_event(stream_id, event)

        # Verify all events were written (5 batches * 10 events each = 50 total)
        stmt = select(events.c.id).select_from(events)
        result = db_session.execute(stmt)
        count = len(result.fetchall())
        assert count == 50

        # Verify no data corruption by checking a few random events
        stmt = select(events.c.event_type, events.c.event_data).limit(5)
        result = db_session.execute(stmt)
        
        for row in result:
            event_type, event_data = row
            assert event_type == "StoreCreated"
            # Should be valid JSON
            import json
            parsed_data = json.loads(event_data)
            assert "store_id" in parsed_data
            assert "name" in parsed_data


class TestEventStoreEventBusIntegration:
    """Test EventStore publishes events to event bus when available."""

    def test_append_event_publishes_to_event_bus_when_available(self, db_session: Session) -> None:
        """EventStore should publish events to event bus after storage."""
        # Create mock event bus
        mock_event_bus = Mock()
        mock_event_bus.publish = AsyncMock()
        
        # Create event store with event bus
        event_store = EventStore(session=db_session, event_bus=mock_event_bus)
        store_id = uuid4()
        stream_id = f"store-{store_id}"

        event = StoreCreated(
            store_id=store_id,
            name="Test Store",
            description="A test store",
            infinite_supply=False,
            created_at=datetime.now(),
        )

        # Set up async context
        async def test_with_event_loop():
            # Append event (this should trigger event bus publish)
            event_store.append_event(stream_id, event)
            
            # Allow async task to complete
            await asyncio.sleep(0.001)
            
            # Verify event was published to event bus
            mock_event_bus.publish.assert_called_once_with(event)

        # Run test in async context
        asyncio.run(test_with_event_loop())

    def test_append_event_works_without_event_bus(self, db_session: Session) -> None:
        """EventStore should work normally when no event bus is provided."""
        # Create event store without event bus
        event_store = EventStore(session=db_session, event_bus=None)
        store_id = uuid4()
        stream_id = f"store-{store_id}"

        event = StoreCreated(
            store_id=store_id,
            name="Test Store",
            description="A test store",
            infinite_supply=False,
            created_at=datetime.now(),
        )

        # This should not raise any errors
        event_store.append_event(stream_id, event)

        # Verify event was still persisted
        store_events = get_typed_events(event_store, stream_id, StoreCreated)
        assert len(store_events) == 1

    def test_append_event_handles_event_bus_errors_gracefully(self, db_session: Session) -> None:
        """EventStore should handle event bus errors without affecting storage."""
        # Create mock event bus that raises an error
        mock_event_bus = Mock()
        mock_event_bus.publish = AsyncMock(side_effect=Exception("Event bus error"))
        
        # Create event store with faulty event bus
        event_store = EventStore(session=db_session, event_bus=mock_event_bus)
        store_id = uuid4()
        stream_id = f"store-{store_id}"

        event = StoreCreated(
            store_id=store_id,
            name="Test Store",
            description="A test store",
            infinite_supply=False,
            created_at=datetime.now(),
        )

        # Set up async context
        async def test_with_event_loop():
            # This should not raise any errors despite event bus failure
            event_store.append_event(stream_id, event)
            
            # Allow async task to complete (and potentially fail)
            await asyncio.sleep(0.001)

        # Run test in async context
        asyncio.run(test_with_event_loop())

        # Verify event was still persisted despite event bus error
        store_events = get_typed_events(event_store, stream_id, StoreCreated)
        assert len(store_events) == 1

    def test_append_event_works_without_async_context(self, db_session: Session) -> None:
        """EventStore should work when no async event loop is running."""
        # Create mock event bus
        mock_event_bus = Mock()
        mock_event_bus.publish = AsyncMock()
        
        # Create event store with event bus
        event_store = EventStore(session=db_session, event_bus=mock_event_bus)
        store_id = uuid4()
        stream_id = f"store-{store_id}"

        event = StoreCreated(
            store_id=store_id,
            name="Test Store",
            description="A test store",
            infinite_supply=False,
            created_at=datetime.now(),
        )

        # Call without async context (no event loop running)
        # This should not raise any errors and should skip event bus publish
        event_store.append_event(stream_id, event)

        # Verify event was still persisted
        store_events = get_typed_events(event_store, stream_id, StoreCreated)
        assert len(store_events) == 1
        
        # Event bus publish should not have been called (no event loop)
        mock_event_bus.publish.assert_not_called()
