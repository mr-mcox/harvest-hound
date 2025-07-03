from app.infrastructure.baml_client.types import Ingredient as BamlIngredient
from app.models.parsed_inventory import ParsedInventoryItem


class InventoryTranslator:
    """Translates BAML-generated types to domain models."""

    def to_parsed_inventory_item(
        self, baml_ingredient: BamlIngredient
    ) -> ParsedInventoryItem:
        """Convert BAML Ingredient to domain ParsedInventoryItem.

        Args:
            baml_ingredient: BAML-generated Ingredient instance

        Returns:
            ParsedInventoryItem: Domain model with validation

        Raises:
            ValueError: If domain constraints are violated
        """
        # ParsedInventoryItem will validate constraints in __post_init__
        return ParsedInventoryItem(
            name=baml_ingredient.name,
            quantity=baml_ingredient.quantity,
            unit=baml_ingredient.unit,
        )
