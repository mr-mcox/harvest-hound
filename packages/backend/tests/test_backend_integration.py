"""Backend integration tests with real database and full HTTP request/response cycle."""

from unittest.mock import patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api import app
from app.infrastructure.event_store import EventStore
from app.infrastructure.repositories import IngredientRepository, StoreRepository
from app.infrastructure.database import metadata
from app.infrastructure.view_stores import InventoryItemViewStore, StoreViewStore
from app.services.store_service import StoreService
from tests.mocks.llm_service import ConfigurableMockLLMParser, MockLLMInventoryParser


class TestBackendIntegrationWithRealDatabase:
    """Integration tests using real SQLite database and full HTTP stack."""
    
    @pytest.fixture
    def db_session(self):
        """Create isolated test database session."""
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        yield session
        
        session.close()
    
    @pytest.fixture 
    def integration_client(self, db_session):
        """Create test client with real database and dependency injection."""
        # Create fresh event store with temporary database
        event_store = EventStore(session=db_session)
        store_repository = StoreRepository(event_store)
        ingredient_repository = IngredientRepository(event_store)
        
        # Create view stores
        store_view_store = StoreViewStore(session=db_session)
        inventory_item_view_store = InventoryItemViewStore(session=db_session)
        
        # Use mocked LLM for predictable testing
        mock_parser = MockLLMInventoryParser()
        store_service = StoreService(
            store_repository, 
            ingredient_repository, 
            mock_parser,
            store_view_store,
            inventory_item_view_store
        )
        
        # Override app dependencies for testing
        with patch('api.store_service', store_service):
            client = TestClient(app)
            yield client
    
    def test_complete_store_workflow_with_real_database(self, integration_client):
        """Test complete workflow: create store → upload inventory → query data with real database persistence."""
        client = integration_client
        
        # Create store
        store_response = client.post("/stores", json={
            "name": "Integration Test CSA",
            "description": "Test store for integration testing",
            "infinite_supply": False
        })
        assert store_response.status_code == 201
        store_data = store_response.json()
        store_id = store_data["store_id"]
        
        # Verify store creation
        assert UUID(store_id)  # Valid UUID
        assert store_data["name"] == "Integration Test CSA"
        assert store_data["description"] == "Test store for integration testing"
        assert store_data["infinite_supply"] is False
        
        # Upload inventory using mocked LLM (matches fixture pattern)
        upload_response = client.post(f"/stores/{store_id}/inventory", json={
            "inventory_text": "2 lbs carrots, 1 bunch kale"
        })
        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        assert upload_data["items_added"] == 2
        assert upload_data["success"] is True
        assert upload_data["errors"] == []
        
        # Verify inventory retrieval
        inventory_response = client.get(f"/stores/{store_id}/inventory")
        assert inventory_response.status_code == 200
        inventory_items = inventory_response.json()
        assert len(inventory_items) == 2
        
        # Verify data structure and content with denormalized fields
        carrot_item = next(item for item in inventory_items if "carrot" in item["ingredient_name"].lower())
        assert carrot_item["quantity"] == 2.0
        assert carrot_item["unit"] == "pound"
        assert carrot_item["store_name"] == "Integration Test CSA"
        assert "store_id" in carrot_item
        assert "ingredient_id" in carrot_item
        
        kale_item = next(item for item in inventory_items if "kale" in item["ingredient_name"].lower())
        assert kale_item["quantity"] == 1.0
        assert kale_item["unit"] == "bunch"
        assert kale_item["store_name"] == "Integration Test CSA"
        assert "store_id" in kale_item
        assert "ingredient_id" in kale_item
        
        # Verify store list includes new store with correct item count
        stores_response = client.get("/stores")
        assert stores_response.status_code == 200
        stores = stores_response.json()
        
        created_store = next(store for store in stores if store["store_id"] == store_id)
        assert created_store["name"] == "Integration Test CSA"
        assert created_store["item_count"] == 2
    
    def test_multiple_stores_maintain_separate_inventories(self, integration_client):
        """Test that multiple stores maintain separate inventories in the database."""
        client = integration_client
        
        # Create two stores
        store1_response = client.post("/stores", json={"name": "Store One"})
        store2_response = client.post("/stores", json={"name": "Store Two"})
        
        store1_id = store1_response.json()["store_id"]
        store2_id = store2_response.json()["store_id"]
        
        # Add different inventory to each store
        client.post(f"/stores/{store1_id}/inventory", json={
            "inventory_text": "2 lbs carrots, 1 bunch kale"
        })
        client.post(f"/stores/{store2_id}/inventory", json={
            "inventory_text": "3.5 oz organic spinach, 2.25 cups whole milk, 1/2 cup olive oil"
        })
        
        # Verify each store has its own inventory
        store1_inventory = client.get(f"/stores/{store1_id}/inventory").json()
        store2_inventory = client.get(f"/stores/{store2_id}/inventory").json()
        
        assert len(store1_inventory) == 2
        assert len(store2_inventory) == 3
        
        # Verify store list shows correct item counts
        stores_response = client.get("/stores").json()
        store1_data = next(s for s in stores_response if s["store_id"] == store1_id)
        store2_data = next(s for s in stores_response if s["store_id"] == store2_id)
        
        assert store1_data["item_count"] == 2
        assert store2_data["item_count"] == 3
    
    def test_database_persistence_across_requests(self, integration_client):
        """Test that data persists in the database across multiple HTTP requests."""
        client = integration_client
        
        # Create store and add inventory
        store_response = client.post("/stores", json={"name": "Persistence Test"})
        store_id = store_response.json()["store_id"]
        
        client.post(f"/stores/{store_id}/inventory", json={
            "inventory_text": "1 apple"
        })
        
        # Make multiple separate requests to verify persistence
        for _ in range(3):
            inventory_response = client.get(f"/stores/{store_id}/inventory")
            assert inventory_response.status_code == 200
            inventory = inventory_response.json()
            assert len(inventory) == 1
            assert inventory[0]["ingredient_name"] == "apple"
            assert inventory[0]["store_name"] == "Persistence Test"
            assert "store_id" in inventory[0]
            assert "ingredient_id" in inventory[0]
        
        # Add more inventory
        client.post(f"/stores/{store_id}/inventory", json={
            "inventory_text": "2 lbs carrots, 1 bunch kale"
        })
        
        # Verify cumulative inventory
        final_inventory = client.get(f"/stores/{store_id}/inventory").json()
        assert len(final_inventory) == 3  # apple + carrot + kale


