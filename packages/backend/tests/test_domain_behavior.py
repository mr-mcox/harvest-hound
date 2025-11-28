import uuid
from datetime import datetime

import pytest

from app.events import IngredientCreated, InventoryItemAdded, StoreCreated
from app.models import Ingredient
from app.models.inventory_store import (
    DefinitionBasedStore,
    ExplicitInventoryStore,
    inventory_store_from_events,
)


class TestExplicitInventoryStoreCreation:
    """Test ExplicitInventoryStore creation behavior and event generation."""

    def test_generates_single_store_created_event(self) -> None:
        """Store creation generates exactly one StoreCreated event."""
        _, events = ExplicitInventoryStore.create(uuid.uuid4(), "CSA Box")

        assert len(events) == 1
        assert isinstance(events[0], StoreCreated)
        assert events[0].store_type == "explicit"

    def test_roundtrip_preserves_store_data(self) -> None:
        """Store can be perfectly reconstructed from its creation event."""
        original_store, events = ExplicitInventoryStore.create(
            uuid.uuid4(), "CSA Box", "Weekly delivery"
        )

        reconstructed_store = ExplicitInventoryStore.from_events(events)
        assert reconstructed_store == original_store

    def test_can_add_inventory(self) -> None:
        """ExplicitInventoryStore allows adding inventory items."""
        store, _ = ExplicitInventoryStore.create(uuid.uuid4(), "Test Store")
        # Should not raise an exception
        updated_store, events = store.add_inventory_item(uuid.uuid4(), 1.0, "lbs")
        assert len(updated_store.inventory_items) == 1


class TestExplicitInventoryStoreInventory:
    """Test ExplicitInventoryStore inventory operations."""

    @pytest.fixture
    def sample_store(self) -> ExplicitInventoryStore:
        """Create a sample store for testing inventory operations."""
        store, _ = ExplicitInventoryStore.create(uuid.uuid4(), "Test Store")
        return store

    def test_generates_single_inventory_item_added_event(
        self, sample_store: ExplicitInventoryStore
    ) -> None:
        """Adding inventory item generates exactly one InventoryItemAdded event."""
        _, events = sample_store.add_inventory_item(
            uuid.uuid4(), 2.0, "lbs", "Fresh carrots"
        )

        assert len(events) == 1
        assert isinstance(events[0], InventoryItemAdded)

    def test_adds_item_to_store_inventory(
        self, sample_store: ExplicitInventoryStore
    ) -> None:
        """Adding inventory item updates store's inventory list."""
        ingredient_id = uuid.uuid4()

        updated_store, _ = sample_store.add_inventory_item(
            ingredient_id, 2.0, "lbs", "Fresh carrots"
        )

        assert len(updated_store.inventory_items) == 1
        assert updated_store.inventory_items[0].ingredient_id == ingredient_id

    def test_complete_store_roundtrip_with_inventory(
        self, sample_store: ExplicitInventoryStore
    ) -> None:
        """Store with inventory items can be reconstructed from event history."""
        # Get creation events for the sample store
        creation_event = StoreCreated(
            store_id=sample_store.store_id,
            name=sample_store.name,
            description=sample_store.description,
            store_type="explicit",
            created_at=datetime.now(),
        )

        # Add multiple inventory items
        store1, events1 = sample_store.add_inventory_item(
            uuid.uuid4(), 2.0, "lbs", "Carrots"
        )
        store2, events2 = store1.add_inventory_item(uuid.uuid4(), 1.0, "bunch", "Kale")

        # Reconstruct from complete event history
        all_events = [creation_event] + events1 + events2
        reconstructed = ExplicitInventoryStore.from_events(all_events)

        assert reconstructed == store2
        assert len(reconstructed.inventory_items) == 2

    def test_check_availability_returns_true_when_sufficient(
        self, sample_store: ExplicitInventoryStore
    ) -> None:
        """check_availability returns True when ingredient quantity is sufficient."""
        ingredient_id = uuid.uuid4()
        store_with_item, _ = sample_store.add_inventory_item(
            ingredient_id, 5.0, "lbs", "Carrots"
        )

        assert store_with_item.check_availability(ingredient_id, 3.0, "lbs") is True

    def test_check_availability_returns_false_when_insufficient(
        self, sample_store: ExplicitInventoryStore
    ) -> None:
        """check_availability returns False when ingredient quantity is insufficient."""
        ingredient_id = uuid.uuid4()
        store_with_item, _ = sample_store.add_inventory_item(
            ingredient_id, 2.0, "lbs", "Carrots"
        )

        assert store_with_item.check_availability(ingredient_id, 5.0, "lbs") is False


