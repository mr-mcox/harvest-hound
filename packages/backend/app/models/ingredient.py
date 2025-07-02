from datetime import datetime
from typing import Any, List
from uuid import UUID

from pydantic import BaseModel, Field

from ..events import IngredientCreated


class Ingredient(BaseModel):
    ingredient_id: UUID
    name: str
    default_unit: str
    created_at: datetime
    uncommitted_events: List[Any] = Field(default_factory=list, exclude=True)

    @classmethod
    def create(
        cls,
        ingredient_id: UUID,
        name: str,
        default_unit: str,
    ) -> "Ingredient":
        """Create a new Ingredient and generate IngredientCreated event"""
        created_at = datetime.now()

        ingredient = cls(
            ingredient_id=ingredient_id,
            name=name,
            default_unit=default_unit,
            created_at=created_at,
        )

        event = IngredientCreated(
            ingredient_id=ingredient_id,
            name=name,
            default_unit=default_unit,
            created_at=created_at,
        )

        ingredient.uncommitted_events.append(event)
        return ingredient
