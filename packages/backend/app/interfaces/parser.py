"""Inventory parser interface protocols."""

from typing import List, Protocol, TYPE_CHECKING

from ..models.parsed_inventory import ParsedInventoryItem

if TYPE_CHECKING:
    from ..services.inventory_parser import InventoryParsingResult


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
    
    def parse_inventory_with_notes(self, inventory_text: str) -> "InventoryParsingResult":
        """Parse inventory text with partial success and error reporting.
        
        Args:
            inventory_text: Raw text containing inventory items
            
        Returns:
            Parsing result with successful items and optional parsing notes
            
        Raises:
            ValueError: If text cannot be parsed at all
            TimeoutError: If parsing service is unavailable
        """
        ...