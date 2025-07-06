"""
Test view stores for read model persistence.

Testing view stores to ensure they provide efficient storage and retrieval
of denormalized read models as per ADR-005.
"""
import sqlite3
from datetime import datetime
from uuid import uuid4
from unittest.mock import Mock, patch

import pytest

from app.models.read_models import InventoryItemView, StoreView
from app.infrastructure.view_stores import InventoryItemViewStore, StoreViewStore


class TestInventoryItemViewStore:
    """Test InventoryItemViewStore for inventory read model persistence."""

    def test_save_inventory_item_view(self):
        """InventoryItemViewStore should save InventoryItemView to database."""
        # Arrange
        store = InventoryItemViewStore(db_path=":memory:")
        
        view = InventoryItemView(
            store_id=uuid4(),
            ingredient_id=uuid4(),
            ingredient_name="Carrots",
            store_name="CSA Box",
            quantity=2.0,
            unit="lbs",
            notes="Fresh from farm",
            added_at=datetime(2024, 1, 15, 14, 30),
        )
        
        # Act & Assert - should not raise exception
        store.save_inventory_item_view(view)

    def test_get_by_ingredient_id(self):
        """InventoryItemViewStore should retrieve views by ingredient ID."""
        # Arrange
        store = InventoryItemViewStore(db_path=":memory:")
        ingredient_id = uuid4()
        
        # Act
        views = store.get_by_ingredient_id(ingredient_id)
        
        # Assert
        assert isinstance(views, list)

    def test_get_all_for_store(self):
        """InventoryItemViewStore should retrieve all views for a store."""
        # Arrange
        store = InventoryItemViewStore(db_path=":memory:")
        store_id = uuid4()
        
        # Act
        views = store.get_all_for_store(store_id)
        
        # Assert
        assert isinstance(views, list)


class TestStoreViewStore:
    """Test StoreViewStore for store read model persistence."""

    def test_save_store_view(self):
        """StoreViewStore should save StoreView to database."""
        # Arrange
        store = StoreViewStore(db_path=":memory:")
        
        view = StoreView(
            store_id=uuid4(),
            name="CSA Box",
            description="Weekly vegetable delivery",
            infinite_supply=False,
            item_count=5,
            created_at=datetime(2024, 1, 15, 10, 0),
        )
        
        # Act & Assert - should not raise exception
        store.save_store_view(view)

    def test_get_by_store_id(self):
        """StoreViewStore should retrieve view by store ID."""
        # Arrange
        store = StoreViewStore(db_path=":memory:")
        store_id = uuid4()
        
        # Act
        view = store.get_by_store_id(store_id)
        
        # Assert - view can be None if not found
        assert view is None or isinstance(view, StoreView)

    def test_get_all_stores(self):
        """StoreViewStore should retrieve all store views."""
        # Arrange
        store = StoreViewStore(db_path=":memory:")
        
        # Act
        views = store.get_all_stores()
        
        # Assert
        assert isinstance(views, list)