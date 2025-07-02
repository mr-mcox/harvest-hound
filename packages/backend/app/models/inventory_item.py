from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class InventoryItem(BaseModel):
    store_id: UUID
    ingredient_id: UUID
    quantity: float
    unit: str
    notes: Optional[str] = None
    added_at: datetime
