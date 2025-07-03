import tempfile
from datetime import datetime
from uuid import uuid4

import pytest

from app.events.domain_events import IngredientCreated, InventoryItemAdded, StoreCreated
from app.infrastructure.event_store import EventStore


class TestProjectionBehavior:
    """Test that domain events enable fast queries through projections."""

    @pytest.fixture
    def temp_db_path(self) -> str:
        """Create a temporary database file for testing."""
        return tempfile.mktemp(suffix=".db")

    @pytest.fixture
    def event_store(self, temp_db_path: str) -> EventStore:
        """Create an EventStore with temporary database."""
        return EventStore(temp_db_path)

    def test_ingredient_created_event_enables_fast_lookup(
        self, event_store: EventStore, temp_db_path: str
    ) -> None:
        """Test that IngredientCreated event enables fast ingredient lookup."""
        # Given: a new ingredient is created
        ingredient_id = uuid4()
        created_at = datetime(2023, 1, 1, 0, 0, 0)
        event = IngredientCreated(
            ingredient_id=ingredient_id,
            name="carrot",
            default_unit="pound",
            created_at=created_at,
        )

        # When: the event is stored
        event_store.append_event(f"ingredient-{ingredient_id}", event)

        # Then: the ingredient can be quickly looked up by ID
        ingredient = event_store.get_ingredient_by_id(str(ingredient_id))

        assert ingredient is not None, "Ingredient should be findable by ID"
        assert ingredient["ingredient_id"] == str(ingredient_id)
        assert ingredient["name"] == "carrot"
        assert ingredient["default_unit"] == "pound"
        assert ingredient["created_at"] == created_at.isoformat()

    def test_store_created_event_appears_in_store_list(
        self, event_store: EventStore, temp_db_path: str
    ) -> None:
        """Test that StoreCreated event makes store appear in store list queries."""
        # Given: a new store is created
        store_id = uuid4()
        created_at = datetime(2023, 1, 1, 0, 0, 0)
        event = StoreCreated(
            store_id=store_id,
            name="CSA Box",
            description="Weekly vegetable delivery",
            infinite_supply=False,
            created_at=created_at,
        )

        # When: the event is stored
        event_store.append_event(f"store-{store_id}", event)

        # Then: the store appears in the store list
        stores = event_store.get_stores_with_item_count()

        assert len(stores) == 1, "Should have one store in the list"
        store = stores[0]
        assert store["store_id"] == str(store_id)
        assert store["name"] == "CSA Box"
        assert store["description"] == "Weekly vegetable delivery"
        assert store["infinite_supply"] is False
        assert store["item_count"] == 0  # No inventory items yet

    def test_inventory_item_added_enables_store_inventory_query(
        self, event_store: EventStore, temp_db_path: str
    ) -> None:
        """Test complete roundtrip: events → inventory query with ingredient names."""
        # Given: a store and ingredient exist
        ingredient_id = uuid4()
        store_id = uuid4()
        created_at = datetime(2023, 1, 1, 0, 0, 0)
        added_at = datetime(2023, 1, 1, 12, 0, 0)

        # Setup prerequisite events
        event_store.append_event(
            f"ingredient-{ingredient_id}",
            IngredientCreated(
                ingredient_id=ingredient_id,
                name="kale",
                default_unit="bunch",
                created_at=created_at,
            ),
        )

        event_store.append_event(
            f"store-{store_id}",
            StoreCreated(
                store_id=store_id,
                name="Farmer's Market",
                description="Local produce",
                infinite_supply=False,
                created_at=created_at,
            ),
        )

        # When: inventory is added to the store
        event_store.append_event(
            f"store-{store_id}",
            InventoryItemAdded(
                store_id=store_id,
                ingredient_id=ingredient_id,
                quantity=1.0,
                unit="bunch",
                notes="Fresh from garden",
                added_at=added_at,
            ),
        )

        # Then: store inventory query returns the item with ingredient name
        inventory = event_store.get_store_inventory(str(store_id))

        assert len(inventory) == 1, "Should have one inventory item"
        item = inventory[0]
        assert item["ingredient_id"] == str(ingredient_id)
        assert item["ingredient_name"] == "kale"  # Name resolved from ingredient
        assert item["quantity"] == 1.0
        assert item["unit"] == "bunch"
        assert item["notes"] == "Fresh from garden"
        assert item["added_at"] == added_at.isoformat()

        # And: store list shows updated item count
        stores = event_store.get_stores_with_item_count()
        store = next(s for s in stores if s["store_id"] == str(store_id))
        assert store["item_count"] == 1

    def test_store_list_shows_accurate_item_counts(
        self, event_store: EventStore, temp_db_path: str
    ) -> None:
        """Test that store list query accurately reflects inventory item counts."""
        # Given: multiple stores with different inventory levels
        store1_id, store2_id = uuid4(), uuid4()
        ingredient1_id, ingredient2_id = uuid4(), uuid4()
        created_at = datetime(2023, 1, 1, 0, 0, 0)

        # Create stores
        for store_id, name, has_items in [
            (store1_id, "CSA Box", True),
            (store2_id, "Empty Store", False),
        ]:
            event_store.append_event(
                f"store-{store_id}",
                StoreCreated(
                    store_id=store_id,
                    name=name,
                    description="Test store",
                    infinite_supply=False,
                    created_at=created_at,
                ),
            )

        # Create ingredients and add to first store only
        for ingredient_id, name in [
            (ingredient1_id, "carrot"),
            (ingredient2_id, "onion"),
        ]:
            event_store.append_event(
                f"ingredient-{ingredient_id}",
                IngredientCreated(
                    ingredient_id=ingredient_id,
                    name=name,
                    default_unit="pound",
                    created_at=created_at,
                ),
            )

            # Add to first store only
            event_store.append_event(
                f"store-{store1_id}",
                InventoryItemAdded(
                    store_id=store1_id,
                    ingredient_id=ingredient_id,
                    quantity=1.0,
                    unit="pound",
                    notes=None,
                    added_at=created_at,
                ),
            )

        # When: querying store list
        stores = event_store.get_stores_with_item_count()

        # Then: item counts are accurate
        assert len(stores) == 2

        store_by_id = {s["store_id"]: s for s in stores}
        assert store_by_id[str(store1_id)]["item_count"] == 2
        assert store_by_id[str(store2_id)]["item_count"] == 0

    def test_store_inventory_query_includes_ingredient_names(
        self, event_store: EventStore, temp_db_path: str
    ) -> None:
        """Test that store inventory queries include resolved ingredient names."""
        # Given: a store with multiple inventory items
        store_id = uuid4()

        # Setup store and ingredients
        setup_data = [
            (uuid4(), "carrot", 2.5, "Fresh carrots"),
            (uuid4(), "onion", 3.0, None),
        ]

        created_at = datetime(2023, 1, 1, 0, 0, 0)

        # Create store
        event_store.append_event(
            f"store-{store_id}",
            StoreCreated(
                store_id=store_id,
                name="Test Store",
                description="Test store",
                infinite_supply=False,
                created_at=created_at,
            ),
        )

        # Create ingredients and inventory
        for ingredient_id, name, quantity, notes in setup_data:
            event_store.append_event(
                f"ingredient-{ingredient_id}",
                IngredientCreated(
                    ingredient_id=ingredient_id,
                    name=name,
                    default_unit="pound",
                    created_at=created_at,
                ),
            )

            event_store.append_event(
                f"store-{store_id}",
                InventoryItemAdded(
                    store_id=store_id,
                    ingredient_id=ingredient_id,
                    quantity=quantity,
                    unit="pound",
                    notes=notes,
                    added_at=created_at,
                ),
            )

        # When: querying store inventory
        inventory = event_store.get_store_inventory(str(store_id))

        # Then: items include ingredient names and correct data
        assert len(inventory) == 2

        # Sort for consistent testing
        inventory.sort(key=lambda x: x["ingredient_name"])

        assert inventory[0]["ingredient_name"] == "carrot"
        assert inventory[0]["quantity"] == 2.5
        assert inventory[0]["notes"] == "Fresh carrots"

        assert inventory[1]["ingredient_name"] == "onion"
        assert inventory[1]["quantity"] == 3.0
        assert inventory[1]["notes"] is None

    def test_ingredient_lookup_handles_nonexistent_ingredients(
        self, event_store: EventStore, temp_db_path: str
    ) -> None:
        """Test that ingredient lookup gracefully handles missing ingredients."""
        # Given: no ingredients exist
        nonexistent_id = str(uuid4())

        # When: looking up a non-existent ingredient
        ingredient = event_store.get_ingredient_by_id(nonexistent_id)

        # Then: returns None rather than throwing an error
        assert ingredient is None
