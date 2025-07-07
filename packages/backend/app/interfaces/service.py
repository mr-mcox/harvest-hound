"""Service interface protocols."""

from typing import Any, Dict, List, Protocol
from uuid import UUID

from ..services.store_service import InventoryUploadResult


class StoreServiceProtocol(Protocol):
    """Protocol for store service operations."""

    def create_store(
        self,
        name: str,
        description: str = "",
        infinite_supply: bool = False,
    ) -> UUID:
        """Create a new inventory store.
        
        Args:
            name: Store name
            description: Optional store description
            infinite_supply: Whether store has infinite supply
            
        Returns:
            UUID of the created store
        """
        ...

    def upload_inventory(
        self,
        store_id: UUID,
        inventory_text: str,
    ) -> InventoryUploadResult:
        """Upload inventory items to a store by parsing text input.
        
        Args:
            store_id: Unique identifier for the store
            inventory_text: Raw text containing inventory items
            
        Returns:
            Result indicating success/failure and items added
        """
        ...

    def get_all_stores(self) -> List[Dict[str, Any]]:
        """Get list of all stores with item counts.
        
        Returns:
            List of store data dictionaries
        """
        ...

    def get_store_inventory(self, store_id: UUID) -> List[Dict[str, Any]]:
        """Get current inventory for a store with denormalized view data.
        
        Args:
            store_id: Unique identifier for the store
            
        Returns:
            List of inventory item data dictionaries
        """
        ...