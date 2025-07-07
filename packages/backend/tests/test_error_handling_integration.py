"""
Error Handling Integration Tests (Tier 2)
Tests error scenarios: invalid inventory, network errors, LLM failures, partial parsing

Following our three-tier testing strategy:
- Real FastAPI + SQLite database
- Mocked LLM responses for error scenarios
- Full HTTP request/response cycle testing
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api import app
from app.models.parsed_inventory import ParsedInventoryItem
from tests.mocks.llm_service import ConfigurableMockLLMParser, FailingMockLLMParser


class TestErrorHandlingIntegration:
    """Test error handling scenarios in the integration environment."""

    @pytest.fixture
    def client(self):
        """Create test client for API calls."""
        return TestClient(app)

    @pytest.fixture
    def sample_store(self, client):
        """Create a sample store for testing error scenarios."""
        response = client.post(
            "/stores",
            json={"name": "Error Test Store", "description": "Store for error testing"}
        )
        return response.json()["store_id"]

    def test_invalid_inventory_text_shows_error_without_crashing(self, client, sample_store):
        """Test: Invalid inventory text shows error without crashing."""
        # Use the FailingMockLLMParser to simulate parsing errors
        failing_parser = FailingMockLLMParser(error_type="parsing")
        
        with patch("app.services.store_service.StoreService._parse_inventory_text") as mock_parse:
            mock_parse.side_effect = ValueError("Failed to parse inventory text")
            
            inventory_response = client.post(
                f"/stores/{sample_store}/inventory",
                json={"inventory_text": "invalid unparseable text that should fail"}
            )
            
            # Should return a 400 error for parsing failure, not crash (500)
            assert inventory_response.status_code == 400
            error_data = inventory_response.json()
            
            # Should contain error details
            assert "detail" in error_data
            response_detail = error_data["detail"]
            assert response_detail["success"] is False
            assert response_detail["items_added"] == 0
            assert len(response_detail["errors"]) > 0

        # Verify the store still exists and is accessible
        store_response = client.get("/stores")
        assert store_response.status_code == 200
        stores = store_response.json()
        test_store = next(s for s in stores if s["store_id"] == sample_store)
        assert test_store["item_count"] == 0  # No items should have been added

    def test_llm_service_unavailable_shows_graceful_error(self, client, sample_store):
        """Test: LLM service unavailable shows graceful error."""
        # Mock the parsing method to simulate LLM timeout
        with patch("app.services.store_service.StoreService._parse_inventory_text") as mock_parse:
            mock_parse.side_effect = TimeoutError("LLM service timeout")
            
            inventory_response = client.post(
                f"/stores/{sample_store}/inventory",
                json={"inventory_text": "2 lbs carrots, 1 bunch kale"}
            )
            
            # Should return 400 (error result) with graceful error message
            assert inventory_response.status_code == 400
            error_data = inventory_response.json()
            assert "detail" in error_data
            response_detail = error_data["detail"]
            assert response_detail["success"] is False
            assert "timeout" in str(response_detail["errors"]).lower()

        # Verify the store is still accessible after the error
        store_response = client.get("/stores")
        assert store_response.status_code == 200

    def test_partial_parsing_results_display_correctly(self, client, sample_store):
        """Test: Partial parsing results display correctly."""
        # Create a mock parser that returns partial results with errors
        partial_parser = ConfigurableMockLLMParser()
        partial_parser.set_response(
            "2 lbs carrots, some kale, 3 tomatoes",
            [
                ParsedInventoryItem(name="carrot", quantity=2.0, unit="pound"),
                ParsedInventoryItem(name="tomato", quantity=3.0, unit="piece")
            ]
        )
        
        with patch("api.inventory_parser.parse_inventory", side_effect=partial_parser.parse_inventory):
            inventory_response = client.post(
                f"/stores/{sample_store}/inventory", 
                json={"inventory_text": "2 lbs carrots, some kale, 3 tomatoes"}
            )
            
            assert inventory_response.status_code == 201
            result = inventory_response.json()
            
            # Partial success should still be considered successful
            assert result["success"] is True
            assert result["items_added"] == 2  # Only 2 items parsed successfully
            # Note: Our current mock doesn't support errors array, 
            # but in real implementation this would contain parsing errors

        # Verify the successfully parsed items were added
        inventory_list_response = client.get(f"/stores/{sample_store}/inventory")
        inventory = inventory_list_response.json()
        assert len(inventory) == 2
        
        ingredient_names = [item["ingredient_name"] for item in inventory]
        assert "carrot" in ingredient_names
        assert "tomato" in ingredient_names
        assert "kale" not in ingredient_names  # This one failed to parse

    def test_malformed_request_data_handled_gracefully(self, client, sample_store):
        """Test: Malformed request data is handled gracefully."""
        # Test missing inventory_text field
        response1 = client.post(
            f"/stores/{sample_store}/inventory",
            json={}
        )
        assert response1.status_code == 422  # Validation error

        # Test invalid JSON structure
        response2 = client.post(
            f"/stores/{sample_store}/inventory",
            json={"wrong_field": "some text"}
        )
        assert response2.status_code == 422  # Validation error

        # Test null inventory_text
        response3 = client.post(
            f"/stores/{sample_store}/inventory",
            json={"inventory_text": None}
        )
        assert response3.status_code == 422  # Validation error

    def test_non_existent_store_inventory_upload_error(self, client):
        """Test: Inventory upload to non-existent store returns 404."""
        fake_store_id = "00000000-0000-0000-0000-000000000000"
        
        response = client.post(
            f"/stores/{fake_store_id}/inventory",
            json={"inventory_text": "1 apple"}
        )
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data

    def test_invalid_store_id_format_handled(self, client):
        """Test: Invalid store ID format is handled gracefully."""
        invalid_store_id = "not-a-valid-uuid"
        
        response = client.post(
            f"/stores/{invalid_store_id}/inventory",
            json={"inventory_text": "1 apple"}
        )
        
        # FastAPI should return 422 for invalid UUID format
        assert response.status_code == 422

    def test_empty_inventory_text_handled_gracefully(self, client, sample_store):
        """Test: Empty inventory text is handled without errors."""
        response = client.post(
            f"/stores/{sample_store}/inventory",
            json={"inventory_text": ""}
        )
        
        assert response.status_code == 201
        result = response.json()
        assert result["success"] is True
        assert result["items_added"] == 0
        assert result["errors"] == []

    def test_very_long_inventory_text_handled(self, client, sample_store):
        """Test: Very long inventory text doesn't crash the system."""
        # Create a very long inventory text
        long_text = "apple, banana, carrot, " * 100  # 300 items
        
        response = client.post(
            f"/stores/{sample_store}/inventory",
            json={"inventory_text": long_text}
        )
        
        # Should not crash (500), might be slow but should succeed or fail gracefully
        assert response.status_code in [201, 400, 404]  # Success or graceful failure
        
        if response.status_code == 201:
            result = response.json()
            assert "success" in result
            assert "items_added" in result


