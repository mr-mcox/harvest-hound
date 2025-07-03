import os
import tempfile
from typing import Generator
from uuid import uuid4

import pytest

from app.infrastructure.event_store import EventStore
from app.infrastructure.repositories import IngredientRepository, StoreRepository
from app.services.inventory_parser import TestInventoryParserClient
from app.services.store_service import StoreService


@pytest.fixture
def temp_db() -> Generator[str, None, None]:
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    yield db_path

    # Clean up
    os.unlink(db_path)


@pytest.fixture
def event_store(temp_db: str) -> EventStore:
    """Create an EventStore instance for testing."""
    return EventStore(temp_db)


@pytest.fixture
def store_repository(event_store: EventStore) -> StoreRepository:
    """Create a StoreRepository for testing."""
    return StoreRepository(event_store)


@pytest.fixture
def ingredient_repository(event_store: EventStore) -> IngredientRepository:
    """Create an IngredientRepository for testing."""
    return IngredientRepository(event_store)


@pytest.fixture
def inventory_parser() -> TestInventoryParserClient:
    """Create a test inventory parser client."""
    return TestInventoryParserClient()


@pytest.fixture
def store_service(
    store_repository: StoreRepository,
    ingredient_repository: IngredientRepository,
    inventory_parser: TestInventoryParserClient,
) -> StoreService:
    """Create a StoreService for testing."""
    return StoreService(store_repository, ingredient_repository, inventory_parser)


class TestStoreCreation:
    """Test store creation behavior."""

    def test_create_store_returns_uuid_and_persists_store_created_event(
        self, store_service: StoreService, event_store: EventStore
    ) -> None:
        """Test that create_store returns UUID and persists StoreCreated event."""
        # Act
        store_id = store_service.create_store("CSA Box", "Weekly vegetable box")

        # Assert
        assert isinstance(store_id, type(uuid4()))

        # Check that StoreCreated event was persisted
        stream_id = f"store-{store_id}"
        events = event_store.load_events(stream_id)

        assert len(events) == 1
        assert events[0]["event_type"] == "StoreCreated"
        assert events[0]["event_data"]["store_id"] == str(store_id)
        assert events[0]["event_data"]["name"] == "CSA Box"
        assert events[0]["event_data"]["description"] == "Weekly vegetable box"
        assert events[0]["event_data"]["infinite_supply"] is False

    def test_create_store_with_infinite_supply_true_sets_flag_correctly(
        self, store_service: StoreService, event_store: EventStore
    ) -> None:
        """Test that create_store with infinite_supply=True sets flag correctly."""
        # Act
        store_id = store_service.create_store(
            "Pantry", "Long-term storage", infinite_supply=True
        )

        # Assert
        stream_id = f"store-{store_id}"
        events = event_store.load_events(stream_id)

        assert len(events) == 1
        assert events[0]["event_type"] == "StoreCreated"
        assert events[0]["event_data"]["infinite_supply"] is True

    def test_create_store_with_duplicate_name_succeeds(
        self, store_service: StoreService, event_store: EventStore
    ) -> None:
        """Test that create_store with duplicate name succeeds."""
        # Arrange - create first store
        first_store_id = store_service.create_store("CSA Box", "First box")

        # Act - create second store with same name
        second_store_id = store_service.create_store("CSA Box", "Second box")

        # Assert - both stores should exist with different IDs
        assert first_store_id != second_store_id

        # Check first store events
        first_stream_id = f"store-{first_store_id}"
        first_events = event_store.load_events(first_stream_id)
        assert len(first_events) == 1
        assert first_events[0]["event_data"]["description"] == "First box"

        # Check second store events
        second_stream_id = f"store-{second_store_id}"
        second_events = event_store.load_events(second_stream_id)
        assert len(second_events) == 1
        assert second_events[0]["event_data"]["description"] == "Second box"
