"""
Tests for database seeding logic
"""

from sqlmodel import select

from models import GroceryStore, HouseholdProfile, Pantry, seed_defaults


def test_seed_creates_defaults_on_empty_db(session):
    """Seeding an empty database creates all three config types"""
    # Verify database is empty
    assert session.exec(select(HouseholdProfile)).first() is None
    assert session.exec(select(Pantry)).first() is None
    assert session.exec(select(GroceryStore)).first() is None

    # Run seeding
    seed_defaults(session)

    # Verify all configs exist
    household = session.exec(select(HouseholdProfile)).first()
    assert household is not None
    assert "household" in household.content.lower() or len(household.content) > 0

    pantry = session.exec(select(Pantry)).first()
    assert pantry is not None
    assert "pantry" in pantry.content.lower() or len(pantry.content) > 0

    stores = session.exec(select(GroceryStore)).all()
    assert len(stores) == 1
    assert stores[0].name is not None


def test_seed_is_idempotent(session):
    """Running seed twice doesn't duplicate records"""
    # Seed once
    seed_defaults(session)

    # Count records
    household_count_1 = len(session.exec(select(HouseholdProfile)).all())
    pantry_count_1 = len(session.exec(select(Pantry)).all())
    store_count_1 = len(session.exec(select(GroceryStore)).all())

    # Seed again
    seed_defaults(session)

    # Count should be the same
    household_count_2 = len(session.exec(select(HouseholdProfile)).all())
    pantry_count_2 = len(session.exec(select(Pantry)).all())
    store_count_2 = len(session.exec(select(GroceryStore)).all())

    assert household_count_1 == household_count_2 == 1
    assert pantry_count_1 == pantry_count_2 == 1
    assert store_count_1 == store_count_2 == 1
