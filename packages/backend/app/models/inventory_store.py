from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Self, Sequence, Tuple, Union
from uuid import UUID

from pydantic import BaseModel, Field

from ..events import InventoryItemAdded, StoreCreated
from .inventory_item import InventoryItem


class InventoryStore(BaseModel, ABC):
    """
    Abstract base class for inventory stores.

    Defines common interface for different store types:
    - ExplicitInventoryStore: Enumerated inventory with tracked quantities
    - DefinitionBasedStore: LLM-inferred availability from natural language

    All state mutations return (updated_aggregate, events) tuples
    for explicit event tracking without infrastructure concerns.
    """

    store_id: UUID
    name: str
    description: str = ""

    @abstractmethod
    def check_availability(
        self, ingredient_id: UUID, quantity: float, unit: str
    ) -> bool:
        """Check if ingredient is available in this store."""
        pass

    @classmethod
    @abstractmethod
    def from_events(
        cls, events: Sequence[Union[StoreCreated, InventoryItemAdded]]
    ) -> Self:
        """Rebuild store from a sequence of events."""
        pass


class ExplicitInventoryStore(InventoryStore):
    """
    Inventory store with explicit enumerated inventory.

    Tracks specific quantities of ingredients. Inventory must be
    explicitly added and is finite.
    """

    inventory_items: List[InventoryItem] = Field(default_factory=list)

    def check_availability(
        self, ingredient_id: UUID, quantity: float, unit: str
    ) -> bool:
        """Check if ingredient is available in explicit inventory."""
        for item in self.inventory_items:
            if item.ingredient_id == ingredient_id and item.unit == unit:
                return item.quantity >= quantity
        return False

    @classmethod
    def create(
        cls,
        store_id: UUID,
        name: str,
        description: str = "",
    ) -> Tuple[Self, List[StoreCreated]]:
        """Create a new ExplicitInventoryStore and generate StoreCreated event."""
        created_at = datetime.now()

        store = cls(
            store_id=store_id,
            name=name,
            description=description,
            inventory_items=[],
        )

        event = StoreCreated(
            store_id=store_id,
            name=name,
            description=description,
            store_type="explicit",
            created_at=created_at,
        )

        return store, [event]

    def add_inventory_item(
        self,
        ingredient_id: UUID,
        quantity: float,
        unit: str,
        notes: str | None = None,
    ) -> Tuple[Self, List[InventoryItemAdded]]:
        """Add an inventory item to the store and generate InventoryItemAdded event."""
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

        # Create updated store with new item
        updated_store = self.model_copy()
        updated_store.inventory_items.append(inventory_item)

        # Generate the event
        event = InventoryItemAdded(
            store_id=self.store_id,
            ingredient_id=ingredient_id,
            quantity=quantity,
            unit=unit,
            notes=notes,
            added_at=added_at,
        )

        return updated_store, [event]

    @classmethod
    def from_events(
        cls, events: Sequence[Union[StoreCreated, InventoryItemAdded]]
    ) -> Self:
        """Rebuild ExplicitInventoryStore from a sequence of events."""
        store = None

        for event in events:
            if isinstance(event, StoreCreated):
                # Initialize the store from StoreCreated event
                store = cls(
                    store_id=event.store_id,
                    name=event.name,
                    description=event.description,
                    inventory_items=[],
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

        return store


class DefinitionBasedStore(InventoryStore):
    """
    Inventory store with LLM-inferred availability.

    Uses natural language definition to describe what ingredients
    are available. Availability is determined by LLM inference.

    Note: Does not support add_inventory_item() - that method is only
    available on ExplicitInventoryStore.
    """

    definition: str = Field(
        ..., description="Natural language description of available ingredients"
    )

    def check_availability(
        self, ingredient_id: UUID, quantity: float, unit: str
    ) -> bool:
        """Check availability via LLM inference (stubbed for now)."""
        # TODO: Implement LLM-based availability check
        # For now, return False as a stub
        return False

    @classmethod
    def create(
        cls,
        store_id: UUID,
        name: str,
        definition: str,
        description: str = "",
    ) -> Tuple[Self, List[StoreCreated]]:
        """Create a new DefinitionBasedStore and generate StoreCreated event."""
        created_at = datetime.now()

        store = cls(
            store_id=store_id,
            name=name,
            description=description,
            definition=definition,
        )

        event = StoreCreated(
            store_id=store_id,
            name=name,
            description=description,
            store_type="definition",
            definition=definition,
            created_at=created_at,
        )

        return store, [event]

    @classmethod
    def from_events(
        cls, events: Sequence[Union[StoreCreated, InventoryItemAdded]]
    ) -> Self:
        """Rebuild DefinitionBasedStore from a sequence of events."""
        store = None

        for event in events:
            if isinstance(event, StoreCreated):
                # Initialize the store from StoreCreated event
                if not hasattr(event, "definition") or event.definition is None:
                    raise ValueError(
                        "StoreCreated event for DefinitionBasedStore must have "
                        "definition field"
                    )

                store = cls(
                    store_id=event.store_id,
                    name=event.name,
                    description=event.description,
                    definition=event.definition,
                )
            elif isinstance(event, InventoryItemAdded):
                # DefinitionBasedStore should not have inventory items
                raise ValueError(
                    "DefinitionBasedStore cannot process InventoryItemAdded events"
                )

        if store is None:
            raise ValueError("No StoreCreated event found in event sequence")

        return store


# Factory function for polymorphic store creation from events
def inventory_store_from_events(
    events: Sequence[Union[StoreCreated, InventoryItemAdded]],
) -> Union[ExplicitInventoryStore, DefinitionBasedStore]:
    """
    Factory function to create the correct store type from events.

    Inspects the StoreCreated event's store_type discriminator to
    determine which subclass to instantiate.
    """
    if not events:
        raise ValueError("No events provided")

    # Find the StoreCreated event to determine store type
    store_created_event = None
    for event in events:
        if isinstance(event, StoreCreated):
            store_created_event = event
            break

    if store_created_event is None:
        raise ValueError("No StoreCreated event found in event sequence")

    # Route to correct subclass based on discriminator
    store_type = getattr(store_created_event, "store_type", "explicit")

    if store_type == "explicit":
        return ExplicitInventoryStore.from_events(events)
    elif store_type == "definition":
        return DefinitionBasedStore.from_events(events)
    else:
        raise ValueError(f"Unknown store type: {store_type}")
