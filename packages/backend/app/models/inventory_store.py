from typing import List, Tuple, Union
from uuid import UUID

from pydantic import BaseModel, Field

from ..domain.operations import (
    add_inventory_item_to_store,
    create_inventory_store,
    rebuild_inventory_store_from_events,
)
from ..events import DomainEvent, InventoryItemAdded, StoreCreated
from .inventory_item import InventoryItem


class InventoryStore(BaseModel):
    """
    Clean domain model for inventory stores.

    All state mutations are handled via pure functions that return
    (updated_aggregate, events) tuples for explicit event tracking.
    """

    store_id: UUID
    name: str
    description: str = ""
    infinite_supply: bool = False
    inventory_items: List[InventoryItem] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        store_id: UUID,
        name: str,
        description: str = "",
        infinite_supply: bool = False,
    ) -> Tuple["InventoryStore", List[DomainEvent]]:
        """Create a new InventoryStore and generate StoreCreated event."""
        return create_inventory_store(store_id, name, description, infinite_supply)

    def add_inventory_item(
        self,
        ingredient_id: UUID,
        quantity: float,
        unit: str,
        notes: str | None = None,
    ) -> Tuple["InventoryStore", List[DomainEvent]]:
        """Add an inventory item to the store and generate InventoryItemAdded event."""
        return add_inventory_item_to_store(self, ingredient_id, quantity, unit, notes)

    @classmethod
    def from_events(
        cls, events: List[Union[StoreCreated, InventoryItemAdded]]
    ) -> "InventoryStore":
        """Rebuild InventoryStore from a sequence of events."""
        return rebuild_inventory_store_from_events(events)
