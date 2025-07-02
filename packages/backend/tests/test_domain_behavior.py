import uuid
from datetime import datetime

from app.events import IngredientCreated, InventoryItemAdded, StoreCreated
from app.models import Ingredient, InventoryStore


def test_inventory_store_creation_generates_store_created_event():
    """Test that InventoryStore creation generates StoreCreated event"""
    # Arrange
    store_id = uuid.uuid4()
    name = "CSA Box"
    description = "Weekly vegetable delivery"
    infinite_supply = False

    # Act
    store = InventoryStore.create(
        store_id=store_id,
        name=name,
        description=description,
        infinite_supply=infinite_supply,
    )

    # Assert
    assert len(store.uncommitted_events) == 1
    event = store.uncommitted_events[0]
    assert isinstance(event, StoreCreated)
    assert event.store_id == store_id
    assert event.name == name
    assert event.description == description
    assert event.infinite_supply == infinite_supply
    assert isinstance(event.created_at, datetime)


def test_adding_inventory_item_generates_inventory_item_added_event():
    """Test that adding inventory item to store generates InventoryItemAdded event"""
    # Arrange
    store_id = uuid.uuid4()
    ingredient_id = uuid.uuid4()
    store = InventoryStore.create(
        store_id=store_id,
        name="CSA Box",
        description="Test store",
        infinite_supply=False,
    )
    # Clear the creation event for this test
    store.uncommitted_events.clear()

    # Act
    store.add_inventory_item(
        ingredient_id=ingredient_id,
        quantity=2.0,
        unit="lbs",
        notes="Fresh carrots",
    )

    # Assert
    assert len(store.uncommitted_events) == 1
    event = store.uncommitted_events[0]
    assert isinstance(event, InventoryItemAdded)
    assert event.store_id == store_id
    assert event.ingredient_id == ingredient_id
    assert event.quantity == 2.0
    assert event.unit == "lbs"
    assert event.notes == "Fresh carrots"
    assert isinstance(event.added_at, datetime)


def test_inventory_store_can_be_rebuilt_from_events():
    """Test that InventoryStore can be rebuilt from sequence of events"""
    # Arrange - create events that represent the history
    store_id = uuid.uuid4()
    ingredient1_id = uuid.uuid4()
    ingredient2_id = uuid.uuid4()

    store_created_event = StoreCreated(
        store_id=store_id,
        name="CSA Box",
        description="Weekly delivery",
        infinite_supply=False,
        created_at=datetime.now(),
    )

    item1_added_event = InventoryItemAdded(
        store_id=store_id,
        ingredient_id=ingredient1_id,
        quantity=2.0,
        unit="lbs",
        notes="Carrots",
        added_at=datetime.now(),
    )

    item2_added_event = InventoryItemAdded(
        store_id=store_id,
        ingredient_id=ingredient2_id,
        quantity=1.0,
        unit="bunch",
        notes="Kale",
        added_at=datetime.now(),
    )

    events = [store_created_event, item1_added_event, item2_added_event]

    # Act
    store = InventoryStore.from_events(events)

    # Assert
    assert store.store_id == store_id
    assert store.name == "CSA Box"
    assert store.description == "Weekly delivery"
    assert store.infinite_supply is False
    assert len(store.inventory_items) == 2
    assert len(store.uncommitted_events) == 0  # Should be empty for rebuilt aggregates

    # Check first inventory item
    item1 = store.inventory_items[0]
    assert item1.ingredient_id == ingredient1_id
    assert item1.quantity == 2.0
    assert item1.unit == "lbs"
    assert item1.notes == "Carrots"

    # Check second inventory item
    item2 = store.inventory_items[1]
    assert item2.ingredient_id == ingredient2_id
    assert item2.quantity == 1.0
    assert item2.unit == "bunch"
    assert item2.notes == "Kale"


def test_ingredient_creation_generates_ingredient_created_event():
    """Test that Ingredient creation generates IngredientCreated event"""
    # Arrange
    ingredient_id = uuid.uuid4()
    name = "Carrots"
    default_unit = "lbs"

    # Act
    ingredient = Ingredient.create(
        ingredient_id=ingredient_id,
        name=name,
        default_unit=default_unit,
    )

    # Assert
    assert len(ingredient.uncommitted_events) == 1
    event = ingredient.uncommitted_events[0]
    assert isinstance(event, IngredientCreated)
    assert event.ingredient_id == ingredient_id
    assert event.name == name
    assert event.default_unit == default_unit
    assert isinstance(event.created_at, datetime)
