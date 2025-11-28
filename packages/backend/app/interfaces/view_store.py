"""View store interface protocols."""

from typing import List, Optional, Protocol
from uuid import UUID

from ..models.read_models import InventoryItemView, StoreView


class StoreViewStoreProtocol(Protocol):
    """Protocol for store view store operations."""

    def get_all_stores(self) -> List[StoreView]:
        """Get all store view records.

        Returns:
            List of all store views
        """
        ...

    def get_by_store_id(self, store_id: UUID) -> Optional[StoreView]:
        """Get store view by ID.

        Args:
            store_id: Unique identifier for the store

        Returns:
            Store view if found, None otherwise
        """
        ...

    def save_store_view(self, store_view: StoreView) -> None:
        """Save a store view record.

        Args:
            store_view: The store view to save
        """
        ...


class InventoryItemViewStoreProtocol(Protocol):
    """Protocol for inventory item view store operations."""

    def get_all_for_store(self, store_id: UUID) -> List[InventoryItemView]:
        """Get all inventory items for a store.

        Args:
            store_id: Unique identifier for the store

        Returns:
            List of inventory item views for the store
        """
        ...

    def save_inventory_item_view(self, item_view: InventoryItemView) -> None:
        """Save an inventory item view record.

        Args:
            item_view: The inventory item view to save
        """
        ...

    def get_by_ingredient_id(self, ingredient_id: UUID) -> List[InventoryItemView]:
        """Get all inventory items for an ingredient.

        Args:
            ingredient_id: Unique identifier for the ingredient

        Returns:
            List of inventory item views for the ingredient
        """
        ...