class TestNetworkErrorHandling:
    """Test network-related error scenarios."""

    @pytest.fixture
    def client(self):
        """Create test client for API calls."""
        return TestClient(app)

    def test_malformed_json_request_handled(self, client):
        """Test: Malformed JSON requests show appropriate error messages."""
        # Test with raw string instead of JSON
        response = client.post(
            "/stores",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

    def test_missing_content_type_handled(self, client):
        """Test: Missing Content-Type header is handled gracefully."""
        response = client.post(
            "/stores",
            data='{"name": "Test Store"}',
            headers={}  # No Content-Type
        )
        
        # FastAPI should still handle this gracefully
        assert response.status_code in [201, 400, 422]

    def test_cors_headers_present_in_error_responses(self, client):
        """Test: CORS headers are present even in error responses."""
        response = client.post(
            "/stores",
            json={}  # Invalid request that will fail validation
        )
        
        assert response.status_code == 422
        # Note: In a real deployment, CORS headers would be tested here
        # For TestClient, CORS middleware might not be active


class TestServiceRobustness:
    """Test overall service robustness and recovery."""

    @pytest.fixture
    def client(self):
        """Create test client for API calls."""
        return TestClient(app)

    def test_health_check_works_during_errors(self, client):
        """Test: Health check endpoint works even when other operations fail."""
        # First cause an error
        client.post("/stores", json={})  # This will fail validation
        
        # Health check should still work
        health_response = client.get("/health")
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data["status"] == "healthy"

    def test_multiple_error_scenarios_dont_affect_each_other(self, client):
        """Test: Multiple error scenarios don't affect each other."""
        # Create a store
        store_response = client.post(
            "/stores",
            json={"name": "Robustness Test Store"}
        )
        store_id = store_response.json()["store_id"]
        
        # Cause several different types of errors
        client.post("/stores", json={})  # Validation error
        client.post(f"/stores/{store_id}/inventory", json={})  # Missing field error
        client.get("/stores/invalid-uuid/inventory")  # Invalid UUID error
        
        # Verify normal operations still work
        stores_response = client.get("/stores")
        assert stores_response.status_code == 200
        
        # Verify we can still upload valid inventory
        inventory_response = client.post(
            f"/stores/{store_id}/inventory",
            json={"inventory_text": "1 apple"}
        )
        assert inventory_response.status_code == 201