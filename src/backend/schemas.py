"""
Pydantic schemas for API request/response models
"""

from datetime import datetime

from pydantic import BaseModel


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
