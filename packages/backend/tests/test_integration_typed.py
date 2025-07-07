"""Integration tests with typed dependency injection (replaces test_integration_mocked_llm.py)."""

from typing import Any, Dict, Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.models.parsed_inventory import ParsedInventoryItem
from tests.implementations.parser import (
    ConfigurableMockInventoryParser,
    FailingMockInventoryParser,
    MockInventoryParser,
)
from tests.utils.api_helpers import (
    create_store,
    find_inventory_item_by_name,
    get_all_stores,
    get_store_inventory,
    upload_inventory,
)
# All fixtures are now in conftest.py and automatically available


class TestTypedIntegrationWorkflow:
    """Test complete API workflow using typed dependency injection."""

    def test_create_store_and_upload_inventory_with_predictable_parsing(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test full workflow: create store → upload inventory → verify parsed results."""
        # Given - Using typed mocked dependencies
        
        # When - Create store
        store_data = create_store(test_client_with_mocks, "Test CSA Box")
        store_id = UUID(store_data["store_id"])

        # When - Upload inventory text that matches fixture
        inventory_text = "2 lbs carrots, 1 bunch kale"
        upload_data = upload_inventory(test_client_with_mocks, store_id, inventory_text)

        # Then - Should parse successfully using fixture data
        assert upload_data["items_added"] == 2
        assert upload_data["success"] is True

        # Then - Verify inventory contains parsed items
        inventory_items = get_store_inventory(test_client_with_mocks, store_id)
        assert len(inventory_items) == 2
        
        # Verify carrots
        carrots = find_inventory_item_by_name(inventory_items, "carrot")
        assert carrots["quantity"] == 2.0
        assert carrots["unit"] == "pound"
        assert carrots["store_name"] == "Test CSA Box"
        
        # Verify kale
        kale = find_inventory_item_by_name(inventory_items, "kale")
        assert kale["quantity"] == 1.0
        assert kale["unit"] == "bunch"
        assert kale["store_name"] == "Test CSA Box"

    def test_complex_inventory_parsing_with_fixture_data(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test parsing complex inventory using fixture responses."""
        # Create store
        store_data = create_store(test_client_with_mocks, "Complex Store")
        store_id = UUID(store_data["store_id"])

        # When - Upload complex inventory (matches fixture)
        complex_text = "3.5 oz organic spinach, 2.25 cups whole milk, 1/2 cup olive oil"
        upload_data = upload_inventory(test_client_with_mocks, store_id, complex_text)

        # Then
        assert upload_data["items_added"] == 3
        assert upload_data["success"] is True

        inventory_items = get_store_inventory(test_client_with_mocks, store_id)
        assert len(inventory_items) == 3

        # Verify fractional quantities are handled correctly
        spinach = find_inventory_item_by_name(inventory_items, "spinach")
        assert spinach["quantity"] == 3.5

        milk = find_inventory_item_by_name(inventory_items, "milk")
        assert milk["quantity"] == 2.25

        oil = find_inventory_item_by_name(inventory_items, "oil")
        assert oil["quantity"] == 0.5


class TestTypedErrorHandling:
    """Test error scenarios using typed mocked dependencies."""

    @pytest.fixture
    def client_with_failing_parser(self) -> Generator[TestClient, None, None]:
        """Client with parser that fails with timeout."""
        from app.dependencies import get_inventory_parser
        from api import app
        
        failing_parser = FailingMockInventoryParser(error_type="timeout")
        
        app.dependency_overrides[get_inventory_parser] = lambda: failing_parser
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    def test_llm_service_timeout_returns_appropriate_error(
        self, client_with_failing_parser: TestClient
    ) -> None:
        """Test handling of LLM service timeouts."""
        # Create store
        store_data = create_store(client_with_failing_parser, "Test Store")
        store_id = UUID(store_data["store_id"])

        # When - Try to upload inventory (should fail with timeout)
        response = client_with_failing_parser.post(
            f"/stores/{store_id}/inventory", 
            json={"inventory_text": "2 lbs carrots"}
        )

        # Then - Should return 400 with timeout error
        assert response.status_code == 400
        error_data = response.json()
        assert "timeout" in error_data["detail"]["errors"][0].lower()

    def test_empty_parsing_result_returns_success_with_zero_items(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test handling when parser returns empty results."""
        # Create store
        store_data = create_store(test_client_with_mocks, "Test Store")
        store_id = UUID(store_data["store_id"])

        # When - Upload text that results in empty parsing
        upload_data = upload_inventory(
            test_client_with_mocks, 
            store_id, 
            "Lorem ipsum dolor sit amet"
        )

        # Then
        assert upload_data["items_added"] == 0
        assert upload_data["success"] is True


class TestTypedPerformanceAndBatching:
    """Test performance characteristics using typed mocked dependencies."""

    def test_batch_processing_handles_multiple_requests(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test multiple concurrent parsing requests."""
        # Create multiple stores
        store_ids = []
        for i in range(3):
            store_data = create_store(test_client_with_mocks, f"Store {i}")
            store_ids.append(UUID(store_data["store_id"]))

        # When - Upload to all stores
        upload_results = []
        for store_id in store_ids:
            upload_data = upload_inventory(
                test_client_with_mocks,
                store_id,
                "1 apple"
            )
            upload_results.append(upload_data)

        # Then - All should succeed
        for result in upload_results:
            assert result["items_added"] == 1
            assert result["success"] is True


class TestTypedConfigurableScenarios:
    """Test specific scenarios using configurable typed mocks."""

    @pytest.fixture
    def client_with_custom_parser(self) -> Generator[TestClient, None, None]:
        """Client with custom parser configuration."""
        from app.dependencies import get_inventory_parser
        from api import app
        
        custom_parser = ConfigurableMockInventoryParser()
        custom_parser.set_response(
            "2 bunches cilantro, 3 limes",
            [
                ParsedInventoryItem(name="cilantro", quantity=2.0, unit="bunches"),
                ParsedInventoryItem(name="limes", quantity=3.0, unit="pieces"),
            ]
        )
        
        app.dependency_overrides[get_inventory_parser] = lambda: custom_parser
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    def test_custom_parsing_scenario(
        self, client_with_custom_parser: TestClient
    ) -> None:
        """Test specific parsing scenario with custom mock configuration."""
        # Create store
        store_data = create_store(client_with_custom_parser, "Custom Store")
        store_id = UUID(store_data["store_id"])

        # When - Upload the configured text
        upload_data = upload_inventory(
            client_with_custom_parser,
            store_id,
            "2 bunches cilantro, 3 limes"
        )

        # Then
        assert upload_data["items_added"] == 2
        assert upload_data["success"] is True

        inventory_items = get_store_inventory(client_with_custom_parser, store_id)
        
        cilantro = find_inventory_item_by_name(inventory_items, "cilantro")
        assert cilantro["quantity"] == 2.0
        assert cilantro["unit"] == "bunches"

    def test_edge_case_handling_with_typed_responses(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test edge cases using typed fixture-based responses."""
        # Create store
        store_data = create_store(test_client_with_mocks, "Edge Case Store")
        store_id = UUID(store_data["store_id"])

        # Test empty input
        empty_result = upload_inventory(test_client_with_mocks, store_id, "")
        assert empty_result["items_added"] == 0
        assert empty_result["success"] is True

        # Test whitespace only
        whitespace_result = upload_inventory(
            test_client_with_mocks, 
            store_id, 
            "   \n\t  "
        )
        assert whitespace_result["items_added"] == 0
        assert whitespace_result["success"] is True