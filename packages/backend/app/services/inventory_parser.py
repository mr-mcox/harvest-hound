import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from ..infrastructure.baml_client import b
from ..infrastructure.translation import InventoryTranslator
from ..models.parsed_inventory import ParsedInventoryItem


@dataclass
class InventoryParsingResult:
    """Result of parsing inventory text with partial success support."""
    successful_items: List[ParsedInventoryItem]
    parsing_notes: Optional[str] = None


class InventoryParserClient(ABC):
    """Abstract client for parsing inventory text."""

    @abstractmethod
    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Parse inventory text into structured items."""
        pass
    
    @abstractmethod
    def parse_inventory_with_notes(self, inventory_text: str) -> InventoryParsingResult:
        """Parse inventory text with partial success and error reporting."""
        pass


class BamlInventoryParserClient(InventoryParserClient):
    """Real BAML-based inventory parser client."""

    def __init__(self) -> None:
        # Require explicit opt-in for BAML usage (defaults to safe testing mode)
        if os.environ.get("ENABLE_BAML", "false").lower() != "true":
            raise RuntimeError(
                "BAML client requires ENABLE_BAML=true environment variable. "
                "Use MockInventoryParserClient for testing."
            )

    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Parse inventory text using BAML LLM service."""
        if not inventory_text.strip():
            return []

        # Use BAML client to parse the text
        translator = InventoryTranslator()
        baml_ingredients = b.ExtractIngredients(inventory_text)

        # Convert BAML result to domain objects
        return [
            translator.to_parsed_inventory_item(ingredient)
            for ingredient in baml_ingredients
        ]
    
    def parse_inventory_with_notes(self, inventory_text: str) -> InventoryParsingResult:
        """Parse inventory text with partial success reporting using BAML."""
        # TODO: Implement in Task 2.4 with enhanced BAML schema
        # For now, delegate to existing method
        items = self.parse_inventory(inventory_text)
        return InventoryParsingResult(successful_items=items, parsing_notes=None)


class MockInventoryParserClient(InventoryParserClient):
    """Test implementation for inventory parser client."""

    def __init__(
        self, 
        mock_results: Optional[List[ParsedInventoryItem]] = None,
        mock_parsing_result: Optional[InventoryParsingResult] = None
    ):
        self.mock_results = mock_results or []
        self.mock_parsing_result = mock_parsing_result

    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Return pre-configured mock results."""
        if not inventory_text.strip():
            return []
        return self.mock_results
    
    def parse_inventory_with_notes(self, inventory_text: str) -> InventoryParsingResult:
        """Return pre-configured mock parsing result with notes."""
        if not inventory_text.strip():
            return InventoryParsingResult(successful_items=[], parsing_notes=None)
        
        if self.mock_parsing_result is not None:
            return self.mock_parsing_result
        
        # Default: use mock_results with no parsing notes
        return InventoryParsingResult(successful_items=self.mock_results, parsing_notes=None)


def create_inventory_parser_client() -> InventoryParserClient:
    """Factory function to create appropriate inventory parser client.

    Defaults to MockInventoryParserClient for safety.
    Use ENABLE_BAML=true to enable real BAML client.
    """
    if os.environ.get("ENABLE_BAML", "false").lower() == "true":
        return BamlInventoryParserClient()
    else:
        return MockInventoryParserClient()
