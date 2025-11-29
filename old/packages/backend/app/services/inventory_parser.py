import os
from abc import ABC, abstractmethod
from typing import List, Optional

from ..infrastructure.baml_client import b
from ..infrastructure.translation import InventoryTranslator
from ..interfaces.parser import ParsedInventoryResult
from ..models.parsed_inventory import ParsedInventoryItem


class InventoryParserClient(ABC):
    """Abstract client for parsing inventory text."""

    @abstractmethod
    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Parse inventory text into structured items."""
        pass

    @abstractmethod
    def parse_inventory_with_notes(self, inventory_text: str) -> ParsedInventoryResult:
        """Parse inventory text and return items with parsing notes."""
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
        result = self.parse_inventory_with_notes(inventory_text)
        return result.items

    def parse_inventory_with_notes(self, inventory_text: str) -> ParsedInventoryResult:
        """Parse inventory text using BAML LLM service with parsing notes."""
        if not inventory_text.strip():
            return ParsedInventoryResult(items=[], parsing_notes=None)

        # Use enhanced BAML client to parse with error reporting
        translator = InventoryTranslator()
        baml_result = b.ExtractIngredients(inventory_text)

        # Convert BAML result to domain objects
        items = [
            translator.to_parsed_inventory_item(ingredient)
            for ingredient in baml_result.ingredients
        ]

        return ParsedInventoryResult(
            items=items, parsing_notes=baml_result.parsing_notes
        )


class MockInventoryParserClient(InventoryParserClient):
    """Test implementation for inventory parser client."""

    def __init__(self, mock_results: Optional[List[ParsedInventoryItem]] = None):
        self.mock_results = mock_results or []
        self.mock_parsing_notes: Optional[str] = None

    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Return pre-configured mock results."""
        if not inventory_text.strip():
            return []
        return self.mock_results

    def parse_inventory_with_notes(self, inventory_text: str) -> ParsedInventoryResult:
        """Return pre-configured mock results with parsing notes."""
        items = self.parse_inventory(inventory_text)
        return ParsedInventoryResult(items=items, parsing_notes=self.mock_parsing_notes)


def create_inventory_parser_client() -> InventoryParserClient:
    """Factory function to create appropriate inventory parser client.

    Defaults to MockInventoryParserClient for safety.
    Use ENABLE_BAML=true to enable real BAML client.
    """
    if os.environ.get("ENABLE_BAML", "false").lower() == "true":
        return BamlInventoryParserClient()
    else:
        return MockInventoryParserClient()
