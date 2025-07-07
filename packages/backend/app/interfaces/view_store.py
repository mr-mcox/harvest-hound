"""View store interface protocols."""

from typing import Any, Dict, List, Optional, Protocol
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

    def create_store_view(self, store_view: StoreView) -> None:
        """Create a new store view record.
        
        Args:
            store_view: The store view to create
        """
        ...

    def update_item_count(self, store_id: UUID, new_count: int) -> None:
        """Update the item count for a store.
        
        Args:
            store_id: Unique identifier for the store
            new_count: New item count
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

    def create_inventory_item_view(self, item_view: InventoryItemView) -> None:
        """Create a new inventory item view record.
        
        Args:
            item_view: The inventory item view to create
        """
        ...