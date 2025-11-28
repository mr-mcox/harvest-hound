"""Service interface protocols."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol
from uuid import UUID

from ..services.store_service import InventoryUploadResult

if TYPE_CHECKING:
    from ..services.store_service import UnifiedCreationResult


class StoreServiceProtocol(Protocol):
    """Protocol for store service operations."""

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

    def create_store_with_inventory(
        self,
        name: str,
        description: str,
        store_type: str,
        inventory_text: Optional[str],
        definition: Optional[str] = None,
    ) -> "UnifiedCreationResult":
        """Create store and optionally process inventory in unified operation.

        Args:
            name: Store name
            description: Store description
            store_type: Type of store ("explicit" or "definition")
            inventory_text: Optional inventory text to process
            definition: Required for definition-based stores

        Returns:
            Unified creation result with store_id, successful_items, and error_message
        """
        ...
