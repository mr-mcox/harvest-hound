"""
Test projection registry for managing event handlers.

Testing projection registry to ensure it correctly routes domain events
to appropriate projection handlers as per ADR-005.
"""

from datetime import datetime
from typing import Any
from unittest.mock import Mock
from uuid import uuid4

from app.events.domain_events import IngredientCreated, InventoryItemAdded, StoreCreated
from app.projections.registry import ProjectionRegistry


class TestProjectionRegistry:
    """Test ProjectionRegistry for event routing and handler management."""

    def test_register_handler(self) -> None:
        """ProjectionRegistry should register handlers for specific event types."""
        # Arrange
        registry = ProjectionRegistry()
        mock_handler = Mock()

        # Act
        registry.register(StoreCreated, mock_handler.handle_store_created)

        # Assert - should not raise exception
        assert True  # Basic test that registration works

    def test_handle_routes_to_correct_handler(self) -> None:
        """ProjectionRegistry should route events to correct registered handlers."""
        # Arrange
        registry = ProjectionRegistry()
        mock_store_handler = Mock()
        mock_inventory_handler = Mock()

        registry.register(StoreCreated, mock_store_handler.handle_store_created)
        registry.register(
            InventoryItemAdded, mock_inventory_handler.handle_inventory_item_added
        )

        event = StoreCreated(
            store_id=uuid4(),
            name="CSA Box",
            description="Weekly delivery",
            store_type="explicit",
            created_at=datetime(2024, 1, 15, 10, 0),
        )

        # Act
        registry.handle(event)

        # Assert
        mock_store_handler.handle_store_created.assert_called_once_with(event)
        mock_inventory_handler.handle_inventory_item_added.assert_not_called()

    def test_handle_multiple_handlers_for_same_event(self) -> None:
        """ProjectionRegistry should support multiple handlers for the same event
        type.
        """
        # Arrange
        registry = ProjectionRegistry()
        mock_handler_1 = Mock()
        mock_handler_2 = Mock()

        registry.register(
            InventoryItemAdded, mock_handler_1.handle_inventory_item_added
        )
        registry.register(
            InventoryItemAdded, mock_handler_2.handle_inventory_item_added
        )

        event = InventoryItemAdded(
            store_id=uuid4(),
            ingredient_id=uuid4(),
            quantity=2.0,
            unit="lbs",
            notes="Fresh",
            added_at=datetime(2024, 1, 15, 14, 30),
        )

        # Act
        registry.handle(event)

        # Assert
        mock_handler_1.handle_inventory_item_added.assert_called_once_with(event)
        mock_handler_2.handle_inventory_item_added.assert_called_once_with(event)

    def test_handle_unknown_event_type(self) -> None:
        """ProjectionRegistry should handle unknown event types gracefully."""
        # Arrange
        registry = ProjectionRegistry()

        event = IngredientCreated(
            ingredient_id=uuid4(),
            name="Carrots",
            default_unit="lbs",
            created_at=datetime(2024, 1, 15),
        )

        # Act - should not raise exception for unknown event
        registry.handle(event)

        # Assert - no error should occur
        assert True

    def test_register_with_dependency_injection(self) -> None:
        """ProjectionRegistry should support handler dependency injection patterns."""
        # Arrange
        registry = ProjectionRegistry()
        mock_dependency = Mock()

        def handler_with_deps(event: Any) -> None:
            """Handler that uses injected dependencies."""
            mock_dependency.process(event)

        registry.register(StoreCreated, handler_with_deps)

        event = StoreCreated(
            store_id=uuid4(),
            name="Test Store",
            description="Test",
            store_type="explicit",
            created_at=datetime.now(),
        )

        # Act
        registry.handle(event)

        # Assert
        mock_dependency.process.assert_called_once_with(event)
