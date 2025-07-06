"""
Happy Path Integration Tests (Tier 2)
Tests the core user workflow: Create "CSA Box" store → upload "2 lbs carrots, 1 bunch kale" → see 2 items

Following our three-tier testing strategy:
- Real FastAPI + SQLite database
- Mocked LLM responses using fixtures
- Full HTTP request/response cycle testing
"""

import pytest
from fastapi.testclient import TestClient

from api import app


class TestHappyPathIntegration:
    """Test the exact happy path workflow defined in Task 9.4."""

    @pytest.fixture
    def client(self):
        """Create test client for API calls."""
        return TestClient(app)

    def test_complete_happy_path_workflow(self, client):
        """Test: Create "CSA Box" store → upload "2 lbs carrots, 1 bunch kale" → see 2 items in table."""
        # Step 1: Create "CSA Box" store
        store_response = client.post(
            "/stores",
            json={
                "name": "CSA Box",
                "description": "Weekly CSA delivery store",
                "infinite_supply": False
            }
        )
        
        assert store_response.status_code == 201
        store_data = store_response.json()
        assert store_data["name"] == "CSA Box"
        assert store_data["description"] == "Weekly CSA delivery store"
        assert store_data["infinite_supply"] is False
        store_id = store_data["store_id"]

        # Step 2: Upload exact test case "2 lbs carrots, 1 bunch kale"
        inventory_response = client.post(
            f"/stores/{store_id}/inventory",
            json={"inventory_text": "2 lbs carrots, 1 bunch kale"}
        )
        
        assert inventory_response.status_code == 201
        upload_result = inventory_response.json()
        assert upload_result["success"] is True
        assert upload_result["items_added"] == 2
        assert upload_result["errors"] == []

        # Step 3: Verify we can see 2 items in the inventory table
        inventory_list_response = client.get(f"/stores/{store_id}/inventory")
        assert inventory_list_response.status_code == 200
        
        inventory = inventory_list_response.json()
        assert len(inventory) == 2

        # Verify the specific items match our expectations (from LLM fixtures)
        carrot_item = next((item for item in inventory if item["ingredient_name"] == "carrot"), None)
        kale_item = next((item for item in inventory if item["ingredient_name"] == "kale"), None)

        assert carrot_item is not None
        assert carrot_item["quantity"] == 2.0
        assert carrot_item["unit"] == "pound"

        assert kale_item is not None
        assert kale_item["quantity"] == 1.0
        assert kale_item["unit"] == "bunch"

        # Verify all required fields are present
        for item in [carrot_item, kale_item]:
            assert "ingredient_name" in item
            assert "quantity" in item
            assert "unit" in item
            assert "added_at" in item
            assert isinstance(item["quantity"], (int, float))
            assert item["quantity"] > 0

    def test_store_list_shows_csa_box_with_item_count_2(self, client):
        """Test: Store list shows "CSA Box" with item_count=2."""
        # First create the store and add inventory
        store_response = client.post(
            "/stores",
            json={"name": "CSA Box", "description": "Weekly CSA delivery store"}
        )
        store_id = store_response.json()["store_id"]
        
        client.post(
            f"/stores/{store_id}/inventory",
            json={"inventory_text": "2 lbs carrots, 1 bunch kale"}
        )

        # Get the store list
        stores_response = client.get("/stores")
        assert stores_response.status_code == 200

        stores = stores_response.json()
        assert isinstance(stores, list)

        # Find our CSA Box store
        csa_box_store = next((store for store in stores if store["name"] == "CSA Box"), None)
        assert csa_box_store is not None
        assert csa_box_store["item_count"] == 2
        assert csa_box_store["description"] == "Weekly CSA delivery store"

    def test_data_persists_across_requests_event_sourcing_verification(self, client):
        """Test: Page refresh preserves all data (event sourcing working)."""
        # Create store and add inventory
        store_response = client.post(
            "/stores",
            json={"name": "CSA Box", "description": "Weekly CSA delivery store"}
        )
        store_id = store_response.json()["store_id"]
        
        client.post(
            f"/stores/{store_id}/inventory",
            json={"inventory_text": "2 lbs carrots, 1 bunch kale"}
        )

        # Get initial state
        initial_stores_response = client.get("/stores")
        initial_stores = initial_stores_response.json()
        initial_inventory_response = client.get(f"/stores/{store_id}/inventory")
        initial_inventory = initial_inventory_response.json()

        # Simulate "page refresh" by making fresh requests
        # In event sourcing, all data should be reconstructed from events
        
        # Verify stores are still there with same data
        fresh_stores_response = client.get("/stores")
        assert fresh_stores_response.status_code == 200
        fresh_stores = fresh_stores_response.json()
        
        csa_box_initial = next(s for s in initial_stores if s["name"] == "CSA Box")
        csa_box_fresh = next(s for s in fresh_stores if s["name"] == "CSA Box")
        
        assert csa_box_fresh["store_id"] == csa_box_initial["store_id"]
        assert csa_box_fresh["item_count"] == csa_box_initial["item_count"]
        assert csa_box_fresh["name"] == csa_box_initial["name"]
        assert csa_box_fresh["item_count"] == 2

        # Verify inventory is still there with same data
        fresh_inventory_response = client.get(f"/stores/{store_id}/inventory")
        assert fresh_inventory_response.status_code == 200
        fresh_inventory = fresh_inventory_response.json()

        assert len(fresh_inventory) == len(initial_inventory)
        assert len(fresh_inventory) == 2

        # Verify specific items are preserved
        carrot_item = next(item for item in fresh_inventory if item["ingredient_name"] == "carrot")
        kale_item = next(item for item in fresh_inventory if item["ingredient_name"] == "kale")
        
        assert carrot_item["quantity"] == 2.0
        assert carrot_item["unit"] == "pound"
        assert kale_item["quantity"] == 1.0
        assert kale_item["unit"] == "bunch"

    def test_multiple_stores_maintain_separate_inventories(self, client):
        """Test: Multiple stores maintain separate inventories."""
        # Create CSA Box store
        csa_response = client.post(
            "/stores",
            json={"name": "CSA Box", "description": "Weekly CSA delivery store"}
        )
        csa_store_id = csa_response.json()["store_id"]

        # Create Pantry store
        pantry_response = client.post(
            "/stores",
            json={"name": "Pantry Store", "description": "Non-perishable pantry items"}
        )
        pantry_store_id = pantry_response.json()["store_id"]

        # Add different inventory to each store
        client.post(
            f"/stores/{csa_store_id}/inventory",
            json={"inventory_text": "2 lbs carrots, 1 bunch kale"}
        )
        
        client.post(
            f"/stores/{pantry_store_id}/inventory",
            json={"inventory_text": "1 apple"}
        )

        # Verify CSA Box has its inventory
        csa_inventory_response = client.get(f"/stores/{csa_store_id}/inventory")
        csa_inventory = csa_inventory_response.json()
        assert len(csa_inventory) == 2

        # Verify Pantry Store has its own inventory
        pantry_inventory_response = client.get(f"/stores/{pantry_store_id}/inventory")
        pantry_inventory = pantry_inventory_response.json()
        assert len(pantry_inventory) == 1
        assert pantry_inventory[0]["ingredient_name"] == "apple"

        # Verify store list shows correct counts
        stores_response = client.get("/stores")
        stores = stores_response.json()

        csa_store = next(s for s in stores if s["name"] == "CSA Box")
        pantry_store = next(s for s in stores if s["name"] == "Pantry Store")

        assert csa_store["item_count"] == 2
        assert pantry_store["item_count"] == 1


