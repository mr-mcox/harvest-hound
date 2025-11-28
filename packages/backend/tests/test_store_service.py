from typing import Generator, List
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.events.domain_events import (
    IngredientCreated,
    InventoryItemAdded,
    StoreCreated,
    StoreCreatedWithInventory,
)
from app.infrastructure.database import metadata
from app.infrastructure.event_bus import InMemoryEventBus
from app.infrastructure.event_publisher import EventPublisher
from app.infrastructure.event_store import EventStore
from app.infrastructure.repositories import IngredientRepository, StoreRepository
from app.infrastructure.view_stores import InventoryItemViewStore, StoreViewStore
from app.models.parsed_inventory import ParsedInventoryItem
from app.projections.handlers import InventoryProjectionHandler, StoreProjectionHandler
from app.services.inventory_parser import MockInventoryParserClient
from app.services.store_service import (
    InventoryUploadResult,
    StoreService,
)
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


@pytest.fixture
def shared_event_bus() -> InMemoryEventBus:
    """Create a shared event bus for all test components."""
    return InMemoryEventBus()


@pytest.fixture
def event_store(
    db_session: Session,
    shared_event_bus: InMemoryEventBus,
    store_view_store: StoreViewStore,
    inventory_item_view_store: InventoryItemViewStore,
) -> EventStore:
    """Create an EventStore instance for testing with event bus."""
    import asyncio

    # Create event store and event publisher with shared event bus
    event_store = EventStore(session=db_session)
    event_publisher = EventPublisher(shared_event_bus)

    # Create projection handlers
    store_projection_handler = StoreProjectionHandler(store_view_store)

    # Create ingredient and store repositories with event publisher
    ingredient_repository = IngredientRepository(event_store, event_publisher)
    store_repository = StoreRepository(event_store, event_publisher)

    inventory_projection_handler = InventoryProjectionHandler(
        ingredient_repository, store_repository, inventory_item_view_store
    )

    # Subscribe handlers to event bus synchronously
    async def setup_subscribers() -> None:
        await shared_event_bus.subscribe(
            StoreCreated, store_projection_handler.handle_store_created
        )
        await shared_event_bus.subscribe(
            InventoryItemAdded, store_projection_handler.handle_inventory_item_added
        )
        await shared_event_bus.subscribe(
            InventoryItemAdded, inventory_projection_handler.handle_inventory_item_added
        )
        await shared_event_bus.subscribe(
            IngredientCreated, inventory_projection_handler.handle_ingredient_created
        )

    # Run the async setup
    asyncio.run(setup_subscribers())

    return event_store


@pytest.fixture
def store_repository(
    event_store: EventStore, shared_event_bus: InMemoryEventBus
) -> StoreRepository:
    """Create a StoreRepository for testing."""
    event_publisher = EventPublisher(shared_event_bus)
    return StoreRepository(event_store, event_publisher)


@pytest.fixture
def ingredient_repository(
    event_store: EventStore, shared_event_bus: InMemoryEventBus
) -> IngredientRepository:
    """Create an IngredientRepository for testing."""
    event_publisher = EventPublisher(shared_event_bus)
    return IngredientRepository(event_store, event_publisher)


@pytest.fixture
def inventory_parser() -> MockInventoryParserClient:
    """Create a test inventory parser client."""
    return MockInventoryParserClient()


@pytest.fixture
def store_view_store(db_session: Session) -> StoreViewStore:
    """Create a StoreViewStore for testing."""
    return StoreViewStore(session=db_session)


@pytest.fixture
def inventory_item_view_store(db_session: Session) -> InventoryItemViewStore:
    """Create an InventoryItemViewStore for testing."""
    return InventoryItemViewStore(session=db_session)


@pytest.fixture
def store_service(
    store_repository: StoreRepository,
    ingredient_repository: IngredientRepository,
    inventory_parser: MockInventoryParserClient,
    store_view_store: StoreViewStore,
    inventory_item_view_store: InventoryItemViewStore,
    event_store: EventStore,
    shared_event_bus: InMemoryEventBus,
) -> StoreService:
    """Create a StoreService for testing."""
    from app.infrastructure.event_publisher import EventPublisher

    event_publisher = EventPublisher(shared_event_bus)
    return StoreService(
        store_repository,
        ingredient_repository,
        inventory_parser,
        store_view_store,
        inventory_item_view_store,
        event_store,
        event_publisher,
    )


