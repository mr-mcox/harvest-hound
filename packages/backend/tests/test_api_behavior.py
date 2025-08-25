import asyncio
from typing import Generator, List
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from api import _startup_completed, app, startup_event
from app.dependencies import get_inventory_parser
from app.interfaces.parser import InventoryParserProtocol
from app.models.parsed_inventory import ParsedInventoryItem
from app.services.inventory_parser import MockInventoryParserClient


@pytest.fixture(scope="function")  # Changed to function scope for better isolation
def client() -> Generator[TestClient, None, None]:
    """Create test client with proper startup initialization."""
    # Clear any existing dependency overrides from previous tests
    app.dependency_overrides.clear()
    
    # TestClient with app will automatically trigger startup event
    # which initializes projection registry and event bus in app state
    client = TestClient(app)
    
    # Manually trigger startup event if needed (TestClient sometimes doesn't)
    if not _startup_completed:
        asyncio.run(startup_event())
        
    yield client
    
    # Clean up after each test
    app.dependency_overrides.clear()


class TestStoreCreation:
    """Test POST /stores endpoint behavior."""

    def test_create_store_with_valid_data_returns_201_with_store_details(self, client: TestClient) -> None:
        """Test that POST /stores with valid data returns 201 with store details."""
        # Given
        store_data = {"name": "CSA Box"}

        # When
        response = client.post("/stores", json=store_data)

        # Then
        assert response.status_code == 201
        response_data = response.json()

        # Should return a valid store with generated UUID
        assert "store_id" in response_data
        assert UUID(response_data["store_id"])  # Should be valid UUID
        assert response_data["name"] == "CSA Box"
        assert response_data["description"] == ""
        assert response_data["infinite_supply"] is False

        # Store should be persisted and retrievable
        stores_response = client.get("/stores")
        assert stores_response.status_code == 200
        stores = stores_response.json()

        # Should find our created store in the list
        created_store = next(
            (
                store
                for store in stores
                if store["store_id"] == response_data["store_id"]
            ),
            None,
        )
        assert created_store is not None
        assert created_store["name"] == "CSA Box"
        assert created_store["item_count"] == 0

    def test_create_store_with_missing_name_returns_400_validation_error(self, client: TestClient) -> None:
        """Test that POST /stores with missing name returns 400 validation error."""
        # Given
        store_data = {"description": "Missing name field"}

        # When
        response = client.post("/stores", json=store_data)

        # Then
        assert response.status_code == 422  # FastAPI returns 422 for validation errors
        response_data = response.json()

        # Should have validation error details
        assert "detail" in response_data
        errors = response_data["detail"]
        assert len(errors) > 0

        # Should specifically mention the missing name field
        name_error = next(
            (error for error in errors if error["loc"] == ["body", "name"]),
            None,
        )
        assert name_error is not None
        assert name_error["type"] == "missing"

    def test_create_store_with_inventory_text_returns_201_with_unified_creation_results(self, client: TestClient) -> None:
        """Test that POST /stores with inventory_text returns 201 with unified creation results."""
        # Given - Configure mock inventory parser to return 2 parsed items
        def mock_inventory_parser() -> InventoryParserProtocol:
            parser = MockInventoryParserClient()
            parser.mock_results = [
                ParsedInventoryItem(name="carrots", quantity=2.0, unit="pound"),
                ParsedInventoryItem(name="kale", quantity=1.0, unit="bunch"),
            ]
            return parser

        # Override dependency for this test
        app.dependency_overrides[get_inventory_parser] = mock_inventory_parser
        
        try:
            store_data = {
                "name": "CSA Box",
                "description": "Fresh vegetables",
                "inventory_text": "2 lbs carrots\n1 bunch kale"
            }

            # When
            response = client.post("/stores", json=store_data)

            # Then
            assert response.status_code == 201
            response_data = response.json()

            # Should return a valid store with generated UUID
            assert "store_id" in response_data
            assert UUID(response_data["store_id"])  # Should be valid UUID
            assert response_data["name"] == "CSA Box"
            assert response_data["description"] == "Fresh vegetables"
            assert response_data["infinite_supply"] is False
            
            # Should include unified creation results from inventory processing
            assert response_data["successful_items"] == 2  # carrots + kale
            assert response_data["error_message"] is None
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

        # Store should be persisted with inventory
        stores_response = client.get("/stores")
        assert stores_response.status_code == 200
        stores = stores_response.json()

        # Should find our created store in the list with correct item count
        created_store = next(
            (
                store
                for store in stores
                if store["store_id"] == response_data["store_id"]
            ),
            None,
        )
        assert created_store is not None
        assert created_store["name"] == "CSA Box"
        assert created_store["item_count"] == 2  # Should have 2 inventory items

        # Verify actual inventory was added
        store_id = response_data["store_id"]
        inventory_response = client.get(f"/stores/{store_id}/inventory")
        assert inventory_response.status_code == 200
        inventory_items = inventory_response.json()
        assert len(inventory_items) == 2

    def test_create_store_with_problematic_inventory_returns_201_with_partial_success_results(self, client: TestClient) -> None:
        """Test that POST /stores with problematic inventory returns 201 with partial success results."""
        # Given - Configure mock inventory parser to return valid items with parsing notes about problems
        def mock_inventory_parser() -> InventoryParserProtocol:
            parser = MockInventoryParserClient()
            parser.mock_results = [
                ParsedInventoryItem(name="carrots", quantity=2.0, unit="pound"),
                ParsedInventoryItem(name="kale", quantity=1.0, unit="bunch"),
            ]
            parser.mock_parsing_notes = "Found problematic items: 'Volvo car' is not a food ingredient"
            return parser

        # Override dependency for this test
        app.dependency_overrides[get_inventory_parser] = mock_inventory_parser
        
        try:
            store_data = {
                "name": "CSA Box",
                "inventory_text": "2 lbs carrots\n1 Volvo car\n1 bunch kale"  # Mix of valid and invalid items
            }

            # When
            response = client.post("/stores", json=store_data)

            # Then
            assert response.status_code == 201
            response_data = response.json()

            # Should return a valid store 
            assert "store_id" in response_data
            assert UUID(response_data["store_id"])
            assert response_data["name"] == "CSA Box"
            
            # Should include partial success results
            assert response_data["successful_items"] == 2  # carrots + kale (Volvo filtered out)
            assert response_data["error_message"] is not None  # Should mention problematic items
            assert "volvo" in response_data["error_message"].lower() or "car" in response_data["error_message"].lower()

            # Store should be created with only valid inventory
            store_id = response_data["store_id"]
            inventory_response = client.get(f"/stores/{store_id}/inventory")
            assert inventory_response.status_code == 200
            inventory_items = inventory_response.json()
            assert len(inventory_items) == 2  # Only valid items added
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    def test_create_store_without_inventory_text_returns_201_with_unified_results(self, client: TestClient) -> None:
        """Test that POST /stores without inventory_text returns 201 with unified results showing no inventory processed."""
        # Given
        store_data = {"name": "CSA Box"}

        # When
        response = client.post("/stores", json=store_data)

        # Then
        assert response.status_code == 201
        response_data = response.json()

        # Should return a valid store with standard fields
        assert "store_id" in response_data
        assert UUID(response_data["store_id"])
        assert response_data["name"] == "CSA Box"
        assert response_data["description"] == ""
        assert response_data["infinite_supply"] is False
        
        # Should always include unified creation results (even when no inventory processed)
        assert response_data["successful_items"] == 0  # No inventory provided, so 0 items processed
        assert response_data["error_message"] is None


