"""Integration tests with mocked LLM service for predictable testing."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app
from app.models.parsed_inventory import ParsedInventoryItem
from tests.mocks.llm_service import (
    ConfigurableMockLLMParser,
    FailingMockLLMParser,
    MockLLMInventoryParser,
)

client = TestClient(app)


class TestFullWorkflowWithMockedLLM:
    """Test complete API workflow using mocked LLM responses."""

    def test_create_store_and_upload_inventory_with_predictable_parsing(
        self
    ) -> None:
        """Test full workflow: create store → upload inventory → verify parsed results."""
        # Given - Using fixture-based MockLLMInventoryParser for predictable results

        # When - Create store
        store_response = client.post("/stores", json={"name": "Test CSA Box"})
        assert store_response.status_code == 201
        store_data = store_response.json()
        store_id = store_data["store_id"]

        # When - Upload inventory text that matches fixture
        inventory_text = "2 lbs carrots, 1 bunch kale"
        upload_response = client.post(
            f"/stores/{store_id}/inventory", json={"inventory_text": inventory_text}
        )

        # Then - Should parse successfully using fixture data
        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        assert upload_data["items_added"] == 2

        # Then - Verify inventory contains parsed items
        inventory_response = client.get(f"/stores/{store_id}/inventory")
        assert inventory_response.status_code == 200
        inventory_items = inventory_response.json()

        assert len(inventory_items) == 2
        
        # Verify carrots (using denormalized structure, values from fixture)
        carrots = next(item for item in inventory_items if "carrot" in item["ingredient_name"].lower())
        assert carrots["quantity"] == 2.0
        assert carrots["unit"] == "pound"  # From fixture: "pound", not "lbs"
        assert carrots["store_name"] == "Test CSA Box"  # Verify denormalized data
        
        # Verify kale (using denormalized structure, values from fixture)
        kale = next(item for item in inventory_items if "kale" in item["ingredient_name"].lower())
        assert kale["quantity"] == 1.0
        assert kale["unit"] == "bunch"
        assert kale["store_name"] == "Test CSA Box"  # Verify denormalized data

    def test_complex_inventory_parsing_with_fixture_data(self) -> None:
        """Test parsing complex inventory using fixture responses."""
        # Given - Using fixture-based MockLLMInventoryParser for predictable results

        # Create store
        store_response = client.post("/stores", json={"name": "Complex Store"})
        store_id = store_response.json()["store_id"]

        # When - Upload complex inventory (matches fixture)
        complex_text = "3.5 oz organic spinach, 2.25 cups whole milk, 1/2 cup olive oil"
        upload_response = client.post(
            f"/stores/{store_id}/inventory", json={"inventory_text": complex_text}
        )

        # Then
        assert upload_response.status_code == 201
        assert upload_response.json()["items_added"] == 3

        inventory_response = client.get(f"/stores/{store_id}/inventory")
        inventory_items = inventory_response.json()
        assert len(inventory_items) == 3

        # Verify fractional quantities are handled correctly (using denormalized structure)
        spinach = next(item for item in inventory_items if "spinach" in item["ingredient_name"].lower())
        assert spinach["quantity"] == 3.5

        milk = next(item for item in inventory_items if "milk" in item["ingredient_name"].lower())
        assert milk["quantity"] == 2.25

        oil = next(item for item in inventory_items if "oil" in item["ingredient_name"].lower())
        assert oil["quantity"] == 0.5


class TestErrorHandlingWithMockedLLM:
    """Test error scenarios using mocked LLM failures."""

    @patch("api.inventory_parser.parse_inventory")
    def test_llm_service_timeout_returns_appropriate_error(self, mock_parse_inventory) -> None:
        """Test handling of LLM service timeouts."""
        # Given - Mock LLM that simulates timeout
        failing_parser = FailingMockLLMParser(error_type="timeout")
        mock_parse_inventory.side_effect = failing_parser.parse_inventory

        # Create store
        store_response = client.post("/stores", json={"name": "Test Store"})
        store_id = store_response.json()["store_id"]

        # When - Try to upload inventory
        upload_response = client.post(
            f"/stores/{store_id}/inventory", 
            json={"inventory_text": "2 lbs carrots"}
        )

        # Then - Should return 400 with timeout error (service treats LLM errors as parsing failures)
        assert upload_response.status_code == 400
        error_data = upload_response.json()
        assert "timeout" in error_data["detail"]["errors"][0].lower()

    @patch("api.inventory_parser.parse_inventory")
    def test_llm_parsing_error_returns_400_with_details(self, mock_parse_inventory) -> None:
        """Test handling of LLM parsing errors."""
        # Given
        failing_parser = FailingMockLLMParser(error_type="parsing")
        mock_parse_inventory.side_effect = failing_parser.parse_inventory

        # Create store
        store_response = client.post("/stores", json={"name": "Test Store"})
        store_id = store_response.json()["store_id"]

        # When
        upload_response = client.post(
            f"/stores/{store_id}/inventory", 
            json={"inventory_text": "invalid text"}
        )

        # Then
        assert upload_response.status_code == 400
        error_data = upload_response.json()
        assert "parse" in error_data["detail"]["errors"][0].lower()

    @patch("api.inventory_parser.parse_inventory")
    def test_empty_parsing_result_returns_success_with_zero_items(self, mock_parse_inventory) -> None:
        """Test handling when LLM returns empty results."""
        # Given - Mock to return empty results
        mock_parse_inventory.return_value = []

        # Create store
        store_response = client.post("/stores", json={"name": "Test Store"})
        store_id = store_response.json()["store_id"]

        # When - Upload text that results in empty parsing (matches fixture)
        upload_response = client.post(
            f"/stores/{store_id}/inventory", 
            json={"inventory_text": "Lorem ipsum dolor sit amet"}
        )

        # Then
        assert upload_response.status_code == 201
        assert upload_response.json()["items_added"] == 0


class TestPerformanceWithMockedLLM:
    """Test performance characteristics using mocked LLM with timing simulation."""

    @patch("app.services.inventory_parser.create_inventory_parser_client")
    def test_fast_parsing_completes_quickly(self, mock_parser_factory) -> None:
        """Test fast mocked responses complete in reasonable time."""
        # Given
        mock_parser = MockLLMInventoryParser(simulate_timing=True)
        mock_parser_factory.return_value = mock_parser

        # Create store
        store_response = client.post("/stores", json={"name": "Performance Store"})
        store_id = store_response.json()["store_id"]

        # When - Upload simple text (fast fixture: 50ms simulated)
        import time
        start_time = time.time()
        
        upload_response = client.post(
            f"/stores/{store_id}/inventory", 
            json={"inventory_text": "1 apple"}
        )
        
        end_time = time.time()
        elapsed = end_time - start_time

        # Then - Should complete reasonably quickly (allowing overhead)
        assert upload_response.status_code == 201
        assert elapsed < 1.0  # Should be much faster than real LLM

    @patch("api.inventory_parser.parse_inventory")
    def test_batch_processing_handles_multiple_requests(self, mock_parse_inventory) -> None:
        """Test multiple concurrent parsing requests."""
        # Given - Mock to return consistent results
        mock_parse_inventory.return_value = [
            ParsedInventoryItem(name="test item", quantity=1.0, unit="piece")
        ]

        # Create multiple stores
        store_ids = []
        for i in range(3):
            store_response = client.post("/stores", json={"name": f"Store {i}"})
            store_ids.append(store_response.json()["store_id"])

        # When - Upload to all stores
        upload_responses = []
        for store_id in store_ids:
            response = client.post(
                f"/stores/{store_id}/inventory", 
                json={"inventory_text": f"test input {store_id}"}
            )
            upload_responses.append(response)

        # Then - All should succeed
        for response in upload_responses:
            assert response.status_code == 201
            assert response.json()["items_added"] == 1


class TestConfigurableMockScenarios:
    """Test specific scenarios using configurable mock responses."""

    @patch("api.inventory_parser.parse_inventory")
    def test_custom_parsing_scenario(self, mock_parse_inventory) -> None:
        """Test specific parsing scenario with custom mock configuration."""
        # Given - Configure specific response
        mock_parse_inventory.return_value = [
            ParsedInventoryItem(name="cilantro", quantity=2.0, unit="bunches"),
            ParsedInventoryItem(name="limes", quantity=3.0, unit="pieces"),
        ]

        # Create store
        store_response = client.post("/stores", json={"name": "Custom Store"})
        store_id = store_response.json()["store_id"]

        # When - Upload the configured text
        upload_response = client.post(
            f"/stores/{store_id}/inventory", 
            json={"inventory_text": "2 bunches cilantro, 3 limes"}
        )

        # Then
        assert upload_response.status_code == 201
        assert upload_response.json()["items_added"] == 2

        inventory_response = client.get(f"/stores/{store_id}/inventory")
        inventory_items = inventory_response.json()
        
        cilantro = next(item for item in inventory_items if "cilantro" in item["ingredient_name"])
        assert cilantro["quantity"] == 2.0
        assert cilantro["unit"] == "bunches"

    @patch("app.services.inventory_parser.create_inventory_parser_client")
    def test_edge_case_handling_with_mocked_responses(self, mock_parser_factory) -> None:
        """Test edge cases using fixture-based responses."""
        # Given
        mock_parser = MockLLMInventoryParser()
        mock_parser_factory.return_value = mock_parser

        # Create store
        store_response = client.post("/stores", json={"name": "Edge Case Store"})
        store_id = store_response.json()["store_id"]

        # Test empty input
        empty_response = client.post(
            f"/stores/{store_id}/inventory", 
            json={"inventory_text": ""}
        )
        assert empty_response.status_code == 201
        assert empty_response.json()["items_added"] == 0

        # Test whitespace only
        whitespace_response = client.post(
            f"/stores/{store_id}/inventory", 
            json={"inventory_text": "   \n\t  "}
        )
        assert whitespace_response.status_code == 201
        assert whitespace_response.json()["items_added"] == 0