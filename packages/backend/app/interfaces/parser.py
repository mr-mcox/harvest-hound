"""Inventory parser interface protocols."""

from typing import List, Protocol

from ..models.parsed_inventory import ParsedInventoryItem


class InventoryParserProtocol(Protocol):
    """Protocol for inventory text parsing services."""

    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Parse inventory text into structured items.
        
        Args:
            inventory_text: Raw text containing inventory items
            
        Returns:
            List of parsed inventory items
            
        Raises:
            ValueError: If text cannot be parsed
            TimeoutError: If parsing service is unavailable
        """
        ...