class TestBackendIntegrationErrorHandling:
    """Test error handling in backend integration scenarios."""
    
    @pytest.fixture
    def error_test_client(self):
        """Create test client with configurable mock for error testing."""
        mock_parser = ConfigurableMockLLMParser()
        
        with patch('api.inventory_parser', mock_parser):
            yield TestClient(app), mock_parser
    
    def test_inventory_upload_with_parsing_errors(self, error_test_client):
        """Test error handling when LLM parsing fails."""
        client, mock_parser = error_test_client
        
        # Configure mock to raise parsing error
        mock_parser.set_response("invalid inventory", [])
        
        # Create store
        store_response = client.post("/stores", json={"name": "Error Test Store"})
        store_id = store_response.json()["store_id"]
        
        # Attempt upload with text that triggers parsing error
        upload_response = client.post(f"/stores/{store_id}/inventory", json={
            "inventory_text": "invalid inventory"
        })
        
        # Should succeed but add 0 items
        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        assert upload_data["items_added"] == 0
        assert upload_data["success"] is True
    
    def test_upload_to_nonexistent_store(self, error_test_client):
        """Test error handling when uploading to non-existent store."""
        client, _ = error_test_client
        
        # Try to upload to non-existent store
        fake_store_id = "00000000-0000-0000-0000-000000000000"
        upload_response = client.post(f"/stores/{fake_store_id}/inventory", json={
            "inventory_text": "1 apple"
        })
        
        assert upload_response.status_code == 404
        error_data = upload_response.json()
        assert "not found" in error_data["detail"].lower()
    
    def test_invalid_store_creation_data(self, error_test_client):
        """Test validation errors during store creation."""
        client, _ = error_test_client
        
        # Try to create store with missing name
        response = client.post("/stores", json={})
        assert response.status_code == 422  # Validation error
        
        # Try to create store with empty name
        response = client.post("/stores", json={"name": ""})
        assert response.status_code == 422


