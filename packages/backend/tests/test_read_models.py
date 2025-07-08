"""
Test read model classes for denormalized views.

Testing read models to ensure they provide flat, denormalized data
structures optimized for UI consumption as per ADR-005.
"""
from datetime import datetime
from uuid import uuid4

from app.models.read_models import InventoryItemView, StoreView


class TestInventoryItemView:
    """Test InventoryItemView read model."""

    def test_inventory_item_view_has_denormalized_fields(self) -> None:
        """InventoryItemView should include denormalized ingredient_name and store_name."""
        # Arrange
        store_id = uuid4()
        ingredient_id = uuid4()
        added_at = datetime(2024, 1, 15, 10, 30)

        # Act
        view = InventoryItemView(
            store_id=store_id,
            ingredient_id=ingredient_id,
            ingredient_name="Carrots",
            store_name="CSA Box",
            quantity=2.0,
            unit="lbs",
            notes="Fresh from farm",
            added_at=added_at,
        )

        # Assert
        assert view.store_id == store_id
        assert view.ingredient_id == ingredient_id
        assert view.ingredient_name == "Carrots"
        assert view.store_name == "CSA Box"
        assert view.quantity == 2.0
        assert view.unit == "lbs"
        assert view.notes == "Fresh from farm"
        assert view.added_at == added_at

    def test_inventory_item_view_display_name_property(self) -> None:
        """InventoryItemView should provide computed display_name property."""
        # Arrange
        view = InventoryItemView(
            store_id=uuid4(),
            ingredient_id=uuid4(),
            ingredient_name="Tomatoes",
            store_name="Garden Store",
            quantity=3.0,
            unit="pieces",
            notes=None,
            added_at=datetime.now(),
        )

        # Act & Assert
        assert view.display_name == "3.0 pieces Tomatoes"

    def test_inventory_item_view_optional_notes(self) -> None:
        """InventoryItemView should support optional notes field."""
        # Arrange & Act
        view = InventoryItemView(
            store_id=uuid4(),
            ingredient_id=uuid4(),
            ingredient_name="Kale",
            store_name="CSA Box",
            quantity=1.0,
            unit="bunch",
            notes=None,
            added_at=datetime.now(),
        )

        # Assert
        assert view.notes is None


class TestStoreView:
    """Test StoreView read model."""

    def test_store_view_has_computed_fields(self) -> None:
        """StoreView should include computed item_count field."""
        # Arrange
        store_id = uuid4()
        created_at = datetime(2024, 1, 15, 10, 0)

        # Act
        view = StoreView(
            store_id=store_id,
            name="CSA Box",
            description="Weekly vegetable delivery",
            infinite_supply=False,
            item_count=5,
            created_at=created_at,
        )

        # Assert
        assert view.store_id == store_id
        assert view.name == "CSA Box"
        assert view.description == "Weekly vegetable delivery"
        assert view.infinite_supply is False
        assert view.item_count == 5
        assert view.created_at == created_at

    def test_store_view_empty_description_default(self) -> None:
        """StoreView should support empty description with default."""
        # Arrange & Act
        view = StoreView(
            store_id=uuid4(),
            name="Pantry",
            description="",
            infinite_supply=True,
            item_count=0,
            created_at=datetime.now(),
        )

        # Assert
        assert view.description == ""
        assert view.infinite_supply is True
        assert view.item_count == 0