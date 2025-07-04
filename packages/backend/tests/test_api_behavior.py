from uuid import UUID

from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


class TestStoreCreation:
    """Test POST /stores endpoint behavior."""

    def test_create_store_with_valid_data_returns_201_with_store_details(self) -> None:
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

    def test_create_store_with_missing_name_returns_400_validation_error(self) -> None:
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


class TestStoreList:
    """Test GET /stores endpoint behavior."""

    def test_get_stores_returns_list_of_all_stores_with_item_counts(self) -> None:
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
        self,
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

        # Should have correct details
        assert carrot_item["ingredient_name"] == "carrots"
        assert carrot_item["quantity"] == 2.0
        assert carrot_item["unit"] == "pound"
        assert "added_at" in carrot_item

    def test_upload_inventory_with_parsing_errors_returns_400(self) -> None:
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

    def test_get_store_inventory_returns_current_inventory_with_details(self) -> None:
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

        # Check carrots
        carrots_item = inventory_items[0]
        assert carrots_item["ingredient_name"] == "carrots"
        assert carrots_item["quantity"] == 2.0
        assert carrots_item["unit"] == "pound"
        assert carrots_item["notes"] is None
        assert "added_at" in carrots_item

        # Check kale
        kale_item = inventory_items[1]
        assert kale_item["ingredient_name"] == "kale"
        assert kale_item["quantity"] == 1.0
        assert kale_item["unit"] == "bunch"
        assert kale_item["notes"] is None
        assert "added_at" in kale_item

    def test_upload_inventory_to_non_existent_store_returns_404(self) -> None:
        """Test that POST inventory to non-existent store returns 404."""
        # Given - A non-existent store ID
        from uuid import uuid4

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
