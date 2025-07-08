"""Integration tests for event store with event bus."""

import asyncio
from datetime import datetime
from typing import Generator
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.events.domain_events import StoreCreated
from app.infrastructure.event_store import EventStore
from app.infrastructure.database import metadata


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Create isolated test database session."""
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


class TestEventStoreIntegration:
    """Test EventStore works with event bus."""

    def test_append_event_triggers_event_bus(self, db_session: Session) -> None:
        """EventStore should trigger event bus when available."""
        # Create mock event bus
        mock_event_bus = Mock()
        mock_event_bus.publish = AsyncMock()
        
        # Create event store with event bus
        event_store = EventStore(
            session=db_session,
            event_bus=mock_event_bus
        )
        
        store_id = uuid4()
        stream_id = f"store-{store_id}"
        event = StoreCreated(
            store_id=store_id,
            name="Test Store",
            description="A test store",
            infinite_supply=False,
            created_at=datetime.now(),
        )

        # Set up async context for event bus
        async def test_with_event_loop() -> None:
            # Append event (should trigger event bus)
            event_store.append_event(stream_id, event)
            
            # Allow async task to complete
            await asyncio.sleep(0.001)
            
            # Verify event bus was called
            mock_event_bus.publish.assert_called_once_with(event)

        # Run test in async context
        asyncio.run(test_with_event_loop())

    def test_event_bus_failure_does_not_affect_event_storage(self, db_session: Session) -> None:
        """Event bus failures should not affect event storage."""
        # Create failing mock event bus
        mock_event_bus = Mock()
        mock_event_bus.publish = AsyncMock(side_effect=Exception("Event bus error"))
        
        # Create event store with failing event bus
        event_store = EventStore(
            session=db_session,
            event_bus=mock_event_bus
        )
        
        store_id = uuid4()
        stream_id = f"store-{store_id}"
        event = StoreCreated(
            store_id=store_id,
            name="Test Store",
            description="A test store",
            infinite_supply=False,
            created_at=datetime.now(),
        )

        # Set up async context for event bus
        async def test_with_event_loop() -> None:
            # This should not raise errors despite event bus failure
            event_store.append_event(stream_id, event)
            
            # Allow async task to complete (and potentially fail)
            await asyncio.sleep(0.001)
            
            # Verify event was still stored despite event bus failure
            events = event_store.load_events(stream_id)
            assert len(events) == 1
            assert events[0]["event_type"] == "StoreCreated"

        # Run test in async context
        asyncio.run(test_with_event_loop())

    def test_event_store_works_without_event_bus(self, db_session: Session) -> None:
        """EventStore should work normally without event bus."""
        # Create event store without event bus
        event_store = EventStore(
            session=db_session,
            event_bus=None
        )
        
        store_id = uuid4()
        stream_id = f"store-{store_id}"
        event = StoreCreated(
            store_id=store_id,
            name="Test Store",
            description="A test store",
            infinite_supply=False,
            created_at=datetime.now(),
        )

        # This should work without any issues
        event_store.append_event(stream_id, event)
        
        # Verify event was stored
        events = event_store.load_events(stream_id)
        assert len(events) == 1
        assert events[0]["event_type"] == "StoreCreated"