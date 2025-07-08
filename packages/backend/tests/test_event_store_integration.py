"""Integration tests for event store with both projection registry and event bus."""

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
from app.projections.registry import ProjectionRegistry


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
    """Test EventStore works with both projection registry and event bus."""

    def test_append_event_triggers_both_projections_and_event_bus(self, db_session: Session) -> None:
        """EventStore should trigger both projection registry and event bus when both are available."""
        # Create mock projection registry
        mock_projection_registry = Mock(spec=ProjectionRegistry)
        mock_projection_registry.handle = Mock()
        
        # Create mock event bus
        mock_event_bus = Mock()
        mock_event_bus.publish = AsyncMock()
        
        # Create event store with both systems
        event_store = EventStore(
            session=db_session,
            projection_registry=mock_projection_registry,
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
        async def test_with_event_loop():
            # Append event (should trigger both systems)
            event_store.append_event(stream_id, event)
            
            # Allow async task to complete
            await asyncio.sleep(0.001)
            
            # Verify projection registry was called
            mock_projection_registry.handle.assert_called_once_with(event)
            
            # Verify event bus was called
            mock_event_bus.publish.assert_called_once_with(event)

        # Run test in async context
        asyncio.run(test_with_event_loop())

    def test_projection_registry_failure_does_not_affect_event_bus(self, db_session: Session) -> None:
        """Projection registry failures should not affect event bus publishing."""
        # Create failing mock projection registry
        mock_projection_registry = Mock(spec=ProjectionRegistry)
        mock_projection_registry.handle = Mock(side_effect=Exception("Projection error"))
        
        # Create mock event bus
        mock_event_bus = Mock()
        mock_event_bus.publish = AsyncMock()
        
        # Create event store with both systems
        event_store = EventStore(
            session=db_session,
            projection_registry=mock_projection_registry,
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
        async def test_with_event_loop():
            # This should not raise errors despite projection failure
            event_store.append_event(stream_id, event)
            
            # Allow async task to complete
            await asyncio.sleep(0.001)
            
            # Verify projection registry was called (and failed)
            mock_projection_registry.handle.assert_called_once_with(event)
            
            # Verify event bus was still called despite projection failure
            mock_event_bus.publish.assert_called_once_with(event)

        # Run test in async context
        asyncio.run(test_with_event_loop())

    def test_event_bus_failure_does_not_affect_projection_registry(self, db_session: Session) -> None:
        """Event bus failures should not affect projection registry handling."""
        # Create mock projection registry
        mock_projection_registry = Mock(spec=ProjectionRegistry)
        mock_projection_registry.handle = Mock()
        
        # Create failing mock event bus
        mock_event_bus = Mock()
        mock_event_bus.publish = AsyncMock(side_effect=Exception("Event bus error"))
        
        # Create event store with both systems
        event_store = EventStore(
            session=db_session,
            projection_registry=mock_projection_registry,
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
        async def test_with_event_loop():
            # This should not raise errors despite event bus failure
            event_store.append_event(stream_id, event)
            
            # Allow async task to complete (and potentially fail)
            await asyncio.sleep(0.001)
            
            # Verify projection registry was called successfully
            mock_projection_registry.handle.assert_called_once_with(event)

        # Run test in async context
        asyncio.run(test_with_event_loop())

    def test_backward_compatibility_with_only_projection_registry(self, db_session: Session) -> None:
        """EventStore should work normally with only projection registry (backward compatibility)."""
        # Create mock projection registry
        mock_projection_registry = Mock(spec=ProjectionRegistry)
        mock_projection_registry.handle = Mock()
        
        # Create event store with only projection registry (old behavior)
        event_store = EventStore(
            session=db_session,
            projection_registry=mock_projection_registry,
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

        # This should work exactly as before
        event_store.append_event(stream_id, event)
        
        # Verify projection registry was called
        mock_projection_registry.handle.assert_called_once_with(event)