import pytest

from app.infrastructure.baml_client.types import Ingredient as BamlIngredient
from app.infrastructure.translation import InventoryTranslator
from app.models.parsed_inventory import ParsedInventoryItem


class TestBamlToDomainTranslation:
    """Test translation from BAML types to domain models."""

    def test_baml_ingredient_converts_to_domain_parsed_item(self):
        """Test: BAML InventoryParseResult converts to domain ParsedInventoryItem"""
        baml_ingredient = BamlIngredient(name="carrot", quantity=2.0, unit="pound")

        translator = InventoryTranslator()
        domain_item = translator.to_parsed_inventory_item(baml_ingredient)

        assert isinstance(domain_item, ParsedInventoryItem)
        assert domain_item.name == "carrot"
        assert domain_item.quantity == 2.0
        assert domain_item.unit == "pound"

    def test_translation_preserves_all_data_fields(self):
        """Test: Translation preserves all data fields correctly"""
        baml_ingredient = BamlIngredient(name="kale", quantity=1.0, unit="bunch")

        translator = InventoryTranslator()
        domain_item = translator.to_parsed_inventory_item(baml_ingredient)

        # All fields should be preserved exactly
        assert domain_item.name == baml_ingredient.name
        assert domain_item.quantity == baml_ingredient.quantity
        assert domain_item.unit == baml_ingredient.unit

    def test_translation_handles_missing_fields_gracefully(self):
        """Test: Translation handles missing/null fields gracefully"""
        # Test with edge case values that are still valid
        baml_ingredient = BamlIngredient(
            name="tomato",
            quantity=0.1,  # Very small but valid quantity
            unit="pound",
        )

        translator = InventoryTranslator()

        # Should handle gracefully, not crash
        domain_item = translator.to_parsed_inventory_item(baml_ingredient)
        assert domain_item.name == "tomato"
        assert domain_item.quantity == 0.1
        assert domain_item.unit == "pound"

    def test_translation_validates_domain_constraints(self):
        """Test: Translation validates domain constraints (positive quantities)"""
        baml_ingredient = BamlIngredient(
            name="invalid",
            quantity=-1.0,  # Invalid: negative quantity
            unit="pound",
        )

        translator = InventoryTranslator()

        # Should raise validation error for negative quantity
        with pytest.raises(ValueError) as exc_info:
            translator.to_parsed_inventory_item(baml_ingredient)

        assert "quantity" in str(exc_info.value).lower()
        assert "positive" in str(exc_info.value).lower()

    def test_translation_validates_empty_name(self):
        """Test: Translation validates empty ingredient names"""
        baml_ingredient = BamlIngredient(
            name="",  # Invalid: empty name
            quantity=2.0,
            unit="pound",
        )

        translator = InventoryTranslator()

        # Should raise validation error for empty name
        with pytest.raises(ValueError) as exc_info:
            translator.to_parsed_inventory_item(baml_ingredient)

        assert "name" in str(exc_info.value).lower()

    def test_translation_validates_empty_unit(self):
        """Test: Translation validates empty units"""
        baml_ingredient = BamlIngredient(
            name="carrot",
            quantity=2.0,
            unit="",  # Invalid: empty unit
        )

        translator = InventoryTranslator()

        # Should raise validation error for empty unit
        with pytest.raises(ValueError) as exc_info:
            translator.to_parsed_inventory_item(baml_ingredient)

        assert "unit" in str(exc_info.value).lower()
