"""
Pydantic schemas for API request/response models
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Priority = Literal["Low", "Medium", "High", "Urgent"]


class SingletonConfigResponse(BaseModel):
    """Response schema for singleton config endpoints (HouseholdProfile, Pantry)"""

    content: str
    updated_at: datetime


class SingletonConfigUpdate(BaseModel):
    """Request schema for updating singleton configs"""

    content: str


class GroceryStoreCreate(BaseModel):
    """Request schema for creating a grocery store"""

    name: str
    description: str = ""


class GroceryStoreUpdate(BaseModel):
    """Request schema for updating a grocery store"""

    name: str | None = None
    description: str | None = None


class GroceryStoreResponse(BaseModel):
    """Response schema for grocery store endpoints"""

    id: int
    name: str
    description: str
    created_at: datetime


class InventoryParseRequest(BaseModel):
    """Request schema for parsing free-text inventory"""

    free_text: str
    configuration_instructions: str | None = None


class ParsedIngredient(BaseModel):
    """A single parsed ingredient from BAML (not yet saved)"""

    ingredient_name: str
    quantity: float
    unit: str
    priority: Priority
    portion_size: str | None = None


class InventoryParseResponse(BaseModel):
    """Response schema for parse endpoint"""

    ingredients: list[ParsedIngredient]
    parsing_notes: str | None = None


class InventoryBulkRequest(BaseModel):
    """Request schema for bulk saving inventory items"""

    items: list[ParsedIngredient]


class InventoryItemResponse(BaseModel):
    """Response schema for inventory item"""

    id: int
    ingredient_name: str
    quantity: float
    unit: str
    priority: Priority
    portion_size: str | None = None
    added_at: datetime