class TestStoreCreation:
    """Test store creation behavior."""

    def test_create_store_returns_uuid_and_persists_store_created_event(
        self,
        store_service: StoreService,
        event_store: EventStore,
        store_view_store: StoreViewStore,
    ) -> None:
        """Test that create_store returns UUID and persists StoreCreated event."""
        # Act
        result = store_service.create_store_with_inventory(
            "CSA Box", "Weekly vegetable box", "explicit", None
        )
        store_id = result.store_id

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
                "store_type": "explicit",
            },
        )

        # Check that StoreView was created (view propagation)
        store_view = store_view_store.get_by_store_id(store_id)
        assert store_view is not None
        assert store_view.store_id == store_id
        assert store_view.name == "CSA Box"
        assert store_view.description == "Weekly vegetable box"
        assert store_view.store_type == "explicit"
        assert store_view.item_count == 0  # New store starts with 0 items

    def test_create_explicit_store_sets_type_correctly(
        self, store_service: StoreService, event_store: EventStore
    ) -> None:
        """Test that create_store with store_type="explicit" sets type correctly."""
        # Act
        result = store_service.create_store_with_inventory(
            "Pantry", "Long-term storage", store_type="explicit", inventory_text=None
        )
        store_id = result.store_id

        # Assert
        store_events = get_typed_events(event_store, f"store-{store_id}", StoreCreated)

        assert len(store_events) == 1
        assert_event_matches(store_events[0], {"store_type": "explicit"})

    def test_create_store_with_duplicate_name_succeeds(
        self, store_service: StoreService, event_store: EventStore
    ) -> None:
        """Test that create_store with duplicate name succeeds."""
        # Arrange - create first store
        first_result = store_service.create_store_with_inventory(
            "CSA Box", "First box", "explicit", None
        )
        first_store_id = first_result.store_id

        # Act - create second store with same name
        second_result = store_service.create_store_with_inventory(
            "CSA Box", "Second box", "explicit", None
        )
        second_store_id = second_result.store_id

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
        store_view_store: StoreViewStore,
        inventory_item_view_store: InventoryItemViewStore,
    ) -> None:
        """Test that upload_inventory parses text and creates new Ingredient."""
        # Arrange
        result = store_service.create_store_with_inventory(
            "CSA Box", "", "explicit", None
        )
        store_id = result.store_id

        # Configure parser to return parsed item
        parsed_item = ParsedInventoryItem(name="carrots", quantity=2.0, unit="pound")
        inventory_parser.mock_results = [parsed_item]

        # Act
        upload_result = store_service.upload_inventory(store_id, "2 lbs carrots")

        # Assert - successful upload
        assert upload_result.success is True
        assert upload_result.items_added == 1
        assert upload_result.errors == []

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

        # Check that InventoryItemView was created (view propagation)
        inventory_views = inventory_item_view_store.get_all_for_store(store_id)
        assert len(inventory_views) == 1

        inventory_view = inventory_views[0]
        assert inventory_view.store_id == store_id
        assert inventory_view.ingredient_id == ingredient_id
        assert inventory_view.ingredient_name == "carrots"
        assert inventory_view.store_name == "CSA Box"
        assert inventory_view.quantity == 2.0
        assert inventory_view.unit == "pound"

        # Check that StoreView item_count was updated (view propagation)
        store_view = store_view_store.get_by_store_id(store_id)
        assert store_view is not None
        assert store_view.item_count == 1

    def test_upload_inventory_creates_inventory_item_linking_to_ingredient(
        self,
        store_service: StoreService,
        event_store: EventStore,
        inventory_parser: MockInventoryParserClient,
    ) -> None:
        """Test that upload_inventory creates InventoryItem linking to ingredient."""
        # Arrange
        result = store_service.create_store_with_inventory(
            "CSA Box", "", "explicit", None
        )
        store_id = result.store_id
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
        result = store_service.create_store_with_inventory(
            "CSA Box", "", "explicit", None
        )
        store_id = result.store_id
        parsed_items = [
            ParsedInventoryItem(name="carrots", quantity=2.0, unit="pound"),
            ParsedInventoryItem(name="kale", quantity=1.0, unit="bunch"),
        ]
        inventory_parser.mock_results = parsed_items

        # Act
        upload_result = store_service.upload_inventory(
            store_id, "2 lbs carrots\n1 bunch kale"
        )

        # Assert
        assert isinstance(upload_result, InventoryUploadResult)
        assert upload_result.success is True
        assert upload_result.items_added == 2
        assert upload_result.errors == []

    def test_upload_inventory_handles_parsing_errors(
        self,
        store_service: StoreService,
        inventory_parser: MockInventoryParserClient,
    ) -> None:
        """Test that upload_inventory handles LLM parsing errors."""
        # Arrange
        result = store_service.create_store_with_inventory(
            "CSA Box", "", "explicit", None
        )
        store_id = result.store_id

        # Configure parser to trigger an exception through parse_inventory call
        # by using a mock that raises an exception when called
        class FailingMockParser(MockInventoryParserClient):
            def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
                raise ValueError("Failed to parse inventory text")

        # Replace the parser with our failing version
        failing_parser = FailingMockParser()
        store_service.inventory_parser = failing_parser

        # Act
        upload_result = store_service.upload_inventory(store_id, "invalid text")

        # Assert
        assert upload_result.success is False
        assert upload_result.items_added == 0
        assert len(upload_result.errors) == 1
        assert "Failed to parse inventory text" in upload_result.errors[0]

    def test_upload_inventory_with_empty_parsing_result(
        self,
        store_service: StoreService,
        inventory_parser: MockInventoryParserClient,
    ) -> None:
        """Test that upload_inventory handles empty parsing results correctly."""
        # Arrange
        result = store_service.create_store_with_inventory(
            "CSA Box", "", "explicit", None
        )
        store_id = result.store_id

        # Configure parser to return empty list (parsing succeeds but finds nothing)
        class EmptyResultMockParser(MockInventoryParserClient):
            def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
                # Simulate LLM returning empty list (valid response, but no items found)
                return []

        # Replace the parser with our empty result version
        empty_parser = EmptyResultMockParser()
        store_service.inventory_parser = empty_parser

        # Act
        upload_result = store_service.upload_inventory(
            store_id, "some text that parses to nothing"
        )

        # Assert
        assert upload_result.success is True  # Parsing succeeded, just found no items
        assert upload_result.items_added == 0
        assert upload_result.errors == []

    def test_get_store_inventory_returns_current_inventory_with_ingredient_names(
        self,
        store_service: StoreService,
        inventory_parser: MockInventoryParserClient,
    ) -> None:
        """Test that get_store_inventory returns current inventory with names."""
        # Arrange
        result = store_service.create_store_with_inventory(
            "CSA Box", "", "explicit", None
        )
        store_id = result.store_id
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


