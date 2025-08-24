"""Inventory parser interface protocols."""

from dataclasses import dataclass
from typing import List, Optional, Protocol

from ..models.parsed_inventory import ParsedInventoryItem


@dataclass
class ParsedInventoryResult:
    """Result of parsing inventory text including items and notes."""
    
    items: List[ParsedInventoryItem]
    parsing_notes: Optional[str] = None


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

    def parse_inventory_with_notes(self, inventory_text: str) -> ParsedInventoryResult:
        """Parse inventory text and return items with parsing notes.
        
        Args:
            inventory_text: Raw text containing inventory items
            
        Returns:
            ParsedInventoryResult with items and optional parsing notes
            
        Raises:
            ValueError: If text cannot be parsed
            TimeoutError: If parsing service is unavailable
        """
        ...