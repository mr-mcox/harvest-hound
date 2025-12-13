"""
Pydantic schemas for API request/response models
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

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


class InventoryItemUpdate(BaseModel):
    """Request schema for updating inventory item (partial updates)"""

    quantity: float | None = None
    priority: Priority | None = None


# --- Flesh-Out Schemas ---


class PitchToFleshOut(BaseModel):
    """A pitch selected for flesh-out"""

    name: str
    blurb: str
    inventory_ingredients: list[dict]  # [{name, quantity, unit}]
    criterion_id: UUID  # Which criterion this pitch belongs to


class FleshOutRequest(BaseModel):
    """Request schema for batch flesh-out of selected pitches"""

    pitches: list[PitchToFleshOut]


class ClaimSummary(BaseModel):
    """Summary of an ingredient claim created during flesh-out"""

    ingredient_name: str
    quantity: float
    unit: str
    inventory_item_id: int


class RecipeIngredientResponse(BaseModel):
    """Recipe ingredient in response"""

    name: str
    quantity: str
    unit: str
    preparation: str | None = None
    notes: str | None = None
    purchase_likelihood: float = 0.5  # 0.0-1.0, LLM confidence needs purchase


class FleshedOutRecipe(BaseModel):
    """A recipe generated from flesh-out with claim summary"""

    id: str  # UUID as string
    criterion_id: str | None = None  # UUID as string, links to meal criterion
    name: str
    description: str
    ingredients: list[RecipeIngredientResponse]
    instructions: list[str]
    active_time_minutes: int
    total_time_minutes: int
    servings: int
    notes: str | None
    state: str = "planned"  # Recipe state (planned, cooked, abandoned)
    claims: list[ClaimSummary]  # Claims created for inventory items


class FleshOutResponse(BaseModel):
    """Response schema for flesh-out endpoint"""

    recipes: list[FleshedOutRecipe]
    errors: list[str]  # Any pitches that failed to flesh out


# --- Recipe Lifecycle Schemas ---


class RecipeLifecycleResponse(BaseModel):
    """Response schema for recipe lifecycle actions (cook/abandon)"""

    recipe_id: str  # UUID as string
    new_state: str  # RecipeState value
    claims_deleted: int
    inventory_items_decremented: int  # Only for cook action, 0 for abandon