class TestStoreList:
    """Test GET /stores endpoint behavior."""

    def test_get_stores_returns_list_of_all_stores_with_item_counts(self, client: TestClient) -> None:
        """Test that GET /stores returns list of all stores with item counts."""
        # Given - Create multiple stores
        store1_data = {"name": "CSA Box", "description": "Fresh vegetables"}
        store2_data = {
            "name": "Pantry",
            "description": "Dry goods",
            "infinite_supply": True,
        }

        store1_response = client.post("/stores", json=store1_data)
        store2_response = client.post("/stores", json=store2_data)

        assert store1_response.status_code == 201
        assert store2_response.status_code == 201

        store1_id = store1_response.json()["store_id"]
        store2_id = store2_response.json()["store_id"]

        # When
        response = client.get("/stores")

        # Then
        assert response.status_code == 200
        stores = response.json()

        # Should be a list with at least our 2 stores
        assert isinstance(stores, list)
        assert len(stores) >= 2

        # Find our created stores
        created_store1 = next(
            (store for store in stores if store["store_id"] == store1_id),
            None,
        )
        created_store2 = next(
            (store for store in stores if store["store_id"] == store2_id),
            None,
        )

        # Both stores should be found
        assert created_store1 is not None
        assert created_store2 is not None

        # Verify store1 details
        assert created_store1["name"] == "CSA Box"
        assert created_store1["description"] == "Fresh vegetables"
        assert created_store1["item_count"] == 0

        # Verify store2 details
        assert created_store2["name"] == "Pantry"
        assert created_store2["description"] == "Dry goods"
        assert created_store2["item_count"] == 0

        # Each store should have the required fields
        for store in [created_store1, created_store2]:
            assert "store_id" in store
            assert "name" in store
            assert "description" in store
            assert "item_count" in store
            assert isinstance(store["item_count"], int)


