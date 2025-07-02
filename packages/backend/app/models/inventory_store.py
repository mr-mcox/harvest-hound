from typing import List
from uuid import UUID

from pydantic import BaseModel, Field

from .inventory_item import InventoryItem


class InventoryStore(BaseModel):
    store_id: UUID
    name: str
    description: str = ""
    infinite_supply: bool = False
    inventory_items: List[InventoryItem] = Field(default_factory=list)