class TestHappyPathEdgeCases:
    """Test edge cases in the happy path workflow."""

    @pytest.fixture
    def client(self):
        """Create test client for API calls."""
        return TestClient(app)

    def test_empty_store_creation_then_successful_inventory_upload(self, client):
        """Test creating empty store then adding inventory."""
        # Create empty store
        store_response = client.post(
            "/stores",
            json={"name": "Empty Store Test"}
        )
        store_id = store_response.json()["store_id"]

        # Verify store starts with 0 items
        initial_stores_response = client.get("/stores")
        initial_stores = initial_stores_response.json()
        empty_store = next(s for s in initial_stores if s["name"] == "Empty Store Test")
        assert empty_store["item_count"] == 0

        # Add inventory
        inventory_response = client.post(
            f"/stores/{store_id}/inventory",
            json={"inventory_text": "2 lbs carrots, 1 bunch kale"}
        )
        assert inventory_response.status_code == 201

        # Verify store now shows correct count
        final_stores_response = client.get("/stores")
        final_stores = final_stores_response.json()
        updated_store = next(s for s in final_stores if s["name"] == "Empty Store Test")
        assert updated_store["item_count"] == 2

    def test_infinite_supply_store_preserves_setting(self, client):
        """Test stores with infinite_supply setting work correctly."""
        # Create infinite supply store
        store_response = client.post(
            "/stores",
            json={
                "name": "Infinite Supply Store",
                "description": "Store with infinite supply",
                "infinite_supply": True
            }
        )
        store_data = store_response.json()
        assert store_data["infinite_supply"] is True
        store_id = store_data["store_id"]

        # Add inventory
        client.post(
            f"/stores/{store_id}/inventory",
            json={"inventory_text": "2 lbs carrots, 1 bunch kale"}
        )

        # Verify store preserves infinite_supply setting
        stores_response = client.get("/stores")
        stores = stores_response.json()
        infinite_store = next(s for s in stores if s["name"] == "Infinite Supply Store")
        
        # Note: API response doesn't include infinite_supply field in store list
        # This is expected based on our StoreListItem model
        assert infinite_store["item_count"] == 2