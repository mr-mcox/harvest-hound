"""
Pure functions for domain operations that generate events.

These functions implement the core business logic while maintaining
separation of concerns from infrastructure. Each function returns
a tuple of (aggregate, events) for explicit event handling.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Tuple, Union
from uuid import UUID

from ..events import DomainEvent, IngredientCreated, InventoryItemAdded, StoreCreated

if TYPE_CHECKING:
    from ..models import Ingredient, InventoryStore


def create_inventory_store(
    store_id: UUID,
    name: str,
    description: str = "",
    infinite_supply: bool = False,
) -> Tuple["InventoryStore", List[DomainEvent]]:
    """Create a new InventoryStore and generate StoreCreated event."""
    from ..models.inventory_store import InventoryStore

    created_at = datetime.now()

    store = InventoryStore(
        store_id=store_id,
        name=name,
        description=description,
        infinite_supply=infinite_supply,
        inventory_items=[],
    )

    event = StoreCreated(
        store_id=store_id,
        name=name,
        description=description,
        infinite_supply=infinite_supply,
        created_at=created_at,
    )

    return store, [event]


def add_inventory_item_to_store(
    store: "InventoryStore",
    ingredient_id: UUID,
    quantity: float,
    unit: str,
    notes: str | None = None,
) -> Tuple["InventoryStore", List[DomainEvent]]:
    """Add an inventory item to store and generate InventoryItemAdded event."""
    from ..models.inventory_item import InventoryItem

    added_at = datetime.now()

    # Create the inventory item
    inventory_item = InventoryItem(
        store_id=store.store_id,
        ingredient_id=ingredient_id,
        quantity=quantity,
        unit=unit,
        notes=notes,
        added_at=added_at,
    )

    # Create updated store with new item
    updated_store = store.model_copy()
    updated_store.inventory_items.append(inventory_item)

    # Generate the event
    event = InventoryItemAdded(
        store_id=store.store_id,
        ingredient_id=ingredient_id,
        quantity=quantity,
        unit=unit,
        notes=notes,
        added_at=added_at,
    )

    return updated_store, [event]


def create_ingredient(
    ingredient_id: UUID,
    name: str,
    default_unit: str,
) -> Tuple["Ingredient", List[DomainEvent]]:
    """Create a new Ingredient and generate IngredientCreated event."""
    from ..models.ingredient import Ingredient

    created_at = datetime.now()

    ingredient = Ingredient(
        ingredient_id=ingredient_id,
        name=name,
        default_unit=default_unit,
        created_at=created_at,
    )

    event = IngredientCreated(
        ingredient_id=ingredient_id,
        name=name,
        default_unit=default_unit,
        created_at=created_at,
    )

    return ingredient, [event]


def rebuild_inventory_store_from_events(
    events: List[Union[StoreCreated, InventoryItemAdded]],
) -> "InventoryStore":
    """Rebuild InventoryStore from a sequence of events."""
    from ..models.inventory_item import InventoryItem
    from ..models.inventory_store import InventoryStore

    store = None

    for event in events:
        if isinstance(event, StoreCreated):
            # Initialize the store from StoreCreated event
            store = InventoryStore(
                store_id=event.store_id,
                name=event.name,
                description=event.description,
                infinite_supply=event.infinite_supply,
                inventory_items=[],
            )
        elif isinstance(event, InventoryItemAdded):
            # Add inventory item from InventoryItemAdded event
            if store is None:
                raise ValueError("InventoryItemAdded event without StoreCreated event")

            inventory_item = InventoryItem(
                store_id=event.store_id,
                ingredient_id=event.ingredient_id,
                quantity=event.quantity,
                unit=event.unit,
                notes=event.notes,
                added_at=event.added_at,
            )

            store.inventory_items.append(inventory_item)

    if store is None:
        raise ValueError("No StoreCreated event found in event sequence")

    return store
