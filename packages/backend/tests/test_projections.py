import sqlite3
import tempfile
from datetime import datetime
from uuid import uuid4

import pytest

from app.events.domain_events import IngredientCreated, InventoryItemAdded, StoreCreated
from app.infrastructure.event_store import EventStore


class TestProjectionBehavior:
    """Test that domain events update projection tables correctly."""

    @pytest.fixture
    def temp_db_path(self) -> str:
        """Create a temporary database file for testing."""
        return tempfile.mktemp(suffix=".db")

    @pytest.fixture
    def event_store(self, temp_db_path: str) -> EventStore:
        """Create an EventStore with temporary database."""
        return EventStore(temp_db_path)

    def test_ingredient_created_event_updates_ingredients_table(
        self, event_store: EventStore, temp_db_path: str
    ) -> None:
        """Test that IngredientCreated event updates ingredients projection table."""
        # Create an IngredientCreated event
        ingredient_id = uuid4()
        created_at = datetime(2023, 1, 1, 0, 0, 0)
        event = IngredientCreated(
            ingredient_id=ingredient_id,
            name="carrot",
            default_unit="pound",
            created_at=created_at,
        )

        # This should fail because we haven't implemented projection updates yet
        event_store.append_event(f"ingredient-{ingredient_id}", event)

        # Check that the ingredient was added to the projection table
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute(
                """SELECT ingredient_id, name, default_unit, created_at
                   FROM ingredients WHERE ingredient_id = ?""",
                (str(ingredient_id),),
            )
            row = cursor.fetchone()

        assert row is not None, "Ingredient should be in projection table"
        assert row[0] == str(ingredient_id)
        assert row[1] == "carrot"
        assert row[2] == "pound"
        assert row[3] == created_at.isoformat()

    def test_store_created_event_updates_stores_table(
        self, event_store: EventStore, temp_db_path: str
    ) -> None:
        """Test that StoreCreated event updates stores projection table."""
        # Create a StoreCreated event
        store_id = uuid4()
        created_at = datetime(2023, 1, 1, 0, 0, 0)
        event = StoreCreated(
            store_id=store_id,
            name="CSA Box",
            description="Weekly vegetable delivery",
            infinite_supply=False,
            created_at=created_at,
        )

        # This should fail because we haven't implemented projection updates yet
        event_store.append_event(f"store-{store_id}", event)

        # Check that the store was added to the projection table
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute(
                """SELECT store_id, name, description, infinite_supply, created_at
                   FROM stores WHERE store_id = ?""",
                (str(store_id),),
            )
            row = cursor.fetchone()

        assert row is not None, "Store should be in projection table"
        assert row[0] == str(store_id)
        assert row[1] == "CSA Box"
        assert row[2] == "Weekly vegetable delivery"
        assert row[3] == 0  # SQLite stores boolean as 0/1
        assert row[4] == created_at.isoformat()

    def test_inventory_item_added_event_updates_current_inventory_view(
        self, event_store: EventStore, temp_db_path: str
    ) -> None:
        """Test that InventoryItemAdded event updates current_inventory view."""
        # First create prerequisite ingredient and store
        ingredient_id = uuid4()
        store_id = uuid4()
        created_at = datetime(2023, 1, 1, 0, 0, 0)
        added_at = datetime(2023, 1, 1, 12, 0, 0)

        ingredient_event = IngredientCreated(
            ingredient_id=ingredient_id,
            name="kale",
            default_unit="bunch",
            created_at=created_at,
        )

        store_event = StoreCreated(
            store_id=store_id,
            name="Farmer's Market",
            description="Local produce",
            infinite_supply=False,
            created_at=created_at,
        )

        # Add events to populate projection tables
        event_store.append_event(f"ingredient-{ingredient_id}", ingredient_event)
        event_store.append_event(f"store-{store_id}", store_event)

        # Create an InventoryItemAdded event
        inventory_event = InventoryItemAdded(
            store_id=store_id,
            ingredient_id=ingredient_id,
            quantity=1.0,
            unit="bunch",
            notes="Fresh from garden",
            added_at=added_at,
        )

        # This should fail because we haven't implemented projection updates yet
        event_store.append_event(f"store-{store_id}", inventory_event)

        # Check that the inventory item appears in current_inventory view
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute(
                """SELECT store_id, store_name, ingredient_id, ingredient_name,
                          quantity, unit, notes, added_at
                   FROM current_inventory
                   WHERE store_id = ? AND ingredient_id = ?""",
                (str(store_id), str(ingredient_id)),
            )
            row = cursor.fetchone()

        assert row is not None, "Inventory item should appear in current_inventory view"
        assert row[0] == str(store_id)
        assert row[1] == "Farmer's Market"
        assert row[2] == str(ingredient_id)
        assert row[3] == "kale"
        assert row[4] == 1.0
        assert row[5] == "bunch"
        assert row[6] == "Fresh from garden"
        assert row[7] == added_at.isoformat()
