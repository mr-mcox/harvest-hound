from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DomainEvent(BaseModel):
    """Base class for all domain events."""

    pass


class StoreCreated(DomainEvent):
    store_id: UUID
    name: str
    description: str
    store_type: str  # Discriminator: "explicit" or "definition"
    definition: Optional[str] = None  # Required for definition-based stores
    created_at: datetime


class IngredientCreated(DomainEvent):
    ingredient_id: UUID
    name: str
    default_unit: str
    created_at: datetime


class InventoryItemAdded(DomainEvent):
    store_id: UUID
    ingredient_id: UUID
    quantity: float
    unit: str
    notes: Optional[str] = None
    added_at: datetime


class StoreCreatedWithInventory(DomainEvent):
    store_id: UUID
    successful_items: int
    error_message: Optional[str] = None
