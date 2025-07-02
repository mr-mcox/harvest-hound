from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Ingredient(BaseModel):
    ingredient_id: UUID
    name: str
    default_unit: str
    created_at: datetime