class TestInventoryUpload:
    """Test POST /stores/{id}/inventory endpoint HTTP behavior."""

    def test_upload_inventory_with_valid_text_returns_201_success_response(
        self, client: TestClient
    ) -> None:
        """Test POST /stores/{id}/inventory with valid text returns 201 with success structure."""
        # Given - Create a store first
        store_data = {"name": "Test Store"}
        store_response = client.post("/stores", json=store_data)
        assert store_response.status_code == 201
        store_id = store_response.json()["store_id"]
        
        # Configure mock parser to return 1 parsed item
        def mock_inventory_parser() -> InventoryParserProtocol:
            parser = MockInventoryParserClient()
            parser.mock_results = [
                ParsedInventoryItem(name="test_item", quantity=1.0, unit="count"),
            ]
            return parser
        
        app.dependency_overrides[get_inventory_parser] = mock_inventory_parser
        
        try:
            # When - Upload inventory
            inventory_data = {"inventory_text": "test inventory text"}
            response = client.post(f"/stores/{store_id}/inventory", json=inventory_data)

            # Then - Focus on HTTP behavior and response structure
            assert response.status_code == 201
            response_data = response.json()

            # Should have success response structure
            assert response_data["success"] is True
            assert response_data["items_added"] == 1
            assert response_data["errors"] == []
        finally:
            app.dependency_overrides.clear()

    def test_upload_inventory_with_parsing_failure_returns_400_error_response(
        self, client: TestClient
    ) -> None:
        """Test POST /stores/{id}/inventory returns 400 with proper error structure when parsing fails."""
        # Given - Create a store first
        store_data = {"name": "Test Store"}
        store_response = client.post("/stores", json=store_data)
        assert store_response.status_code == 201
        store_id = store_response.json()["store_id"]
        
        # Configure mock parser to simulate complete parsing failure
        def failing_mock_parser() -> InventoryParserProtocol:
            class FailingParser(MockInventoryParserClient):
                def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
                    raise Exception("Simulated parsing failure")
            return FailingParser()
        
        app.dependency_overrides[get_inventory_parser] = failing_mock_parser
        
        try:
            # When - Upload inventory that will fail parsing
            inventory_data = {"inventory_text": "invalid unparseable text"}
            response = client.post(f"/stores/{store_id}/inventory", json=inventory_data)

            # Then - Should return 400 with proper error structure
            assert response.status_code == 400
            response_data = response.json()

            # HTTPException with detail containing the error response
            assert "detail" in response_data
            error_detail = response_data["detail"]

            # Should have error response structure
            assert error_detail["success"] is False
            assert error_detail["items_added"] == 0
            assert len(error_detail["errors"]) > 0
            assert isinstance(error_detail["errors"][0], str)
        finally:
            app.dependency_overrides.clear()


class TestInventoryRetrieval:
    """Test GET /stores/{id}/inventory endpoint HTTP behavior."""

    def test_get_store_inventory_returns_200_with_proper_json_structure(self, client: TestClient) -> None:
        """Test GET /stores/{id}/inventory returns 200 with proper JSON structure."""
        # Given - Create a store and add minimal inventory for testing structure
        store_data = {"name": "Test Store"}
        store_response = client.post("/stores", json=store_data)
        assert store_response.status_code == 201
        store_id = store_response.json()["store_id"]

        # Add one inventory item using configured mock
        def mock_inventory_parser() -> InventoryParserProtocol:
            parser = MockInventoryParserClient()
            parser.mock_results = [
                ParsedInventoryItem(name="test_item", quantity=1.0, unit="count"),
            ]
            return parser
        
        app.dependency_overrides[get_inventory_parser] = mock_inventory_parser
        
        try:
            # Add inventory via POST (minimal setup)
            inventory_data = {"inventory_text": "test item"}
            post_response = client.post(f"/stores/{store_id}/inventory", json=inventory_data)
            assert post_response.status_code == 201  # Ensure setup worked

            # When - Get store inventory
            response = client.get(f"/stores/{store_id}/inventory")

            # Then - Focus on HTTP behavior and response structure
            assert response.status_code == 200
            inventory_items = response.json()

            # Should return array with proper item structure
            assert isinstance(inventory_items, list)
            assert len(inventory_items) == 1
            
            # Verify required fields exist (focus on structure, not content)
            item = inventory_items[0]
            required_fields = [
                "ingredient_name", "quantity", "unit", "store_name", 
                "store_id", "ingredient_id", "added_at", "notes"
            ]
            for field in required_fields:
                assert field in item, f"Missing required field: {field}"
            
            # Basic type validation
            assert isinstance(item["quantity"], (int, float))
            assert isinstance(item["ingredient_name"], str)
            assert isinstance(item["unit"], str)
        finally:
            app.dependency_overrides.clear()

    def test_upload_inventory_to_non_existent_store_returns_404(self, client: TestClient) -> None:
        """Test that POST inventory to non-existent store returns 404."""
        # Given - A non-existent store ID
        non_existent_store_id = uuid4()

        # When - Try to upload inventory to non-existent store
        inventory_data = {"inventory_text": "2 lbs carrots"}
        response = client.post(
            f"/stores/{non_existent_store_id}/inventory", json=inventory_data
        )

        # Then - Should return 404
        assert response.status_code == 404
        response_data = response.json()
        assert "detail" in response_data
        assert isinstance(response_data["detail"], str)
