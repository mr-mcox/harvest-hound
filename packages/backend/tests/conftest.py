"""Shared test configuration and fixtures."""

from typing import Any, Dict, Generator
from uuid import UUID

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient

from api import app
from app.dependencies import get_inventory_parser, get_store_service
from app.interfaces.parser import InventoryParserProtocol
from app.interfaces.service import StoreServiceProtocol
from app.models.parsed_inventory import ParsedInventoryItem
from tests.implementations.parser import MockInventoryParser
from tests.implementations.service import MockStoreService


@pytest.fixture
def mock_inventory_parser() -> MockInventoryParser:
    """Provide a mock inventory parser with standard fixtures."""
    return MockInventoryParser({
        "2 lbs carrots, 1 bunch kale": [
            ParsedInventoryItem(name="carrot", quantity=2.0, unit="pound"),
            ParsedInventoryItem(name="kale", quantity=1.0, unit="bunch"),
        ],
        "3.5 oz organic spinach, 2.25 cups whole milk, 1/2 cup olive oil": [
            ParsedInventoryItem(name="spinach", quantity=3.5, unit="ounce"),
            ParsedInventoryItem(name="milk", quantity=2.25, unit="cup"),
            ParsedInventoryItem(name="olive oil", quantity=0.5, unit="cup"),
        ],
        "1 apple": [
            ParsedInventoryItem(name="apple", quantity=1.0, unit="piece"),
        ],
    })


@pytest.fixture
def mock_store_service() -> MockStoreService:
    """Provide a mock store service."""
    return MockStoreService()


@pytest.fixture
def test_client_with_mocks(
    mock_inventory_parser: MockInventoryParser
) -> Generator[TestClient, None, None]:
    """Provide test client with parser mocked, but using real store service."""
    
    def override_inventory_parser() -> InventoryParserProtocol:
        return mock_inventory_parser
    
    app.dependency_overrides[get_inventory_parser] = override_inventory_parser
    
    # Manually trigger startup to initialize projection registry
    from app.dependencies import SessionLocal, engine
    from app.infrastructure.view_stores import InventoryItemViewStore, StoreViewStore
    from app.infrastructure.event_store import EventStore
    from app.infrastructure.repositories import IngredientRepository, StoreRepository
    from app.dependencies import setup_projection_registry
    from app.infrastructure.database import metadata
    
    # Create tables if they don't exist
    metadata.create_all(bind=engine)
    
    # Set up projection registry
    session = SessionLocal()
    try:
        event_store = EventStore(session=session, projection_registry=None)
        store_view_store = StoreViewStore(session)
        inventory_item_view_store = InventoryItemViewStore(session)
        store_repository = StoreRepository(event_store)
        ingredient_repository = IngredientRepository(event_store)
        
        setup_projection_registry(
            event_store,
            store_view_store,
            inventory_item_view_store,
            store_repository,
            ingredient_repository
        )
        session.commit()
    finally:
        session.close()
    
    client = TestClient(app)
    yield client
    
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_store_data() -> Dict[str, Any]:
    """Standard store data for testing."""
    return {
        "name": "Test CSA Box",
        "description": "Test store for integration testing",
        "infinite_supply": False
    }


@pytest.fixture
def standard_inventory_text() -> str:
    """Standard inventory text for testing."""
    return "2 lbs carrots, 1 bunch kale"


@pytest.fixture
def created_store_id(
    test_client_with_mocks: TestClient,
    sample_store_data: Dict[str, Any]
) -> UUID:
    """Create a store and return its ID."""
    response = test_client_with_mocks.post("/stores", json=sample_store_data)
    assert response.status_code == 201
    return UUID(response.json()["store_id"])