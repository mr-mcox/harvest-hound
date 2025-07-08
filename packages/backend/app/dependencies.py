"""FastAPI dependency injection setup."""

import os
import tempfile
from typing import Annotated, Generator

from fastapi import Depends, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .events.domain_events import (
    IngredientCreated,
    InventoryItemAdded,
    StoreCreated,
)
from .infrastructure.event_bus import EventBusManager
from .infrastructure.event_publisher import EventPublisher
from .infrastructure.event_store import EventStore
from .infrastructure.repositories import IngredientRepository, StoreRepository
from .infrastructure.view_stores import InventoryItemViewStore, StoreViewStore
from .infrastructure.websocket_manager import ConnectionManager
from .interfaces.parser import InventoryParserProtocol
from .interfaces.repository import IngredientRepositoryProtocol, StoreRepositoryProtocol
from .interfaces.service import StoreServiceProtocol
from .interfaces.view_store import (
    InventoryItemViewStoreProtocol,
    StoreViewStoreProtocol,
)
from .projections.handlers import InventoryProjectionHandler, StoreProjectionHandler
from .projections.registry import ProjectionRegistry
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

# All dependencies now managed through FastAPI app state - no global variables


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


def get_connection_manager(request: Request) -> ConnectionManager:
    """Provide connection manager implementation from app state."""
    return request.app.state.connection_manager  # type: ignore[no-any-return]


def get_event_store(
    session: Annotated[Session, Depends(get_db_session)]
) -> EventStore:
    """Provide event store implementation."""
    return EventStore(session=session)


def get_event_publisher(request: Request) -> EventPublisher:
    """Provide event publisher implementation from app state."""
    event_bus_manager = request.app.state.event_bus_manager
    return EventPublisher(event_bus_manager.event_bus if event_bus_manager else None)


def get_store_repository(
    event_store: Annotated[EventStore, Depends(get_event_store)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)]
) -> StoreRepositoryProtocol:
    """Provide store repository implementation."""
    return StoreRepository(event_store, event_publisher)


def get_ingredient_repository(
    event_store: Annotated[EventStore, Depends(get_event_store)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)]
) -> IngredientRepositoryProtocol:
    """Provide ingredient repository implementation."""
    return IngredientRepository(event_store, event_publisher)


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
    
    
    # Register specific event handlers
    registry.register(StoreCreated, store_projection_handler.handle_store_created)
    registry.register(InventoryItemAdded, store_projection_handler.handle_inventory_item_added)
    registry.register(InventoryItemAdded, inventory_projection_handler.handle_inventory_item_added)
    registry.register(IngredientCreated, inventory_projection_handler.handle_ingredient_created)
    
    return registry




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
    
    
    # Subscribe handlers to event bus
    await event_bus.subscribe(StoreCreated, store_projection_handler.handle_store_created)
    await event_bus.subscribe(InventoryItemAdded, store_projection_handler.handle_inventory_item_added)
    await event_bus.subscribe(InventoryItemAdded, inventory_projection_handler.handle_inventory_item_added)
    await event_bus.subscribe(IngredientCreated, inventory_projection_handler.handle_ingredient_created)


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