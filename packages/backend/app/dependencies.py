"""FastAPI dependency injection setup."""

import os
import tempfile
from typing import Annotated, Generator, Optional

from fastapi import Depends, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .infrastructure.event_bus import EventBusManager, InMemoryEventBus
from .infrastructure.event_store import EventStore
from .infrastructure.repositories import IngredientRepository, StoreRepository
from .infrastructure.view_stores import InventoryItemViewStore, StoreViewStore
from .interfaces.parser import InventoryParserProtocol
from .interfaces.repository import IngredientRepositoryProtocol, StoreRepositoryProtocol
from .interfaces.service import StoreServiceProtocol
from .interfaces.view_store import InventoryItemViewStoreProtocol, StoreViewStoreProtocol
from .projections.handlers import InventoryProjectionHandler, StoreProjectionHandler
from .projections.registry import ProjectionRegistry
from .services.inventory_parser import create_inventory_parser_client
from .services.store_service import StoreService

# Database setup for view stores
if os.getenv("PYTEST_CURRENT_TEST"):
    # For tests, use a temporary file that gets cleaned up
    temp_dir = tempfile.mkdtemp()
    DATABASE_URL = f"sqlite:///{temp_dir}/test_view_store.db"
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///view_store.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

# Projection registry and event bus manager will be stored in app state during startup
# Also keep global references for service layer access (temporary solution)
_app_state_projection_registry: Optional[ProjectionRegistry] = None
_app_state_event_bus_manager: Optional[EventBusManager] = None


def get_db_session() -> Generator[Session, None, None]:
    """Provide database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_inventory_parser() -> InventoryParserProtocol:
    """Provide inventory parser implementation."""
    # For testing, use the fixture-based mock parser
    # In production with ENABLE_BAML=true, this would use the real BAML client
    from tests.mocks.llm_service import MockLLMInventoryParser
    return MockLLMInventoryParser()


def get_store_view_store(
    session: Annotated[Session, Depends(get_db_session)]
) -> StoreViewStoreProtocol:
    """Provide store view store implementation."""
    return StoreViewStore(session)


def get_inventory_item_view_store(
    session: Annotated[Session, Depends(get_db_session)]
) -> InventoryItemViewStoreProtocol:
    """Provide inventory item view store implementation."""
    return InventoryItemViewStore(session)


def get_event_bus_manager(request: Request) -> EventBusManager:
    """Provide event bus manager implementation from app state."""
    return request.app.state.event_bus_manager  # type: ignore[no-any-return]


def get_projection_registry(request: Request) -> ProjectionRegistry:
    """Provide projection registry implementation from app state."""
    return request.app.state.projection_registry  # type: ignore[no-any-return]


def get_event_store(
    session: Annotated[Session, Depends(get_db_session)]
) -> EventStore:
    """Provide event store implementation with app state dependencies."""
    # Use only event bus now - projection registry is handled via event bus subscribers
    global _app_state_event_bus_manager
    
    return EventStore(
        session=session, 
        projection_registry=None,  # No longer using projection registry
        event_bus=_app_state_event_bus_manager.event_bus if _app_state_event_bus_manager else None
    )


def get_store_repository(
    event_store: Annotated[EventStore, Depends(get_event_store)]
) -> StoreRepositoryProtocol:
    """Provide store repository implementation."""
    return StoreRepository(event_store)


def get_ingredient_repository(
    event_store: Annotated[EventStore, Depends(get_event_store)]
) -> IngredientRepositoryProtocol:
    """Provide ingredient repository implementation."""
    return IngredientRepository(event_store)


def create_projection_registry(
    store_view_store: StoreViewStoreProtocol,
    inventory_item_view_store: InventoryItemViewStoreProtocol,
    store_repository: StoreRepositoryProtocol,
    ingredient_repository: IngredientRepositoryProtocol,
) -> ProjectionRegistry:
    """Create and configure projection registry with handlers."""
    registry = ProjectionRegistry()
    
    # Create handlers
    store_projection_handler = StoreProjectionHandler(store_view_store)
    inventory_projection_handler = InventoryProjectionHandler(
        ingredient_repository,
        store_repository,
        inventory_item_view_store
    )
    
    # Import event types for registration
    from .events.domain_events import IngredientCreated, InventoryItemAdded, StoreCreated
    
    # Register specific event handlers (ignoring async type mismatch as we're migrating away from this)
    registry.register(StoreCreated, store_projection_handler.handle_store_created)  # type: ignore[arg-type]
    registry.register(InventoryItemAdded, store_projection_handler.handle_inventory_item_added)  # type: ignore[arg-type]
    registry.register(InventoryItemAdded, inventory_projection_handler.handle_inventory_item_added)  # type: ignore[arg-type]
    registry.register(IngredientCreated, inventory_projection_handler.handle_ingredient_created)  # type: ignore[arg-type]
    
    return registry


def update_global_app_state(projection_registry: ProjectionRegistry, event_bus_manager: EventBusManager) -> None:
    """Update global app state references for service layer access."""
    global _app_state_projection_registry, _app_state_event_bus_manager
    _app_state_projection_registry = projection_registry
    _app_state_event_bus_manager = event_bus_manager


async def setup_event_bus_subscribers(
    event_bus_manager: EventBusManager,
    store_view_store: StoreViewStoreProtocol,
    inventory_item_view_store: InventoryItemViewStoreProtocol,
    store_repository: StoreRepositoryProtocol,
    ingredient_repository: IngredientRepositoryProtocol,
) -> None:
    """Subscribe projection handlers to event bus."""
    event_bus = event_bus_manager.event_bus
    
    # Create handlers
    store_projection_handler = StoreProjectionHandler(store_view_store)
    inventory_projection_handler = InventoryProjectionHandler(
        ingredient_repository,
        store_repository,
        inventory_item_view_store
    )
    
    # Import event types for subscription
    from .events.domain_events import IngredientCreated, InventoryItemAdded, StoreCreated
    
    # Subscribe handlers to event bus
    await event_bus.subscribe(StoreCreated, store_projection_handler.handle_store_created)  # type: ignore[arg-type]
    await event_bus.subscribe(InventoryItemAdded, store_projection_handler.handle_inventory_item_added)  # type: ignore[arg-type]
    await event_bus.subscribe(InventoryItemAdded, inventory_projection_handler.handle_inventory_item_added)  # type: ignore[arg-type]
    await event_bus.subscribe(IngredientCreated, inventory_projection_handler.handle_ingredient_created)  # type: ignore[arg-type]


def get_store_service(
    store_repository: Annotated[StoreRepositoryProtocol, Depends(get_store_repository)],
    ingredient_repository: Annotated[IngredientRepositoryProtocol, Depends(get_ingredient_repository)],
    inventory_parser: Annotated[InventoryParserProtocol, Depends(get_inventory_parser)],
    store_view_store: Annotated[StoreViewStoreProtocol, Depends(get_store_view_store)],
    inventory_item_view_store: Annotated[InventoryItemViewStoreProtocol, Depends(get_inventory_item_view_store)],
) -> StoreServiceProtocol:
    """Provide store service implementation."""
    return StoreService(
        store_repository,
        ingredient_repository,
        inventory_parser,
        store_view_store,
        inventory_item_view_store,
    )