class TestUnifiedCreationLogic:
    """Test unified store creation with optional inventory processing."""

    def test_create_store_without_inventory_calls_store_service_and_returns_result(
        self, store_service: StoreService, event_store: EventStore
    ) -> None:
        """Test that creating store without inventory text calls
        StoreService.create_store and returns proper result."""
        # Act
        result = store_service.create_store_with_inventory(
            name="CSA Box",
            description="Weekly vegetable box",
            store_type="explicit",
            inventory_text=None,
        )

        # Assert result structure
        assert hasattr(result, "store_id")
        assert hasattr(result, "successful_items")
        assert hasattr(result, "error_message")

        # Assert result values
        assert isinstance(result.store_id, type(uuid4()))
        assert result.successful_items == 0
        assert result.error_message is None

        # Verify StoreCreated event was persisted
        store_events = get_typed_events(
            event_store, f"store-{result.store_id}", StoreCreated
        )
        assert len(store_events) == 1
        assert_event_matches(
            store_events[0],
            {
                "store_id": result.store_id,
                "name": "CSA Box",
                "description": "Weekly vegetable box",
                "store_type": "explicit",
            },
        )

    def test_create_store_with_inventory_processes_items_and_emits_orchestration_event(
        self,
        store_service: StoreService,
        event_store: EventStore,
        inventory_parser: MockInventoryParserClient,
    ) -> None:
        """Test that creating store with inventory text processes items and emits
        StoreCreatedWithInventory event."""
        # Arrange - configure mock parser to return 2 items
        parsed_items = [
            ParsedInventoryItem(name="apples", quantity=2.0, unit="count"),
            ParsedInventoryItem(name="bananas", quantity=3.0, unit="count"),
        ]
        inventory_parser.mock_results = parsed_items

        # Act
        result = store_service.create_store_with_inventory(
            name="CSA Box",
            description="Weekly vegetable box",
            store_type="explicit",
            inventory_text="2 apples\n3 bananas",
        )

        # Assert
        assert isinstance(result.store_id, type(uuid4()))
        assert result.successful_items == 2  # Mock parser returns 2 items
        assert result.error_message is None

        # Verify StoreCreatedWithInventory event was persisted
        orchestration_events = get_typed_events(
            event_store,
            f"unified-creation-{result.store_id}",
            StoreCreatedWithInventory,
        )
        assert len(orchestration_events) == 1
        assert_event_matches(
            orchestration_events[0],
            {
                "store_id": result.store_id,
                "successful_items": 2,
                "error_message": None,
            },
        )

    def test_create_store_with_failing_inventory_returns_error_in_result(
        self, store_service: StoreService, event_store: EventStore
    ) -> None:
        """Test that inventory processing failures are captured in result with simple
        error message."""

        # Arrange - Create a custom mock that fails on upload_inventory
        class FailingInventoryService(StoreService):
            def upload_inventory(
                self, store_id: UUID, inventory_text: str
            ) -> InventoryUploadResult:
                return InventoryUploadResult.error_result(["Simulated parsing failure"])

        failing_service = FailingInventoryService(
            store_service.store_repository,
            store_service.ingredient_repository,
            store_service.inventory_parser,
            store_service.store_view_store,
            store_service.inventory_item_view_store,
            store_service.event_store,
            store_service.event_publisher,
        )

        # Act - processing should fail due to simulated parsing failure
        result = failing_service.create_store_with_inventory(
            name="CSA Box",
            description="Weekly vegetable box",
            store_type="explicit",
            inventory_text="some inventory text",
        )

        # Assert - store still created successfully, but with error message
        assert isinstance(result.store_id, type(uuid4()))
        assert result.successful_items == 0
        assert result.error_message is not None
        assert "failed" in result.error_message.lower()

        # Verify store was still created
        store_events = get_typed_events(
            event_store, f"store-{result.store_id}", StoreCreated
        )
        assert len(store_events) == 1

        # Verify unified creation event includes error message
        unified_events = get_typed_events(
            event_store,
            f"unified-creation-{result.store_id}",
            StoreCreatedWithInventory,
        )
        assert len(unified_events) == 1
        assert unified_events[0].error_message is not None


