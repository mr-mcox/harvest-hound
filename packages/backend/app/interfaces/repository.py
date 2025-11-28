"""Repository interface protocols."""

from typing import Protocol, Sequence
from uuid import UUID

from ..events.domain_events import DomainEvent
from ..models.ingredient import Ingredient
from ..models.inventory_store import InventoryStore


class StoreRepositoryProtocol(Protocol):
    """Protocol for store repository operations."""

    def save(self, store: InventoryStore, events: Sequence[DomainEvent]) -> None:
        """Save store aggregate and publish events.

        Args:
            store: The inventory store aggregate
            events: Domain events to publish
        """
        ...

    def load(self, store_id: UUID) -> InventoryStore:
        """Load store aggregate by ID.

        Args:
            store_id: Unique identifier for the store

        Returns:
            The reconstructed store aggregate

        Raises:
            AggregateNotFoundError: If store doesn't exist
        """
        ...


class IngredientRepositoryProtocol(Protocol):
    """Protocol for ingredient repository operations."""

    def save(self, ingredient: Ingredient, events: Sequence[DomainEvent]) -> None:
        """Save ingredient aggregate and publish events.

        Args:
            ingredient: The ingredient aggregate
            events: Domain events to publish
        """
        ...

    def load(self, ingredient_id: UUID) -> Ingredient:
        """Load ingredient aggregate by ID.

        Args:
            ingredient_id: Unique identifier for the ingredient

        Returns:
            The reconstructed ingredient aggregate

        Raises:
            AggregateNotFoundError: If ingredient doesn't exist
        """
        ...
