import os
from abc import ABC, abstractmethod
from typing import List, Optional

from ..infrastructure.baml_client import b
from ..infrastructure.translation import InventoryTranslator
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


class MockInventoryParserClient(InventoryParserClient):
    """Test implementation for inventory parser client."""

    def __init__(self, mock_results: Optional[List[ParsedInventoryItem]] = None):
        self.mock_results = mock_results or []

    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Return pre-configured mock results."""
        if not inventory_text.strip():
            return []
        return self.mock_results


def create_inventory_parser_client() -> InventoryParserClient:
    """Factory function to create appropriate inventory parser client.

    Defaults to MockInventoryParserClient for safety.
    Use ENABLE_BAML=true to enable real BAML client.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    enable_baml = os.environ.get("ENABLE_BAML", "false")
    logger.error("🐤 CANARY: ENABLE_BAML env var = %r", enable_baml)
    
    if enable_baml.lower() == "true":
        logger.error("🐤 CANARY: Creating BamlInventoryParserClient")
        try:
            return BamlInventoryParserClient()
        except Exception as e:
            logger.error("🐤 CANARY: Failed to create BAML client: %s", str(e))
            raise
    else:
        logger.error("🐤 CANARY: Creating MockInventoryParserClient (ENABLE_BAML not true)")
        return MockInventoryParserClient()
