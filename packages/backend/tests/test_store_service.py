import os
import tempfile
from typing import Generator, List
from uuid import uuid4

import pytest

from app.events.domain_events import IngredientCreated, InventoryItemAdded, StoreCreated
from app.infrastructure.event_store import EventStore
from app.infrastructure.repositories import IngredientRepository, StoreRepository
from app.models.parsed_inventory import ParsedInventoryItem
from app.services.inventory_parser import MockInventoryParserClient
from app.services.store_service import InventoryUploadResult, StoreService
from tests.test_utils import assert_event_matches, get_typed_events


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
def inventory_parser() -> MockInventoryParserClient:
    """Create a test inventory parser client."""
    return MockInventoryParserClient()


@pytest.fixture
def store_service(
    store_repository: StoreRepository,
    ingredient_repository: IngredientRepository,
    inventory_parser: MockInventoryParserClient,
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
        store_events = get_typed_events(event_store, f"store-{store_id}", StoreCreated)

        assert len(store_events) == 1
        assert_event_matches(
            store_events[0],
            {
                "store_id": store_id,
                "name": "CSA Box",
                "description": "Weekly vegetable box",
                "infinite_supply": False,
            },
        )

    def test_create_store_with_infinite_supply_true_sets_flag_correctly(
        self, store_service: StoreService, event_store: EventStore
    ) -> None:
        """Test that create_store with infinite_supply=True sets flag correctly."""
        # Act
        store_id = store_service.create_store(
            "Pantry", "Long-term storage", infinite_supply=True
        )

        # Assert
        store_events = get_typed_events(event_store, f"store-{store_id}", StoreCreated)

        assert len(store_events) == 1
        assert_event_matches(store_events[0], {"infinite_supply": True})

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
        first_events = get_typed_events(
            event_store, f"store-{first_store_id}", StoreCreated
        )
        assert len(first_events) == 1
        assert_event_matches(first_events[0], {"description": "First box"})

        # Check second store events
        second_events = get_typed_events(
            event_store, f"store-{second_store_id}", StoreCreated
        )
        assert len(second_events) == 1
        assert_event_matches(second_events[0], {"description": "Second box"})


class TestInventoryUpload:
    """Test inventory upload behavior."""

    def test_upload_inventory_parses_text_and_creates_new_ingredient(
        self,
        store_service: StoreService,
        event_store: EventStore,
        inventory_parser: MockInventoryParserClient,
    ) -> None:
        """Test that upload_inventory parses text and creates new Ingredient."""
        # Arrange
        store_id = store_service.create_store("CSA Box")

        # Configure parser to return parsed item
        parsed_item = ParsedInventoryItem(name="carrots", quantity=2.0, unit="pound")
        inventory_parser.mock_results = [parsed_item]

        # Act
        result = store_service.upload_inventory(store_id, "2 lbs carrots")

        # Assert - successful upload
        assert result.success is True
        assert result.items_added == 1
        assert result.errors == []

        # Check that InventoryItemAdded event was persisted
        inventory_events = get_typed_events(
            event_store, f"store-{store_id}", InventoryItemAdded
        )
        assert len(inventory_events) == 1
        assert_event_matches(
            inventory_events[0],
            {"store_id": store_id, "quantity": 2.0, "unit": "pound"},
        )

        # Check that IngredientCreated event was persisted
        ingredient_id = inventory_events[0].ingredient_id
        ingredient_events = get_typed_events(
            event_store, f"ingredient-{ingredient_id}", IngredientCreated
        )

        assert len(ingredient_events) == 1
        assert_event_matches(
            ingredient_events[0], {"name": "carrots", "default_unit": "pound"}
        )

    def test_upload_inventory_creates_inventory_item_linking_to_ingredient(
        self,
        store_service: StoreService,
        event_store: EventStore,
        inventory_parser: MockInventoryParserClient,
    ) -> None:
        """Test that upload_inventory creates InventoryItem linking to ingredient."""
        # Arrange
        store_id = store_service.create_store("CSA Box")
        parsed_item = ParsedInventoryItem(name="kale", quantity=1.0, unit="bunch")
        inventory_parser.mock_results = [parsed_item]

        # Act
        store_service.upload_inventory(store_id, "1 bunch kale")

        # Assert - check InventoryItemAdded event
        inventory_events = get_typed_events(
            event_store, f"store-{store_id}", InventoryItemAdded
        )
        assert len(inventory_events) == 1
        assert_event_matches(
            inventory_events[0],
            {"store_id": store_id, "quantity": 1.0, "unit": "bunch"},
        )

        # Verify ingredient_id links to actual ingredient
        ingredient_id = inventory_events[0].ingredient_id
        ingredient_events = get_typed_events(
            event_store, f"ingredient-{ingredient_id}", IngredientCreated
        )
        assert len(ingredient_events) == 1
        assert_event_matches(ingredient_events[0], {"name": "kale"})

    def test_upload_inventory_returns_upload_result_with_items_added_count(
        self,
        store_service: StoreService,
        inventory_parser: MockInventoryParserClient,
    ) -> None:
        """Test that upload_inventory returns InventoryUploadResult with count."""
        # Arrange
        store_id = store_service.create_store("CSA Box")
        parsed_items = [
            ParsedInventoryItem(name="carrots", quantity=2.0, unit="pound"),
            ParsedInventoryItem(name="kale", quantity=1.0, unit="bunch"),
        ]
        inventory_parser.mock_results = parsed_items

        # Act
        result = store_service.upload_inventory(store_id, "2 lbs carrots\n1 bunch kale")

        # Assert
        assert isinstance(result, InventoryUploadResult)
        assert result.success is True
        assert result.items_added == 2
        assert result.errors == []

    def test_upload_inventory_handles_parsing_errors(
        self,
        store_service: StoreService,
        inventory_parser: MockInventoryParserClient,
    ) -> None:
        """Test that upload_inventory handles LLM parsing errors."""
        # Arrange
        store_id = store_service.create_store("CSA Box")

        # Configure parser to trigger an exception through parse_inventory call
        # by using a mock that raises an exception when called
        class FailingMockParser(MockInventoryParserClient):
            def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
                raise ValueError("Failed to parse inventory text")

        # Replace the parser with our failing version
        failing_parser = FailingMockParser()
        store_service.inventory_parser = failing_parser

        # Act
        result = store_service.upload_inventory(store_id, "invalid text")

        # Assert
        assert result.success is False
        assert result.items_added == 0
        assert len(result.errors) == 1
        assert "Failed to parse inventory text" in result.errors[0]

    def test_get_store_inventory_returns_current_inventory_with_ingredient_names(
        self,
        store_service: StoreService,
        inventory_parser: MockInventoryParserClient,
    ) -> None:
        """Test that get_store_inventory returns current inventory with names."""
        # Arrange
        store_id = store_service.create_store("CSA Box")
        parsed_items = [
            ParsedInventoryItem(name="carrots", quantity=2.0, unit="pound"),
            ParsedInventoryItem(name="kale", quantity=1.0, unit="bunch"),
        ]
        inventory_parser.mock_results = parsed_items

        # Upload inventory
        store_service.upload_inventory(store_id, "2 lbs carrots\n1 bunch kale")

        # Act
        inventory = store_service.get_store_inventory(store_id)

        # Assert
        assert len(inventory) == 2

        # Sort by ingredient name for consistent assertions
        inventory_by_name = {item["ingredient_name"]: item for item in inventory}

        assert "carrots" in inventory_by_name
        carrots_item = inventory_by_name["carrots"]
        assert carrots_item["quantity"] == 2.0
        assert carrots_item["unit"] == "pound"
        assert carrots_item["notes"] is None
        assert "added_at" in carrots_item

        assert "kale" in inventory_by_name
        kale_item = inventory_by_name["kale"]
        assert kale_item["quantity"] == 1.0
        assert kale_item["unit"] == "bunch"
        assert kale_item["notes"] is None
        assert "added_at" in kale_item
