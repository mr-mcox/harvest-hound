import os
from abc import ABC, abstractmethod
from typing import List, Optional

from ..infrastructure.baml_client import b
from ..models.parsed_inventory import ParsedInventoryItem


class InventoryParserClient(ABC):
    """Abstract client for parsing inventory text."""

    @abstractmethod
    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Parse inventory text into structured items."""
        pass


class BamlInventoryParserClient(InventoryParserClient):
    """Real BAML-based inventory parser client."""

    def __init__(self) -> None:
        # Check if we're in a test environment and require explicit opt-in
        if os.environ.get("TESTING", "false").lower() == "true":
            if os.environ.get("ALLOW_BAML_IN_TESTS", "false").lower() != "true":
                raise RuntimeError(
                    "BAML client cannot be used in tests. "
                    "Use TestInventoryParserClient instead."
                )

    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Parse inventory text using BAML LLM service."""
        if not inventory_text.strip():
            return []

        # Use BAML client to parse the text
        from ..infrastructure.translation import InventoryTranslator

        translator = InventoryTranslator()
        baml_ingredients = b.ExtractIngredients(inventory_text)

        # Convert BAML result to domain objects
        return [
            translator.to_parsed_inventory_item(ingredient)
            for ingredient in baml_ingredients
        ]


class TestInventoryParserClient(InventoryParserClient):
    """Test implementation for inventory parser client."""

    def __init__(self, mock_results: Optional[List[ParsedInventoryItem]] = None):
        self.mock_results = mock_results or []

    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Return pre-configured mock results."""
        if not inventory_text.strip():
            return []
        return self.mock_results


def create_inventory_parser_client() -> InventoryParserClient:
    """Factory function to create appropriate inventory parser client."""
    if os.environ.get("TESTING", "false").lower() == "true":
        return TestInventoryParserClient()
    else:
        return BamlInventoryParserClient()
