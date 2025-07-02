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

    @classmethod
    def from_events(cls, events: List[IngredientCreated]) -> Self:
        """Rebuild Ingredient from a sequence of events."""
        if not events:
            raise ValueError("No events provided to rebuild Ingredient")

        # For Ingredient, we only expect IngredientCreated events
        created_event = None
        for event in events:
            if isinstance(event, IngredientCreated):
                if created_event is None:
                    created_event = event
                else:
                    raise ValueError("Multiple IngredientCreated events found")
            else:
                raise ValueError(f"Unexpected event type: {type(event)}")

        if created_event is None:
            raise ValueError("No IngredientCreated event found")

        return cls(
            ingredient_id=created_event.ingredient_id,
            name=created_event.name,
            default_unit=created_event.default_unit,
            created_at=created_event.created_at,
        )
