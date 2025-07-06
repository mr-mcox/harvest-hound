"""
Test projection handlers for read model updates.

Testing projection handlers to ensure they correctly update read models
in response to domain events as per ADR-005.
"""
from datetime import datetime
from uuid import uuid4
from unittest.mock import Mock

import pytest

from app.events.domain_events import InventoryItemAdded, StoreCreated, IngredientCreated
from app.models import Ingredient, InventoryStore
from app.models.read_models import InventoryItemView, StoreView
from app.projections.handlers import InventoryProjectionHandler, StoreProjectionHandler


class TestInventoryProjectionHandler:
    """Test InventoryProjectionHandler for inventory read model updates."""

    def test_handle_inventory_item_added_creates_view(self):
        """InventoryProjectionHandler should create InventoryItemView on InventoryItemAdded event."""
        # Arrange
        mock_ingredient_repo = Mock()
        mock_store_repo = Mock()
        mock_view_store = Mock()
        
        # Set up mock data
        store_id = uuid4()
        ingredient_id = uuid4()
        added_at = datetime(2024, 1, 15, 14, 30)
        
        mock_ingredient = Ingredient(
            ingredient_id=ingredient_id,
            name="Carrots",
            default_unit="lbs",
            created_at=datetime(2024, 1, 1)
        )
        mock_store = InventoryStore(
            store_id=store_id,
            name="CSA Box",
            description="Weekly delivery",
            infinite_supply=False,
            inventory_items=[]
        )
        
        mock_ingredient_repo.get_by_id.return_value = mock_ingredient
        mock_store_repo.get_by_id.return_value = mock_store
        
        event = InventoryItemAdded(
            store_id=store_id,
            ingredient_id=ingredient_id,
            quantity=2.0,
            unit="lbs",
            notes="Fresh from farm",
            added_at=added_at,
        )
        
        handler = InventoryProjectionHandler(
            ingredient_repo=mock_ingredient_repo,
            store_repo=mock_store_repo,
            view_store=mock_view_store,
        )
        
        # Act
        handler.handle_inventory_item_added(event)
        
        # Assert
        expected_view = InventoryItemView(
            store_id=store_id,
            ingredient_id=ingredient_id,
            ingredient_name="Carrots",
            store_name="CSA Box",
            quantity=2.0,
            unit="lbs",
            notes="Fresh from farm",
            added_at=added_at,
        )
        
        mock_view_store.save_inventory_item_view.assert_called_once_with(expected_view)

    def test_handle_ingredient_created_updates_existing_views(self):
        """InventoryProjectionHandler should update existing inventory views when ingredient name changes."""
        # Arrange
        mock_ingredient_repo = Mock()
        mock_store_repo = Mock()
        mock_view_store = Mock()
        
        ingredient_id = uuid4()
        store_id = uuid4()
        
        # Existing views to update
        existing_view = InventoryItemView(
            store_id=store_id,
            ingredient_id=ingredient_id,
            ingredient_name="Old Name",
            store_name="CSA Box",
            quantity=2.0,
            unit="lbs",
            notes=None,
            added_at=datetime(2024, 1, 15, 14, 30),
        )
        
        mock_view_store.get_by_ingredient_id.return_value = [existing_view]
        
        event = IngredientCreated(
            ingredient_id=ingredient_id,
            name="Updated Carrots",
            default_unit="lbs",
            created_at=datetime(2024, 1, 16),
        )
        
        handler = InventoryProjectionHandler(
            ingredient_repo=mock_ingredient_repo,
            store_repo=mock_store_repo,
            view_store=mock_view_store,
        )
        
        # Act
        handler.handle_ingredient_created(event)
        
        # Assert
        expected_updated_view = existing_view.model_copy(
            update={"ingredient_name": "Updated Carrots"}
        )
        
        mock_view_store.save_inventory_item_view.assert_called_once_with(expected_updated_view)


class TestStoreProjectionHandler:
    """Test StoreProjectionHandler for store read model updates."""

    def test_handle_store_created_creates_view(self):
        """StoreProjectionHandler should create StoreView on StoreCreated event."""
        # Arrange
        mock_view_store = Mock()
        
        store_id = uuid4()
        created_at = datetime(2024, 1, 15, 10, 0)
        
        event = StoreCreated(
            store_id=store_id,
            name="CSA Box",
            description="Weekly vegetable delivery",
            infinite_supply=False,
            created_at=created_at,
        )
        
        handler = StoreProjectionHandler(view_store=mock_view_store)
        
        # Act
        handler.handle_store_created(event)
        
        # Assert
        expected_view = StoreView(
            store_id=store_id,
            name="CSA Box",
            description="Weekly vegetable delivery",
            infinite_supply=False,
            item_count=0,  # New store starts with 0 items
            created_at=created_at,
        )
        
        mock_view_store.save_store_view.assert_called_once_with(expected_view)

    def test_handle_inventory_item_added_updates_count(self):
        """StoreProjectionHandler should increment item_count on InventoryItemAdded event."""
        # Arrange
        mock_view_store = Mock()
        
        store_id = uuid4()
        
        # Existing store view
        existing_view = StoreView(
            store_id=store_id,
            name="CSA Box",
            description="Weekly delivery",
            infinite_supply=False,
            item_count=2,
            created_at=datetime(2024, 1, 15, 10, 0),
        )
        
        mock_view_store.get_by_store_id.return_value = existing_view
        
        event = InventoryItemAdded(
            store_id=store_id,
            ingredient_id=uuid4(),
            quantity=1.0,
            unit="bunch",
            notes=None,
            added_at=datetime(2024, 1, 15, 14, 30),
        )
        
        handler = StoreProjectionHandler(view_store=mock_view_store)
        
        # Act
        handler.handle_inventory_item_added(event)
        
        # Assert
        expected_updated_view = existing_view.model_copy(
            update={"item_count": 3}
        )
        
        mock_view_store.save_store_view.assert_called_once_with(expected_updated_view)