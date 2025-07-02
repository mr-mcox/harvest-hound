from datetime import datetime
from typing import Any, List, Union
from uuid import UUID

from pydantic import BaseModel, Field

from ..events import InventoryItemAdded, StoreCreated
from .inventory_item import InventoryItem


class InventoryStore(BaseModel):
    store_id: UUID
    name: str
    description: str = ""
    infinite_supply: bool = False
    inventory_items: List[InventoryItem] = Field(default_factory=list)
    uncommitted_events: List[Any] = Field(default_factory=list, exclude=True)

    @classmethod
    def create(
        cls,
        store_id: UUID,
        name: str,
        description: str = "",
        infinite_supply: bool = False,
    ) -> "InventoryStore":
        """Create a new InventoryStore and generate StoreCreated event"""
        created_at = datetime.now()

        store = cls(
            store_id=store_id,
            name=name,
            description=description,
            infinite_supply=infinite_supply,
        )

        event = StoreCreated(
            store_id=store_id,
            name=name,
            description=description,
            infinite_supply=infinite_supply,
            created_at=created_at,
        )

        store.uncommitted_events.append(event)
        return store

    def add_inventory_item(
        self,
        ingredient_id: UUID,
        quantity: float,
        unit: str,
        notes: str | None = None,
    ) -> None:
        """Add an inventory item to the store and generate InventoryItemAdded event"""
        added_at = datetime.now()

        # Create the inventory item
        inventory_item = InventoryItem(
            store_id=self.store_id,
            ingredient_id=ingredient_id,
            quantity=quantity,
            unit=unit,
            notes=notes,
            added_at=added_at,
        )

        # Add to the store's inventory
        self.inventory_items.append(inventory_item)

        # Generate the event
        event = InventoryItemAdded(
            store_id=self.store_id,
            ingredient_id=ingredient_id,
            quantity=quantity,
            unit=unit,
            notes=notes,
            added_at=added_at,
        )

        self.uncommitted_events.append(event)

    @classmethod
    def from_events(
        cls, events: List[Union[StoreCreated, InventoryItemAdded]]
    ) -> "InventoryStore":
        """Rebuild InventoryStore from a sequence of events"""
        store = None

        for event in events:
            if isinstance(event, StoreCreated):
                # Initialize the store from StoreCreated event
                store = cls(
                    store_id=event.store_id,
                    name=event.name,
                    description=event.description,
                    infinite_supply=event.infinite_supply,
                )
            elif isinstance(event, InventoryItemAdded):
                # Add inventory item from InventoryItemAdded event
                if store is None:
                    raise ValueError(
                        "InventoryItemAdded event without StoreCreated event"
                    )

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

        # Rebuilt aggregates should not have uncommitted events
        store.uncommitted_events.clear()
        return store
