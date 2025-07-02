from datetime import datetime
from typing import List, Tuple
from uuid import UUID

from pydantic import BaseModel

from ..domain.operations import create_ingredient
from ..events import DomainEvent


class Ingredient(BaseModel):
    """
    Clean domain model for ingredients.

    All state mutations are handled via pure functions that return
    (updated_aggregate, events) tuples for explicit event tracking.
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
    ) -> Tuple["Ingredient", List[DomainEvent]]:
        """Create a new Ingredient and generate IngredientCreated event."""
        return create_ingredient(ingredient_id, name, default_unit)
