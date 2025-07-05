import uuid
from datetime import datetime

import pytest

from app.events import IngredientCreated, InventoryItemAdded, StoreCreated
from app.models import Ingredient, InventoryStore


class TestInventoryStoreCreation:
    """Test inventory store creation behavior and event generation."""

    def test_generates_single_store_created_event(self) -> None:
        """Store creation generates exactly one StoreCreated event."""
        _, events = InventoryStore.create(uuid.uuid4(), "CSA Box")

        assert len(events) == 1
        assert isinstance(events[0], StoreCreated)

    def test_roundtrip_preserves_store_data(self) -> None:
        """Store can be perfectly reconstructed from its creation event."""
        original_store, events = InventoryStore.create(
            uuid.uuid4(), "CSA Box", "Weekly delivery", infinite_supply=True
        )

        reconstructed_store = InventoryStore.from_events(events)
        assert reconstructed_store == original_store

    @pytest.mark.parametrize("infinite_supply", [True, False])
    def test_infinite_supply_setting_preserved(self, infinite_supply: bool) -> None:
        """Infinite supply setting is preserved through event roundtrip."""
        _, events = InventoryStore.create(
            uuid.uuid4(), "Test Store", infinite_supply=infinite_supply
        )

        reconstructed = InventoryStore.from_events(events)
        assert reconstructed.infinite_supply == infinite_supply


class TestInventoryItemAddition:
    """Test inventory item addition behavior and event generation."""

    @pytest.fixture
    def sample_store(self) -> InventoryStore:
        """Create a sample store for testing inventory operations."""
        store, _ = InventoryStore.create(uuid.uuid4(), "Test Store")
        return store

    def test_generates_single_inventory_item_added_event(
        self, sample_store: InventoryStore
    ) -> None:
        """Adding inventory item generates exactly one InventoryItemAdded event."""
        _, events = sample_store.add_inventory_item(
            uuid.uuid4(), 2.0, "lbs", "Fresh carrots"
        )

        assert len(events) == 1
        assert isinstance(events[0], InventoryItemAdded)

    def test_adds_item_to_store_inventory(self, sample_store: InventoryStore) -> None:
        """Adding inventory item updates store's inventory list."""
        ingredient_id = uuid.uuid4()

        updated_store, _ = sample_store.add_inventory_item(
            ingredient_id, 2.0, "lbs", "Fresh carrots"
        )

        assert len(updated_store.inventory_items) == 1
        assert updated_store.inventory_items[0].ingredient_id == ingredient_id

    def test_complete_store_roundtrip_with_inventory(
        self, sample_store: InventoryStore
    ) -> None:
        """Store with inventory items can be reconstructed from event history."""
        # Get creation events for the sample store
        creation_event = StoreCreated(
            store_id=sample_store.store_id,
            name=sample_store.name,
            description=sample_store.description,
            infinite_supply=sample_store.infinite_supply,
            created_at=datetime.now(),
        )

        # Add multiple inventory items
        store1, events1 = sample_store.add_inventory_item(
            uuid.uuid4(), 2.0, "lbs", "Carrots"
        )
        store2, events2 = store1.add_inventory_item(uuid.uuid4(), 1.0, "bunch", "Kale")

        # Reconstruct from complete event history
        all_events = [creation_event] + events1 + events2
        reconstructed = InventoryStore.from_events(all_events)

        assert reconstructed == store2
        assert len(reconstructed.inventory_items) == 2


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