class TestBackendIntegrationPerformance:
    """Test performance characteristics of backend integration."""
    
    @pytest.fixture
    def performance_client(self):
        """Create test client optimized for performance testing."""
        # Use in-memory SQLite for fastest possible database operations
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        event_store = EventStore(session=session)
        store_repository = StoreRepository(event_store)
        ingredient_repository = IngredientRepository(event_store)
        
        # Create view stores
        store_view_store = StoreViewStore(session=session)
        inventory_item_view_store = InventoryItemViewStore(session=session)
        
        # Use fast mock without timing simulation
        mock_parser = MockLLMInventoryParser(simulate_timing=False)
        store_service = StoreService(
            store_repository, 
            ingredient_repository, 
            mock_parser,
            store_view_store,
            inventory_item_view_store
        )
        
        with patch('api.store_service', store_service):
            yield TestClient(app)
    
    def test_rapid_store_creation_performance(self, performance_client):
        """Test performance of rapid store creation."""
        client = performance_client
        
        import time
        start_time = time.time()
        
        # Create multiple stores rapidly
        store_ids = []
        for i in range(10):
            response = client.post("/stores", json={"name": f"Performance Store {i}"})
            assert response.status_code == 201
            store_ids.append(response.json()["store_id"])
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Should complete reasonably quickly (allowing for overhead)
        assert elapsed < 2.0  # 10 stores in under 2 seconds
        
        # Verify all stores were created
        stores_response = client.get("/stores")
        stores = stores_response.json()
        assert len(stores) == 10
    
    def test_batch_inventory_upload_performance(self, performance_client):
        """Test performance of batch inventory uploads."""
        client = performance_client
        
        # Create store
        store_response = client.post("/stores", json={"name": "Batch Test Store"})
        store_id = store_response.json()["store_id"]
        
        import time
        start_time = time.time()
        
        # Upload inventory multiple times
        for i in range(5):
            response = client.post(f"/stores/{store_id}/inventory", json={
                "inventory_text": f"1 apple{i}"  # Each upload adds unique items
            })
            assert response.status_code == 201
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Should complete quickly with mocked LLM
        assert elapsed < 1.0  # 5 uploads in under 1 second
        
        # Verify all items were added
        inventory_response = client.get(f"/stores/{store_id}/inventory")
        inventory = inventory_response.json()
        assert len(inventory) == 5


class TestBackendIntegrationEventSourcing:
    """Test event sourcing behavior in backend integration scenarios."""
    
    @pytest.fixture
    def event_test_client(self):
        """Create test client that allows inspection of event store."""
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        event_store = EventStore(session=session)
        store_repository = StoreRepository(event_store)
        ingredient_repository = IngredientRepository(event_store)
        
        # Create view stores
        store_view_store = StoreViewStore(session=session)
        inventory_item_view_store = InventoryItemViewStore(session=session)
        
        mock_parser = MockLLMInventoryParser()
        store_service = StoreService(
            store_repository, 
            ingredient_repository, 
            mock_parser,
            store_view_store,
            inventory_item_view_store
        )
        
        with patch('api.store_service', store_service):
            yield TestClient(app), event_store
    
    def test_events_are_persisted_during_workflow(self, event_test_client):
        """Test that domain events are properly persisted during API operations."""
        client, event_store = event_test_client
        
        # Create store
        store_response = client.post("/stores", json={"name": "Event Test Store"})
        store_id = UUID(store_response.json()["store_id"])
        
        # Add inventory
        client.post(f"/stores/{store_id}/inventory", json={
            "inventory_text": "2 lbs carrots, 1 bunch kale"
        })
        
        # Verify events were stored
        events = event_store.get_events(store_id)
        assert len(events) >= 3  # StoreCreated + 2 InventoryItemAdded (minimum)
        
        # Verify event types
        event_types = [event.__class__.__name__ for event in events]
        assert "StoreCreated" in event_types
        assert "InventoryItemAdded" in event_types
    
    def test_store_reconstruction_from_events(self, event_test_client):
        """Test that stores can be reconstructed from persisted events."""
        client, event_store = event_test_client
        
        # Create store and add inventory through API
        store_response = client.post("/stores", json={
            "name": "Reconstruction Test",
            "description": "Test store reconstruction",
            "infinite_supply": True
        })
        store_id = UUID(store_response.json()["store_id"])
        
        client.post(f"/stores/{store_id}/inventory", json={
            "inventory_text": "2 lbs carrots, 1 bunch kale"
        })
        
        # Retrieve events and reconstruct store
        events = event_store.get_events(store_id)
        
        from app.models.inventory_store import InventoryStore
        reconstructed_store = InventoryStore.from_events(events)
        
        # Verify reconstruction matches original
        assert reconstructed_store.store_id == store_id
        assert reconstructed_store.name == "Reconstruction Test"
        assert reconstructed_store.description == "Test store reconstruction"
        assert reconstructed_store.infinite_supply is True
        assert len(reconstructed_store.inventory_items) == 2