from typing import Generator
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.events.domain_events import StoreCreated, StoreCreatedWithInventory
from app.infrastructure.database import metadata
from app.infrastructure.event_bus import InMemoryEventBus
from app.infrastructure.event_publisher import EventPublisher
from app.infrastructure.event_store import EventStore
from app.infrastructure.repositories import IngredientRepository, StoreRepository
from app.infrastructure.view_stores import InventoryItemViewStore, StoreViewStore
from app.services.inventory_parser import MockInventoryParserClient
from app.services.store_creation_orchestrator import StoreCreationOrchestrator, OrchestrationResult
from app.services.store_service import StoreService
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
def event_store(db_session: Session) -> EventStore:
    """Create an EventStore instance for testing."""
    return EventStore(session=db_session)


@pytest.fixture
def event_publisher(shared_event_bus: InMemoryEventBus) -> EventPublisher:
    """Create an EventPublisher for testing.""" 
    return EventPublisher(shared_event_bus)


@pytest.fixture
def store_repository(event_store: EventStore, event_publisher: EventPublisher) -> StoreRepository:
    """Create a StoreRepository for testing."""
    return StoreRepository(event_store, event_publisher)


@pytest.fixture
def ingredient_repository(event_store: EventStore, event_publisher: EventPublisher) -> IngredientRepository:
    """Create an IngredientRepository for testing."""
    return IngredientRepository(event_store, event_publisher)


@pytest.fixture
def store_view_store(db_session: Session) -> StoreViewStore:
    """Create a StoreViewStore for testing."""
    return StoreViewStore(session=db_session)


@pytest.fixture
def inventory_item_view_store(db_session: Session) -> InventoryItemViewStore:
    """Create an InventoryItemViewStore for testing."""
    return InventoryItemViewStore(session=db_session)


@pytest.fixture
def inventory_parser() -> MockInventoryParserClient:
    """Create mock inventory parser for testing."""
    return MockInventoryParserClient()


@pytest.fixture
def store_service(
    store_repository: StoreRepository,
    ingredient_repository: IngredientRepository,
    inventory_parser: MockInventoryParserClient,
    store_view_store: StoreViewStore,
    inventory_item_view_store: InventoryItemViewStore,
) -> StoreService:
    """Create a StoreService for testing."""
    return StoreService(
        store_repository, 
        ingredient_repository, 
        inventory_parser,
        store_view_store,
        inventory_item_view_store
    )


@pytest.fixture
def orchestrator(store_service: StoreService) -> StoreCreationOrchestrator:
    """Create a StoreCreationOrchestrator for testing."""
    return StoreCreationOrchestrator(store_service)


class TestUnifiedCreationLogic:
    """Test unified store creation with optional inventory processing."""

    def test_create_store_without_inventory_calls_store_service_and_returns_result(
        self, orchestrator: StoreCreationOrchestrator, event_store: EventStore
    ) -> None:
        """Test that creating store without inventory text calls StoreService.create_store and returns proper result."""
        # Act
        result = orchestrator.create_store_with_inventory(
            name="CSA Box",
            description="Weekly vegetable box", 
            infinite_supply=False,
            inventory_text=None
        )
        
        # Assert
        assert isinstance(result, OrchestrationResult)
        assert isinstance(result.store_id, UUID)
        assert result.successful_items == 0
        assert result.error_message is None
        
        # Verify StoreCreated event was persisted
        store_events = get_typed_events(event_store, f"store-{result.store_id}", StoreCreated)
        assert len(store_events) == 1
        assert_event_matches(
            store_events[0],
            {
                "store_id": result.store_id,
                "name": "CSA Box",
                "description": "Weekly vegetable box",
                "infinite_supply": False,
            }
        )

    def test_create_store_with_inventory_processes_items_and_emits_orchestration_event(
        self, orchestrator: StoreCreationOrchestrator, event_store: EventStore
    ) -> None:
        """Test that creating store with inventory text processes items and emits StoreCreatedWithInventory event."""
        # Act
        result = orchestrator.create_store_with_inventory(
            name="CSA Box",
            description="Weekly vegetable box",
            infinite_supply=False,
            inventory_text="2 apples\n3 bananas"
        )
        
        # Assert  
        assert isinstance(result, OrchestrationResult)
        assert isinstance(result.store_id, UUID)
        assert result.successful_items == 2  # Mock parser returns 2 items
        assert result.error_message is None
        
        # Verify StoreCreatedWithInventory event was persisted
        orchestration_events = get_typed_events(event_store, f"orchestration-{result.store_id}", StoreCreatedWithInventory)
        assert len(orchestration_events) == 1
        assert_event_matches(
            orchestration_events[0],
            {
                "store_id": result.store_id,
                "successful_items": 2,
                "error_message": None,
            }
        )

    def test_create_store_with_failing_inventory_returns_error_in_result(
        self, orchestrator: StoreCreationOrchestrator, event_store: EventStore
    ) -> None:
        """Test that inventory processing failures are captured in result with simple error message."""
        # Act - using invalid inventory text that will cause parsing failure
        result = orchestrator.create_store_with_inventory(
            name="CSA Box",
            description="Weekly vegetable box",
            infinite_supply=False,
            inventory_text="invalid inventory format that causes error"
        )
        
        # Assert - store still created successfully, but with error message
        assert isinstance(result, OrchestrationResult) 
        assert isinstance(result.store_id, UUID)
        assert result.successful_items == 0
        assert result.error_message is not None
        assert "error" in result.error_message.lower()
        
        # Verify store was still created
        store_events = get_typed_events(event_store, f"store-{result.store_id}", StoreCreated)
        assert len(store_events) == 1
        
        # Verify orchestration event includes error message
        orchestration_events = get_typed_events(event_store, f"orchestration-{result.store_id}", StoreCreatedWithInventory)
        assert len(orchestration_events) == 1
        assert orchestration_events[0].error_message is not None