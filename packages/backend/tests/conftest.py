"""Shared test configuration and fixtures."""

from typing import Any, Dict, Generator
from uuid import UUID

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient

from api import app
from app.dependencies import get_inventory_parser
from app.interfaces.parser import InventoryParserProtocol
from app.models.parsed_inventory import ParsedInventoryItem
from tests.implementations.parser import MockInventoryParser


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
def test_client_with_mocks(
    mock_inventory_parser: MockInventoryParser
) -> Generator[TestClient, None, None]:
    """Provide test client with parser mocked, but using real store service."""
    
    def override_inventory_parser() -> InventoryParserProtocol:
        return mock_inventory_parser
    
    app.dependency_overrides[get_inventory_parser] = override_inventory_parser
    
    # TestClient with app will automatically trigger startup event
    # which initializes projection registry and event bus in app state
    client = TestClient(app)
    
    # Manually trigger startup event if needed (TestClient sometimes doesn't)
    import asyncio
    from api import startup_event, _startup_completed
    if not _startup_completed:
        asyncio.run(startup_event())
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