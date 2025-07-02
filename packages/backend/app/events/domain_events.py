from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class StoreCreated(BaseModel):
    store_id: UUID
    name: str
    description: str
    infinite_supply: bool
    created_at: datetime


class IngredientCreated(BaseModel):
    ingredient_id: UUID
    name: str
    default_unit: str
    created_at: datetime


class InventoryItemAdded(BaseModel):
    store_id: UUID
    ingredient_id: UUID
    quantity: float
    unit: str
    notes: Optional[str] = None
    added_at: datetime
