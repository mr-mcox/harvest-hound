"""Unit tests demonstrating typed dependency injection (no @patch decorators)."""

from typing import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from api import app
from app.dependencies import get_inventory_parser
from app.models.parsed_inventory import ParsedInventoryItem
from tests.implementations.parser import (
    ConfigurableMockInventoryParser,
    FailingMockInventoryParser,
    MockInventoryParser,
)


class TestTypedDependencyInjection:
    """Test dependency injection without @patch decorators."""

    @pytest.fixture
    def client_with_custom_parser(self) -> Generator[TestClient, None, None]:
        """Client with custom parser configuration - no @patch needed."""
        
        # Create custom parser
        custom_parser = MockInventoryParser({
            "test input": [
                ParsedInventoryItem(name="test_item", quantity=1.0, unit="piece")
            ]
        })
        
        # Override dependency using FastAPI's built-in mechanism
        app.dependency_overrides[get_inventory_parser] = lambda: custom_parser
        
        client = TestClient(app)
        yield client
        
        # Clean up
        app.dependency_overrides.clear()

    def test_dependency_override_works_without_patches(
        self, client_with_custom_parser: TestClient
    ) -> None:
        """Test that dependency injection works without any @patch decorators."""
        # Create store
        store_response = client_with_custom_parser.post(
            "/stores",
            json={"name": "DI Test Store"}
        )
        assert store_response.status_code == 201
        store_id = store_response.json()["store_id"]

        # Upload inventory using custom parser
        upload_response = client_with_custom_parser.post(
            f"/stores/{store_id}/inventory",
            json={"inventory_text": "test input"}
        )
        
        # Should succeed with our custom parser
        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        assert upload_data["success"] is True
        assert upload_data["items_added"] == 1

    @pytest.fixture
    def client_with_failing_parser(self) -> Generator[TestClient, None, None]:
        """Client with parser that simulates failures - no @patch needed."""
        
        failing_parser = FailingMockInventoryParser(error_type="timeout")
        
        app.dependency_overrides[get_inventory_parser] = lambda: failing_parser
        
        client = TestClient(app)
        yield client
        
        app.dependency_overrides.clear()

    def test_error_handling_without_patches(
        self, client_with_failing_parser: TestClient
    ) -> None:
        """Test error handling without @patch decorators."""
        # Create store
        store_response = client_with_failing_parser.post(
            "/stores",
            json={"name": "Error Test Store"}
        )
        assert store_response.status_code == 201
        store_id = store_response.json()["store_id"]

        # Try to upload - should fail with timeout
        upload_response = client_with_failing_parser.post(
            f"/stores/{store_id}/inventory",
            json={"inventory_text": "any text"}
        )
        
        assert upload_response.status_code == 400
        error_data = upload_response.json()
        assert "timeout" in str(error_data["detail"]["errors"]).lower()

    @pytest.fixture
    def client_with_configurable_parser(self) -> Generator[TestClient, None, None]:
        """Client with runtime configurable parser - no @patch needed."""
        
        configurable_parser = ConfigurableMockInventoryParser()
        configurable_parser.set_response(
            "dynamic input",
            [ParsedInventoryItem(name="dynamic_item", quantity=5.0, unit="grams")]
        )
        
        app.dependency_overrides[get_inventory_parser] = lambda: configurable_parser
        
        client = TestClient(app)
        yield client
        
        app.dependency_overrides.clear()

    def test_configurable_mock_without_patches(
        self, client_with_configurable_parser: TestClient
    ) -> None:
        """Test configurable mocks without @patch decorators."""
        # Create store
        store_response = client_with_configurable_parser.post(
            "/stores",
            json={"name": "Config Test Store"}
        )
        assert store_response.status_code == 201
        store_id = store_response.json()["store_id"]

        # Upload with configured input
        upload_response = client_with_configurable_parser.post(
            f"/stores/{store_id}/inventory",
            json={"inventory_text": "dynamic input"}
        )
        
        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        assert upload_data["success"] is True
        assert upload_data["items_added"] == 1


class TestTypingCompliance:
    """Test that all dependency injection is properly typed."""

    def test_all_fixtures_are_properly_typed(self) -> None:
        """Verify that all mock implementations conform to protocols."""
        # This test passes if mypy passes - it validates typing
        parser = MockInventoryParser()
        result = parser.parse_inventory("test")
        assert isinstance(result, list)
        
        failing_parser = FailingMockInventoryParser()
        
        try:
            failing_parser.parse_inventory("test")
            assert False, "Should have raised an exception"
        except (ValueError, TimeoutError, ConnectionError):
            pass  # Expected

        configurable_parser = ConfigurableMockInventoryParser()
        configurable_parser.set_response("test", [])
        result = configurable_parser.parse_inventory("test")
        assert result == []

    def test_dependency_injection_types_are_correct(self) -> None:
        """Verify dependency injection maintains type safety."""
        from app.dependencies import get_inventory_parser
        
        # This would fail mypy if types were wrong
        parser = get_inventory_parser()
        # Use a recognized fixture input
        result = parser.parse_inventory("2 lbs carrots, 1 bunch kale")
        assert isinstance(result, list)
        assert len(result) == 2