class TestEnhancedPartialSuccess:
    """Test enhanced StoreService for partial success scenarios."""

    def test_inventory_upload_result_includes_parsing_notes_field(self) -> None:
        """Test that InventoryUploadResult includes parsing_notes field for LLM error
        messages."""
        # Act - create result with parsing notes
        result = InventoryUploadResult(
            items_added=2,
            errors=["Item validation failed"],
            success=False,
            parsing_notes="LLM reported: 'Volvos' not a food item",
        )

        # Assert - parsing_notes field exists and works
        assert hasattr(result, "parsing_notes")
        assert result.parsing_notes == "LLM reported: 'Volvos' not a food item"

    def test_upload_inventory_processes_all_valid_items_despite_individual_failures(
        self, store_service: StoreService, inventory_parser: MockInventoryParserClient
    ) -> None:
        """Test that upload_inventory processes all successfully parsed items instead of
        stopping on first error."""
        # Arrange
        result = store_service.create_store_with_inventory(
            "Test Store", "", "explicit", None
        )
        store_id = result.store_id

        # Create a failing service that will fail on specific ingredient name
        class PartiallyFailingService(StoreService):
            def _create_or_get_ingredient(self, name: str, default_unit: str) -> UUID:
                if name == "problematic_item":
                    raise ValueError("Simulated ingredient creation failure")
                return super()._create_or_get_ingredient(name, default_unit)

        failing_service = PartiallyFailingService(
            store_service.store_repository,
            store_service.ingredient_repository,
            inventory_parser,
            store_service.store_view_store,
            store_service.inventory_item_view_store,
            store_service.event_store,
            store_service.event_publisher,
        )

        # Configure parser to return valid parsed items
        parsed_items = [
            ParsedInventoryItem(name="valid_item_1", quantity=2.0, unit="pound"),
            ParsedInventoryItem(
                name="problematic_item", quantity=1.0, unit="count"
            ),  # Will fail in ingredient creation
            ParsedInventoryItem(name="valid_item_2", quantity=3.0, unit="bunch"),
        ]
        inventory_parser.mock_results = parsed_items

        # Act - currently this will fail fast when ingredient creation fails
        upload_result = failing_service.upload_inventory(
            store_id, "2 lbs valid_item_1\n1 problematic_item\n3 bunches valid_item_2"
        )

        # Assert - should process valid items despite invalid ones
        assert upload_result.items_added == 2  # Should add both valid items
        assert upload_result.success is True  # Partial success is still success
        assert len(upload_result.errors) == 1  # Should capture the invalid item error
        assert "problematic_item" in str(upload_result.errors[0])

    def test_upload_inventory_returns_comprehensive_results_with_parsing_notes(
        self, store_service: StoreService, inventory_parser: MockInventoryParserClient
    ) -> None:
        """Test that upload_inventory returns comprehensive results including both
        successful item count and parsing notes."""
        # Arrange
        result = store_service.create_store_with_inventory(
            "Test Store", "", "explicit", None
        )
        store_id = result.store_id

        # Configure parser to return items with parsing notes
        parsed_items = [
            ParsedInventoryItem(name="apples", quantity=2.0, unit="count"),
        ]
        inventory_parser.mock_results = parsed_items
        # Configure mock to simulate parsing notes from LLM
        inventory_parser.mock_parsing_notes = (
            "LLM noted: 'eggs' quantity unclear, processed as 2 count"
        )

        # Act
        upload_result = store_service.upload_inventory(
            store_id, "2 apples and some eggs"
        )

        # Assert
        assert upload_result.items_added == 1
        assert upload_result.success is True
        assert (
            upload_result.parsing_notes
            == "LLM noted: 'eggs' quantity unclear, processed as 2 count"
        )


