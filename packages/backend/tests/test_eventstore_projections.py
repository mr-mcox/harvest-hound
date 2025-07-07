"""
Test EventStore integration with projection registry.

Testing the refactored EventStore that uses projection registry instead of
inline projection logic, following ADR-005 separation of concerns.
"""
from datetime import datetime
from uuid import uuid4
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.events.domain_events import InventoryItemAdded, StoreCreated, IngredientCreated
from app.infrastructure.event_store import EventStore
from app.infrastructure.database import metadata
from app.projections.registry import ProjectionRegistry


@pytest.fixture
def db_session():
    """Create isolated test database session."""
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


class TestEventStoreWithProjectionRegistry:
    """Test EventStore integration with projection registry."""

    def test_append_event_triggers_projections(self, db_session):
        """EventStore should trigger projection registry when appending events."""
        # Arrange
        mock_registry = Mock(spec=ProjectionRegistry)
        
        event_store = EventStore(session=db_session, projection_registry=mock_registry)
        
        event = StoreCreated(
            store_id=uuid4(),
            name="CSA Box",
            description="Weekly delivery",
            infinite_supply=False,
            created_at=datetime(2024, 1, 15, 10, 0),
        )
        
        # Act
        event_store.append_event("store-123", event)
        
        # Assert
        mock_registry.handle.assert_called_once_with(event)

    def test_append_event_multiple_events_triggers_all(self, db_session):
        """EventStore should trigger projections for all events."""
        # Arrange
        mock_registry = Mock(spec=ProjectionRegistry)
        
        event_store = EventStore(session=db_session, projection_registry=mock_registry)
        
        store_event = StoreCreated(
            store_id=uuid4(),
            name="CSA Box",
            description="Weekly delivery",
            infinite_supply=False,
            created_at=datetime(2024, 1, 15, 10, 0),
        )
        
        ingredient_event = IngredientCreated(
            ingredient_id=uuid4(),
            name="Carrots",
            default_unit="lbs",
            created_at=datetime(2024, 1, 15, 10, 5),
        )
        
        # Act
        event_store.append_event("store-123", store_event)
        event_store.append_event("ingredient-456", ingredient_event)
        
        # Assert
        assert mock_registry.handle.call_count == 2
        mock_registry.handle.assert_any_call(store_event)
        mock_registry.handle.assert_any_call(ingredient_event)

    def test_eventstore_without_registry_works(self, db_session):
        """EventStore should work without projection registry (optional dependency)."""
        # Arrange
        # EventStore without projection registry
        event_store = EventStore(session=db_session, projection_registry=None)
        
        event = StoreCreated(
            store_id=uuid4(),
            name="CSA Box",
            description="Weekly delivery",
            infinite_supply=False,
            created_at=datetime(2024, 1, 15, 10, 0),
        )
        
        # Act & Assert - should not raise exception
        event_store.append_event("store-123", event)
        
        # Verify event was still stored
        events = event_store.load_events("store-123")
        assert len(events) == 1
        assert events[0]["event_type"] == "StoreCreated"

    def test_projection_errors_dont_break_event_storage(self, db_session):
        """EventStore should store events even if projections fail."""
        # Arrange
        mock_registry = Mock(spec=ProjectionRegistry)
        mock_registry.handle.side_effect = Exception("Projection failed")
        
        event_store = EventStore(session=db_session, projection_registry=mock_registry)
        
        event = StoreCreated(
            store_id=uuid4(),
            name="CSA Box",
            description="Weekly delivery",
            infinite_supply=False,
            created_at=datetime(2024, 1, 15, 10, 0),
        )
        
        # Act & Assert - should not raise exception despite projection failure
        event_store.append_event("store-123", event)
        
        # Verify event was still stored
        events = event_store.load_events("store-123")
        assert len(events) == 1
        assert events[0]["event_type"] == "StoreCreated"

    def test_eventstore_maintains_existing_query_methods(self, db_session):
        """EventStore should maintain backward compatibility with existing query methods."""
        # Arrange
        event_store = EventStore(session=db_session, projection_registry=None)
        
        store_id = uuid4()
        ingredient_id = uuid4()
        
        store_event = StoreCreated(
            store_id=store_id,
            name="CSA Box",
            description="Weekly delivery",
            infinite_supply=False,
            created_at=datetime(2024, 1, 15, 10, 0),
        )
        
        ingredient_event = IngredientCreated(
            ingredient_id=ingredient_id,
            name="Carrots",
            default_unit="lbs",
            created_at=datetime(2024, 1, 15, 10, 5),
        )
        
        inventory_event = InventoryItemAdded(
            store_id=store_id,
            ingredient_id=ingredient_id,
            quantity=2.0,
            unit="lbs",
            notes="Fresh",
            added_at=datetime(2024, 1, 15, 14, 30),
        )
        
        # Act
        event_store.append_event(f"store-{store_id}", store_event)
        event_store.append_event(f"ingredient-{ingredient_id}", ingredient_event)
        event_store.append_event(f"store-{store_id}", inventory_event)
        
        # Assert - event storage should still work
        events = event_store.load_events(f"store-{store_id}")
        assert len(events) >= 2  # store created + inventory added