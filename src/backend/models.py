"""
Database setup and models for Harvest Hound

Database location is controlled by DATABASE_URL environment variable:
- Default: sqlite:///dev.db (safe for testing/Claude)
- Live mode: ./dev script sets DATABASE_URL=sqlite:///harvest.db
- Tests: Uses in-memory database via conftest.py fixtures
"""

import os
from collections.abc import Generator
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, field_validator
from sqlalchemy import JSON, Column, event
from sqlmodel import Field, Session, SQLModel, create_engine, select, text


def _utc_now() -> datetime:
    """Return current UTC time (timezone-aware)"""
    return datetime.now(UTC)


DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///dev.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)


# Enable foreign key support for SQLite (required for CASCADE deletes)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class HouseholdProfile(SQLModel, table=True):
    """Singleton config for household cooking context used in recipe generation"""

    id: int | None = Field(default=None, primary_key=True)
    content: str = Field(default="")
    updated_at: datetime = Field(default_factory=_utc_now)


class Pantry(SQLModel, table=True):
    """Singleton config for pantry staples (unlimited, unclaimed)"""

    id: int | None = Field(default=None, primary_key=True)
    content: str = Field(default="")
    updated_at: datetime = Field(default_factory=_utc_now)


class GroceryStore(SQLModel, table=True):
    """Shopping destination for grocery list claims"""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field()
    description: str = Field(default="")
    created_at: datetime = Field(default_factory=_utc_now)


class InventoryItem(SQLModel, table=True):
    """Tracked inventory item from CSA delivery or other source"""

    id: int | None = Field(default=None, primary_key=True)
    store_id: int = Field(foreign_key="grocerystore.id")
    ingredient_name: str = Field()
    quantity: float = Field()
    unit: str = Field()
    priority: str = Field(default="medium")  # low, medium, high, urgent
    portion_size: str | None = Field(default=None)  # e.g., "1 pound", "16 ounce"
    added_at: datetime = Field(default_factory=_utc_now)


class PlanningSession(SQLModel, table=True):
    """Weekly meal planning session for organizing recipe generation by criteria"""

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field()
    created_at: datetime = Field(default_factory=_utc_now)


class MealCriterion(SQLModel, table=True):
    """Meal constraint/category for structured planning (e.g., 'Quick weeknight')"""

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="planningsession.id", ondelete="CASCADE")
    description: str = Field()
    slots: int = Field()  # Number of meal slots (min 1)
    created_at: datetime = Field(default_factory=_utc_now)

    @field_validator("slots")
    @classmethod
    def validate_slots(cls, v: int) -> int:
        if v < 1:
            raise ValueError("slots must be at least 1")
        return v


class PitchIngredient:
    """Ingredient claimed by a pitch with quantity for inventory tracking"""

    name: str
    quantity: float
    unit: str


class Pitch(SQLModel, table=True):
    """Lightweight recipe pitch generated for a specific meal criterion"""

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    criterion_id: UUID = Field(foreign_key="mealcriterion.id", ondelete="CASCADE")
    name: str = Field()
    blurb: str = Field()  # Emotional hook
    why_make_this: str = Field()  # Justification (CSA usage, etc.)
    inventory_ingredients: list[dict] = Field(
        default_factory=list, sa_column=Column(JSON)
    )  # List of {name, quantity, unit} dicts
    active_time_minutes: int = Field()
    created_at: datetime = Field(default_factory=_utc_now)


class RecipeIngredient(BaseModel):
    """Structured ingredient with preparation field for shopping list clarity"""

    name: str
    quantity: str  # String to handle ranges ("2-3"), "to taste", etc.
    unit: str
    preparation: str | None = None  # e.g., "diced", "minced", "julienned"
    notes: str | None = None  # e.g., "organic preferred"


class RecipeState(str, Enum):
    """Recipe lifecycle states"""

    PLANNED = "planned"
    COOKED = "cooked"
    ABANDONED = "abandoned"


class ClaimState(str, Enum):
    """Ingredient claim lifecycle states"""

    RESERVED = "reserved"  # Ingredient reserved for planned recipe
    CONSUMED = "consumed"  # Recipe cooked, ingredient used


class Recipe(SQLModel, table=True):
    """Complete recipe with structured ingredients, generated from a pitch"""

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    criterion_id: UUID | None = Field(default=None)  # Optional link to meal criterion
    name: str = Field()
    description: str = Field()
    ingredients: list[dict] = Field(
        default_factory=list, sa_column=Column(JSON)
    )  # List of RecipeIngredient dicts
    instructions: list[str] = Field(
        default_factory=list, sa_column=Column(JSON)
    )  # Ordered steps
    active_time_minutes: int = Field()
    total_time_minutes: int = Field()
    servings: int = Field()
    state: RecipeState = Field(default=RecipeState.PLANNED)
    notes: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=_utc_now)


class IngredientClaim(SQLModel, table=True):
    """Reservation of inventory item quantity for a planned recipe"""

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    recipe_id: UUID = Field(foreign_key="recipe.id", ondelete="CASCADE")
    inventory_item_id: int = Field(foreign_key="inventoryitem.id", ondelete="CASCADE")
    ingredient_name: str = Field()  # Denormalized for display without joins
    quantity: float = Field()
    unit: str = Field()
    state: ClaimState = Field(default=ClaimState.RESERVED)
    created_at: datetime = Field(default_factory=_utc_now)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions"""
    with Session(engine) as session:
        yield session


def db_health() -> bool:
    """Health check - verify database connectivity"""
    with Session(engine) as session:
        result = session.exec(text("SELECT 1"))
        row = result.one()
        return row[0] == 1


DEFAULT_HOUSEHOLD_PROFILE = """Describe your household cooking context...

Examples:
- Family of 4 with two kids (ages 5 and 8)
- Prefer quick weeknight meals (30 min or less)
- One vegetarian, others eat everything
- Kitchen has instant pot and air fryer"""

DEFAULT_PANTRY = """List your pantry staples (salt, pepper, olive oil, etc.)...

These are ingredients you always have on hand and don't need to buy.
They won't appear on shopping lists.

Examples:
- Salt, pepper, garlic powder
- Olive oil, vegetable oil
- Soy sauce, fish sauce
- Rice, pasta, flour"""


def seed_defaults(session: Session) -> None:
    """Seed default configuration if database is empty. Idempotent."""
    if session.exec(select(HouseholdProfile)).first() is None:
        session.add(HouseholdProfile(content=DEFAULT_HOUSEHOLD_PROFILE))

    if session.exec(select(Pantry)).first() is None:
        session.add(Pantry(content=DEFAULT_PANTRY))

    if session.exec(select(GroceryStore)).first() is None:
        session.add(
            GroceryStore(
                name="Grocery Store",
                description="Default grocery store for shopping lists",
            )
        )

    session.commit()


SQLModel.metadata.create_all(engine)
with Session(engine) as _session:
    seed_defaults(_session)