class TestBamlIntegrationErrorReporting:
    """Test enhanced BAML parsing with LLM error reporting integration."""

    def test_baml_parser_returns_parsing_notes_with_problematic_items(self) -> None:
        """Test that BAML parser can flag problematic items with natural language
        explanations."""
        import os

        if os.environ.get("ENABLE_BAML", "false").lower() != "true":
            pytest.skip(
                "BAML integration test - requires ENABLE_BAML=true and real LLM calls"
            )

        from app.services.inventory_parser import BamlInventoryParserClient

        parser = BamlInventoryParserClient()

        # Test with mix of valid ingredients and problematic items
        result = parser.parse_inventory_with_notes(
            "2 apples, 1 Volvo car, 3 gazillion eggs, 1 banana"
        )

        # Should extract valid items only
        assert len(result.items) == 2  # apples, banana
        valid_names = [item.name for item in result.items]
        assert "apple" in valid_names
        assert "banana" in valid_names

        # Should provide parsing notes about problematic items
        assert result.parsing_notes is not None
        notes_lower = result.parsing_notes.lower()
        # Check that problematic items are mentioned in notes
        assert any(term in notes_lower for term in ["volvo", "car", "gazillion"])

    def test_baml_parser_clean_input_no_parsing_notes(self) -> None:
        """Test that BAML parser returns no parsing notes for clean input."""
        import os

        if os.environ.get("ENABLE_BAML", "false").lower() != "true":
            pytest.skip(
                "BAML integration test - requires ENABLE_BAML=true and real LLM calls"
            )

        from app.services.inventory_parser import BamlInventoryParserClient

        parser = BamlInventoryParserClient()

        # Test with only valid ingredients
        result = parser.parse_inventory_with_notes("2 apples, 1 banana")

        # Should extract both items
        assert len(result.items) == 2
        valid_names = [item.name for item in result.items]
        assert "apple" in valid_names
        assert "banana" in valid_names

        # Should have no parsing notes for clean input
        assert result.parsing_notes is None
