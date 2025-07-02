from typing import List, Union
from uuid import UUID

from ..events.domain_events import (
    DomainEvent,
    IngredientCreated,
    InventoryItemAdded,
    StoreCreated,
)
from ..models.ingredient import Ingredient
from ..models.inventory_store import InventoryStore
from .event_store import EventStore


class RepositoryError(Exception):
    """Base exception for repository operations."""

    pass


class AggregateNotFoundError(RepositoryError):
    """Raised when trying to load an aggregate that doesn't exist."""

    pass


class IngredientRepository:
    """Repository for Ingredient aggregates using event sourcing."""

    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    def save(self, ingredient: Ingredient, events: List[DomainEvent]) -> None:
        """Save ingredient by persisting its events."""
        stream_id = f"ingredient-{ingredient.ingredient_id}"
        for event in events:
            self.event_store.append_event(stream_id, event)

    def load(self, ingredient_id: UUID) -> Ingredient:
        """Load ingredient from its event stream."""
        stream_id = f"ingredient-{ingredient_id}"
        event_dicts = self.event_store.load_events(stream_id)

        if not event_dicts:
            raise AggregateNotFoundError(
                f"Ingredient with ID {ingredient_id} not found"
            )

        # Convert event dictionaries back to domain events
        events = []
        for event_dict in event_dicts:
            if event_dict["event_type"] == "IngredientCreated":
                event = IngredientCreated(**event_dict["event_data"])
                events.append(event)
            else:
                raise ValueError(f"Unknown event type: {event_dict['event_type']}")

        return Ingredient.from_events(events)


class StoreRepository:
    """Repository for InventoryStore aggregates using event sourcing."""

    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    def save(self, store: InventoryStore, events: List[DomainEvent]) -> None:
        """Save store by persisting its events."""
        stream_id = f"store-{store.store_id}"
        for event in events:
            self.event_store.append_event(stream_id, event)

    def load(self, store_id: UUID) -> InventoryStore:
        """Load store from its event stream."""
        stream_id = f"store-{store_id}"
        event_dicts = self.event_store.load_events(stream_id)

        if not event_dicts:
            raise AggregateNotFoundError(f"Store with ID {store_id} not found")

        # Convert event dictionaries back to domain events
        events: List[Union[StoreCreated, InventoryItemAdded]] = []
        for event_dict in event_dicts:
            if event_dict["event_type"] == "StoreCreated":
                store_event = StoreCreated(**event_dict["event_data"])
                events.append(store_event)
            elif event_dict["event_type"] == "InventoryItemAdded":
                item_event = InventoryItemAdded(**event_dict["event_data"])
                events.append(item_event)
            else:
                raise ValueError(f"Unknown event type: {event_dict['event_type']}")

        return InventoryStore.from_events(events)
