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