class TestDefinitionBasedStoreCreation:
    """Test DefinitionBasedStore creation behavior and event generation."""

    def test_generates_single_store_created_event(self) -> None:
        """Store creation generates exactly one StoreCreated event."""
        _, events = DefinitionBasedStore.create(
            uuid.uuid4(), "Pantry", "Basic pantry staples like flour, sugar, salt"
        )

        assert len(events) == 1
        assert isinstance(events[0], StoreCreated)
        assert events[0].store_type == "definition"
        assert events[0].definition == "Basic pantry staples like flour, sugar, salt"

    def test_roundtrip_preserves_store_data(self) -> None:
        """Store can be perfectly reconstructed from its creation event."""
        original_store, events = DefinitionBasedStore.create(
            uuid.uuid4(), "Pantry", "Basic pantry staples", "My pantry"
        )

        reconstructed_store = DefinitionBasedStore.from_events(events)
        assert reconstructed_store == original_store
        assert reconstructed_store.definition == "Basic pantry staples"

    def test_does_not_support_inventory_addition(self) -> None:
        """DefinitionBasedStore does not have add_inventory_item method."""
        store, _ = DefinitionBasedStore.create(
            uuid.uuid4(), "Pantry", "Basic pantry staples"
        )
        # Attempting to add inventory should raise AttributeError
        with pytest.raises(AttributeError):
            store.add_inventory_item(uuid.uuid4(), 1.0, "cup")  # type: ignore[attr-defined]

    def test_check_availability_returns_false_stub(self) -> None:
        """check_availability returns False as stub (LLM not yet implemented)."""
        store, _ = DefinitionBasedStore.create(
            uuid.uuid4(), "Pantry", "Basic pantry staples"
        )
        # Stubbed implementation always returns False for now
        assert store.check_availability(uuid.uuid4(), 1.0, "cup") is False


class TestPolymorphicStoreFactory:
    """Test the inventory_store_from_events factory function."""

    def test_creates_explicit_store_from_events(self) -> None:
        """Factory creates ExplicitInventoryStore when store_type is 'explicit'."""
        store_id = uuid.uuid4()
        events = [
            StoreCreated(
                store_id=store_id,
                name="CSA Box",
                description="Weekly delivery",
                store_type="explicit",
                created_at=datetime.now(),
            )
        ]

        store = inventory_store_from_events(events)

        assert isinstance(store, ExplicitInventoryStore)
        assert store.store_id == store_id

    def test_creates_definition_store_from_events(self) -> None:
        """Factory creates DefinitionBasedStore when store_type is 'definition'."""
        store_id = uuid.uuid4()
        events = [
            StoreCreated(
                store_id=store_id,
                name="Pantry",
                description="My pantry",
                store_type="definition",
                definition="Basic pantry staples",
                created_at=datetime.now(),
            )
        ]

        store = inventory_store_from_events(events)

        assert isinstance(store, DefinitionBasedStore)
        assert store.store_id == store_id
        assert store.definition == "Basic pantry staples"

    def test_raises_error_for_unknown_store_type(self) -> None:
        """Factory raises error for unknown store_type."""
        events = [
            StoreCreated(
                store_id=uuid.uuid4(),
                name="Unknown",
                description="",
                store_type="unknown_type",
                created_at=datetime.now(),
            )
        ]

        with pytest.raises(ValueError, match="Unknown store type"):
            inventory_store_from_events(events)


class TestIngredientCreation:
    """Test ingredient creation behavior and event generation."""

    def test_generates_single_ingredient_created_event(self) -> None:
        """Ingredient creation generates exactly one IngredientCreated event."""
        _, events = Ingredient.create(uuid.uuid4(), "Carrots", "lbs")

        assert len(events) == 1
        assert isinstance(events[0], IngredientCreated)

    def test_roundtrip_preserves_ingredient_data(self) -> None:
        """Ingredient data is preserved through event roundtrip."""
        original_ingredient, events = Ingredient.create(uuid.uuid4(), "Carrots", "lbs")

        # Since Ingredient doesn't have from_events yet, we test event data directly
        event = events[0]
        assert isinstance(event, IngredientCreated)
        reconstructed_ingredient = Ingredient(
            ingredient_id=event.ingredient_id,
            name=event.name,
            default_unit=event.default_unit,
            created_at=event.created_at,
        )

        assert reconstructed_ingredient == original_ingredient
