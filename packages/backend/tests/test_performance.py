"""Performance tests for Harvest Hound backend."""

import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api import app
from tests.mocks.llm_service import MockLLMInventoryParser


@pytest.fixture
def performance_client():
    """Create a test client with mocked LLM for performance testing."""
    # Mock the LLM service for consistent performance
    mock_parser = MockLLMInventoryParser()
    
    with patch('api.create_inventory_parser_client', return_value=mock_parser):
        yield TestClient(app)


class TestPerformanceRequirements:
    """Test performance requirements for the application."""
    
    def test_store_creation_completes_in_under_1_second(self, performance_client):
        """Test that store creation completes in under 1 second."""
        start_time = time.time()
        
        response = performance_client.post("/stores", json={"name": "Test Store"})
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert response.status_code == 201
        assert duration < 1.0, f"Store creation took {duration:.3f}s, expected < 1.0s"
    
    def test_mocked_llm_parsing_completes_in_under_100ms(self, performance_client):
        """Test that mocked LLM parsing completes in under 100ms (baseline)."""
        # First create a store
        store_response = performance_client.post("/stores", json={"name": "Test Store"})
        store_id = store_response.json()["store_id"]
        
        start_time = time.time()
        
        response = performance_client.post(
            f"/stores/{store_id}/inventory",
            json={"inventory_text": "2 lbs carrots, 1 bunch kale"}
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert response.status_code == 201
        assert duration < 0.1, f"LLM parsing took {duration:.3f}s, expected < 0.1s"
    
    def test_inventory_display_loads_in_under_2_seconds(self, performance_client):
        """Test that inventory display loads in under 2 seconds."""
        # First create a store and add some inventory
        store_response = performance_client.post("/stores", json={"name": "Test Store"})
        store_id = store_response.json()["store_id"]
        
        performance_client.post(
            f"/stores/{store_id}/inventory",
            json={"inventory_text": "2 lbs carrots, 1 bunch kale, 3 tomatoes, 1 cup rice"}
        )
        
        start_time = time.time()
        
        response = performance_client.get(f"/stores/{store_id}/inventory")
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert response.status_code == 200
        assert duration < 2.0, f"Inventory display took {duration:.3f}s, expected < 2.0s"
    
    def test_concurrent_store_creation_handles_10_simultaneous_requests(self, performance_client):
        """Test that concurrent store creation handles 10 simultaneous requests."""
        def create_store(index):
            response = performance_client.post("/stores", json={"name": f"Store {index}"})
            return response.status_code, response.json()
        
        start_time = time.time()
        
        # Use ThreadPoolExecutor to simulate concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_store, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        duration = end_time - start_time
        
        # All requests should succeed
        status_codes = [result[0] for result in results]
        assert all(code == 201 for code in status_codes), f"Not all requests succeeded: {status_codes}"
        
        # Should complete within reasonable time (5 seconds for 10 concurrent requests)
        assert duration < 5.0, f"Concurrent store creation took {duration:.3f}s, expected < 5.0s"
        
        # Verify all stores were created with unique names
        store_names = [result[1]["name"] for result in results]
        assert len(set(store_names)) == 10, "Not all stores were created with unique names"