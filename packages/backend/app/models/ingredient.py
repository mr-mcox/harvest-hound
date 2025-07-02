from datetime import datetime
from typing import List, Self, Tuple
from uuid import UUID

from pydantic import BaseModel

from ..events import DomainEvent, IngredientCreated


class Ingredient(BaseModel):
    """
    Clean domain model for ingredients.

    All state mutations return (updated_aggregate, events) tuples
    for explicit event tracking without infrastructure concerns.
    """

    ingredient_id: UUID
    name: str
    default_unit: str
    created_at: datetime

    @classmethod
    def create(
        cls,
        ingredient_id: UUID,
        name: str,
        default_unit: str,
    ) -> Tuple[Self, List[DomainEvent]]:
        """Create a new Ingredient and generate IngredientCreated event."""
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

        return ingredient, [event]
