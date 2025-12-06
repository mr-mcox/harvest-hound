"""
Database setup and models for Harvest Hound
"""

from collections.abc import Generator
from datetime import UTC, datetime

from sqlmodel import Field, Session, SQLModel, create_engine, select, text


def _utc_now() -> datetime:
    """Return current UTC time (timezone-aware)"""
    return datetime.now(UTC)


engine = create_engine("sqlite:///harvest.db")


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
