"""
Read model classes for denormalized views.

These models provide flat, denormalized data structures optimized for UI consumption
as per ADR-005. They eliminate the need for frontend joins and follow the CQRS pattern.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class InventoryItemView(BaseModel):
    """
    Denormalized read model for inventory items with ingredient and store names.
    
    Optimized for UI consumption with flat structure and computed properties.
    """
    
    # Core identifiers
    store_id: UUID
    ingredient_id: UUID
    
    # Denormalized for UI convenience (no deep hierarchies)
    ingredient_name: str
    store_name: str
    
    # Inventory data
    quantity: float
    unit: str
    notes: Optional[str] = None
    added_at: datetime
    
    # Computed fields for common UI patterns
    @property
    def display_name(self) -> str:
        """Format item for display in UI components."""
        return f"{self.quantity} {self.unit} {self.ingredient_name}"


class StoreView(BaseModel):
    """
    Denormalized read model for inventory stores with computed fields.
    
    Includes computed item_count for efficient store listing views.
    """
    
    store_id: UUID
    name: str
    description: str = ""
    infinite_supply: bool = False
    item_count: int = 0
    created_at: datetime