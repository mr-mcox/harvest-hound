import asyncio
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from api import _startup_completed, app, startup_event
from app.dependencies import get_inventory_parser
from app.interfaces.parser import InventoryParserProtocol
from app.models.parsed_inventory import ParsedInventoryItem
from app.services.inventory_parser import MockInventoryParserClient


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Create test client with proper startup initialization."""
    # TestClient with app will automatically trigger startup event
    # which initializes projection registry and event bus in app state
    client = TestClient(app)
    
    # Manually trigger startup event if needed (TestClient sometimes doesn't)
    if not _startup_completed:
        asyncio.run(startup_event())
        
    return client


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

    def test_create_store_without_inventory_text_returns_201_with_no_unified_results(self, client: TestClient) -> None:
        """Test that POST /stores without inventory_text returns 201 with no unified results (backward compatibility)."""
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
        
        # Should NOT include unified creation results when no inventory provided
        assert response_data["successful_items"] is None
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
    """Test POST /stores/{id}/inventory endpoint behavior."""

    def test_upload_inventory_with_valid_text_returns_201_with_parsed_items(
        self, client: TestClient
    ) -> None:
        """Test that POST /stores/{id}/inventory with valid text returns 201."""
        # Given - Create a store first
        store_data = {"name": "Test Store"}
        store_response = client.post("/stores", json=store_data)
        assert store_response.status_code == 201
        store_id = store_response.json()["store_id"]

        # When - Upload inventory
        inventory_data = {"inventory_text": "2 lbs carrots"}
        response = client.post(f"/stores/{store_id}/inventory", json=inventory_data)

        # Then
        assert response.status_code == 201
        response_data = response.json()

        # Should indicate success and items added
        assert response_data["success"] is True
        assert response_data["items_added"] == 1
        assert response_data["errors"] == []

        # Verify inventory was actually added by checking store inventory
        inventory_response = client.get(f"/stores/{store_id}/inventory")
        assert inventory_response.status_code == 200
        inventory_items = inventory_response.json()

        # Should have 1 item
        assert len(inventory_items) == 1
        carrot_item = inventory_items[0]

        # Should have correct details with denormalized data (InventoryItemView structure)
        assert carrot_item["ingredient_name"] == "carrots"
        assert carrot_item["quantity"] == 2.0
        assert carrot_item["unit"] == "pound"
        assert "added_at" in carrot_item
        
        # Should include denormalized store information
        assert carrot_item["store_name"] == "Test Store"
        assert "store_id" in carrot_item
        assert carrot_item["store_id"] == store_id
        assert "ingredient_id" in carrot_item
        assert carrot_item["notes"] is None  # Default notes value

    def test_upload_inventory_with_parsing_errors_returns_400(self, client: TestClient) -> None:
        """Test that POST /stores/{id}/inventory returns 400 for parsing errors."""
        # Given - Create a store first
        store_data = {"name": "Test Store"}
        store_response = client.post("/stores", json=store_data)
        assert store_response.status_code == 201
        store_id = store_response.json()["store_id"]

        # When - Upload inventory with text that will cause parsing errors
        inventory_data = {"inventory_text": "invalid unparseable text"}
        response = client.post(f"/stores/{store_id}/inventory", json=inventory_data)

        # Then
        assert response.status_code == 400
        response_data = response.json()

        # HTTPException with detail containing the error response
        assert "detail" in response_data
        error_detail = response_data["detail"]

        # Should indicate failure and provide error details
        assert error_detail["success"] is False
        assert error_detail["items_added"] == 0
        assert len(error_detail["errors"]) > 0
        assert isinstance(error_detail["errors"][0], str)


class TestInventoryRetrieval:
    """Test GET /stores/{id}/inventory endpoint behavior."""

    def test_get_store_inventory_returns_current_inventory_with_details(self, client: TestClient) -> None:
        """Test that GET /stores/{id}/inventory returns current inventory."""
        # Given - Create a store and add some inventory
        store_data = {"name": "Test Store"}
        store_response = client.post("/stores", json=store_data)
        assert store_response.status_code == 201
        store_id = store_response.json()["store_id"]

        # Add carrots to inventory
        carrots_data = {"inventory_text": "2 lbs carrots"}
        carrots_response = client.post(
            f"/stores/{store_id}/inventory", json=carrots_data
        )
        assert carrots_response.status_code == 201

        # Add kale to inventory
        kale_data = {"inventory_text": "1 bunch kale"}
        kale_response = client.post(f"/stores/{store_id}/inventory", json=kale_data)
        assert kale_response.status_code == 201

        # When - Get store inventory
        response = client.get(f"/stores/{store_id}/inventory")

        # Then
        assert response.status_code == 200
        inventory_items = response.json()

        # Should have 2 items
        assert len(inventory_items) == 2

        # Sort by ingredient name for consistent testing
        inventory_items.sort(key=lambda x: x["ingredient_name"])

        # Check carrots with denormalized data (InventoryItemView structure)
        carrots_item = inventory_items[0]
        assert carrots_item["ingredient_name"] == "carrots"
        assert carrots_item["quantity"] == 2.0
        assert carrots_item["unit"] == "pound"
        assert carrots_item["notes"] is None
        assert "added_at" in carrots_item
        assert carrots_item["store_name"] == "Test Store"
        assert "store_id" in carrots_item
        assert "ingredient_id" in carrots_item

        # Check kale with denormalized data (InventoryItemView structure)
        kale_item = inventory_items[1]
        assert kale_item["ingredient_name"] == "kale"
        assert kale_item["quantity"] == 1.0
        assert kale_item["unit"] == "bunch"
        assert kale_item["notes"] is None
        assert "added_at" in kale_item
        assert kale_item["store_name"] == "Test Store"
        assert "store_id" in kale_item
        assert "ingredient_id" in kale_item

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
