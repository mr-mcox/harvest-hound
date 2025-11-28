"""Test projection handlers working via event bus subscription."""

from datetime import datetime
from typing import Generator
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.events.domain_events import StoreCreated
from app.infrastructure.database import metadata
from app.infrastructure.event_bus import InMemoryEventBus
from app.infrastructure.view_stores import StoreViewStore
from app.projections.handlers import StoreProjectionHandler


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Create isolated test database session."""
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()


class TestProjectionHandlersEventBusIntegration:
    """Test that projection handlers work correctly when subscribed to event bus."""

    @pytest.mark.asyncio
    async def test_store_projection_handler_via_event_bus(
        self, db_session: Session
    ) -> None:
        """Test that StoreProjectionHandler works when subscribed to event bus."""
        # Given
        event_bus = InMemoryEventBus()
        view_store = StoreViewStore(db_session)
        handler = StoreProjectionHandler(view_store)

        # Subscribe handler to event bus
        await event_bus.subscribe(StoreCreated, handler.handle_store_created)

        # Create event
        store_id = uuid4()
        event = StoreCreated(
            store_id=store_id,
            name="Test Store",
            description="Test description",
            store_type="explicit",
            created_at=datetime.now(),
        )

        # When
        await event_bus.publish(event)

        # Then
        # Verify the handler was called by checking the view store
        stored_views = view_store.get_all_stores()
        assert len(stored_views) == 1

        created_view = stored_views[0]
        assert created_view.store_id == store_id
        assert created_view.name == "Test Store"
        assert created_view.description == "Test description"
        assert created_view.store_type == "explicit"
        assert created_view.item_count == 0

    @pytest.mark.asyncio
    async def test_multiple_handlers_via_event_bus(self, db_session: Session) -> None:
        """Test that multiple handlers can be subscribed to the same event type."""
        # Given
        event_bus = InMemoryEventBus()
        view_store1 = StoreViewStore(db_session)
        view_store2 = StoreViewStore(db_session)
        handler1 = StoreProjectionHandler(view_store1)
        handler2 = StoreProjectionHandler(view_store2)

        # Subscribe both handlers to the same event type
        await event_bus.subscribe(StoreCreated, handler1.handle_store_created)
        await event_bus.subscribe(StoreCreated, handler2.handle_store_created)

        # Create event
        store_id = uuid4()
        event = StoreCreated(
            store_id=store_id,
            name="Test Store",
            description="Test description",
            store_type="explicit",
            created_at=datetime.now(),
        )

        # When
        await event_bus.publish(event)

        # Then
        # Both handlers should have been called, but they use upsert so only 1
        # record exists
        stored_views = view_store1.get_all_stores()
        assert len(stored_views) == 1  # Upsert behavior - only one record per store_id

        # Verify the data is correct
        view = stored_views[0]
        assert view.store_id == store_id
        assert view.name == "Test Store"
