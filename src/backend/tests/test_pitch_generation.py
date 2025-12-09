"""
Tests for smart pitch generation logic - calculating how many pitches to generate
"""

from sqlmodel import Session

from models import (
    GroceryStore,
    InventoryItem,
    MealCriterion,
    Pitch,
    PlanningSession,
    Recipe,
    RecipeState,
)
from services import calculate_pitch_generation_delta


def _create_session(db: Session) -> PlanningSession:
    """Helper to create a planning session"""
    session = PlanningSession(name="Test Session")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def _create_criterion(
    db: Session, session: PlanningSession, description: str, slots: int
) -> MealCriterion:
    """Helper to create a meal criterion"""
    criterion = MealCriterion(
        session_id=session.id,
        description=description,
        slots=slots,
    )
    db.add(criterion)
    db.commit()
    db.refresh(criterion)
    return criterion


def _create_recipe(
    db: Session, session: PlanningSession, criterion: MealCriterion, name: str
) -> Recipe:
    """Helper to create a planned recipe"""
    recipe = Recipe(
        session_id=session.id,
        criterion_id=criterion.id,
        name=name,
        description="Test recipe",
        ingredients=[{"name": "test", "quantity": "1", "unit": "test"}],
        instructions=["Test"],
        active_time_minutes=10,
        total_time_minutes=20,
        servings=2,
        state=RecipeState.PLANNED,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


def _create_store_with_inventory(
    db: Session, ingredient_name: str, quantity: float, unit: str
) -> tuple[GroceryStore, InventoryItem]:
    """Helper to create store with inventory item"""
    store = GroceryStore(name="Test Store", description="Test")
    db.add(store)
    db.commit()
    db.refresh(store)

    item = InventoryItem(
        store_id=store.id,
        ingredient_name=ingredient_name,
        quantity=quantity,
        unit=unit,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return store, item


def _create_pitch(
    db: Session,
    criterion: MealCriterion,
    name: str,
    ingredients: list[dict],
) -> Pitch:
    """Helper to create a pitch"""
    pitch = Pitch(
        criterion_id=criterion.id,
        name=name,
        blurb="Test pitch",
        why_make_this="Testing",
        inventory_ingredients=ingredients,
        active_time_minutes=15,
    )
    db.add(pitch)
    db.commit()
    db.refresh(pitch)
    return pitch


class TestCalculatePitchGenerationDelta:
    """Tests for calculate_pitch_generation_delta() function"""

    def test_first_generation_no_recipes_no_pitches(self, session: Session):
        """First generation: 3 slots → should generate 9 pitches (3 per slot)"""
        planning_session = _create_session(session)
        _create_criterion(session, planning_session, "Quick meals", slots=3)

        delta = calculate_pitch_generation_delta(session, planning_session.id)

        # 3 slots * 3 pitches per slot = 9 total pitches needed
        assert delta == 9

    def test_multiple_criteria_no_recipes_no_pitches(self, session: Session):
        """Multiple criteria: slots add up across all criteria"""
        planning_session = _create_session(session)
        _create_criterion(session, planning_session, "Quick meals", slots=2)
        _create_criterion(session, planning_session, "Weekend cooking", slots=1)

        delta = calculate_pitch_generation_delta(session, planning_session.id)

        # (2 + 1) slots * 3 pitches per slot = 9 total
        assert delta == 9

    def test_some_recipes_no_pitches(self, session: Session):
        """Some slots filled: should only generate for unfilled slots"""
        planning_session = _create_session(session)
        criterion = _create_criterion(session, planning_session, "Quick meals", slots=3)

        # Fill 1 out of 3 slots
        _create_recipe(session, planning_session, criterion, "Recipe 1")

        delta = calculate_pitch_generation_delta(session, planning_session.id)

        # 2 unfilled slots * 3 pitches per slot = 6 pitches
        assert delta == 6

    def test_all_slots_filled_returns_zero(self, session: Session):
        """All slots filled: should return 0 (no generation needed)"""
        planning_session = _create_session(session)
        criterion = _create_criterion(session, planning_session, "Quick meals", slots=2)

        # Fill all 2 slots
        _create_recipe(session, planning_session, criterion, "Recipe 1")
        _create_recipe(session, planning_session, criterion, "Recipe 2")

        delta = calculate_pitch_generation_delta(session, planning_session.id)

        assert delta == 0

    def test_valid_pitches_reduce_delta(self, session: Session):
        """Valid pitches count toward target: delta = target - valid_pitches"""
        planning_session = _create_session(session)
        criterion = _create_criterion(session, planning_session, "Quick meals", slots=3)

        # Create inventory so pitches are valid
        _create_store_with_inventory(session, "carrots", 10.0, "pounds")

        # Create 5 valid pitches (target is 9, so should generate 4 more)
        for i in range(5):
            _create_pitch(
                session,
                criterion,
                f"Pitch {i}",
                [{"name": "carrots", "quantity": 1.0, "unit": "pounds"}],
            )

        delta = calculate_pitch_generation_delta(session, planning_session.id)

        # Target: 3 slots * 3 = 9
        # Valid pitches: 5
        # Delta: 9 - 5 = 4
        assert delta == 4

    def test_invalid_pitches_do_not_count(self, session: Session):
        """Invalid pitches don't count: only valid pitches reduce delta"""
        planning_session = _create_session(session)
        criterion = _create_criterion(session, planning_session, "Quick meals", slots=2)

        # Create inventory for only some pitches
        _create_store_with_inventory(session, "carrots", 5.0, "pounds")

        # Create 2 valid pitches
        _create_pitch(
            session,
            criterion,
            "Valid 1",
            [{"name": "carrots", "quantity": 1.0, "unit": "pounds"}],
        )
        _create_pitch(
            session,
            criterion,
            "Valid 2",
            [{"name": "carrots", "quantity": 1.0, "unit": "pounds"}],
        )

        # Create 3 invalid pitches (missing ingredient)
        for i in range(3):
            _create_pitch(
                session,
                criterion,
                f"Invalid {i}",
                [{"name": "potatoes", "quantity": 1.0, "unit": "pounds"}],
            )

        delta = calculate_pitch_generation_delta(session, planning_session.id)

        # Target: 2 slots * 3 = 6
        # Valid pitches: 2 (invalid pitches don't count)
        # Delta: 6 - 2 = 4
        assert delta == 4

    def test_more_pitches_than_needed_returns_zero(self, session: Session):
        """Edge case: already have more pitches than target → return 0"""
        planning_session = _create_session(session)
        criterion = _create_criterion(session, planning_session, "Quick meals", slots=1)

        # Create inventory so pitches are valid
        _create_store_with_inventory(session, "carrots", 10.0, "pounds")

        # Create 10 valid pitches (target is only 3)
        for i in range(10):
            _create_pitch(
                session,
                criterion,
                f"Pitch {i}",
                [{"name": "carrots", "quantity": 1.0, "unit": "pounds"}],
            )

        delta = calculate_pitch_generation_delta(session, planning_session.id)

        # Target: 1 slot * 3 = 3
        # Valid pitches: 10
        # Delta: max(0, 3 - 10) = 0
        assert delta == 0

    def test_zero_slots_configured_returns_zero(self, session: Session):
        """Edge case: no criteria configured → return 0"""
        planning_session = _create_session(session)
        # Don't create any criteria

        delta = calculate_pitch_generation_delta(session, planning_session.id)

        assert delta == 0

    def test_accounts_for_recipes_across_multiple_criteria(self, session: Session):
        """Recipes from any criterion reduce unfilled slots"""
        planning_session = _create_session(session)
        criterion1 = _create_criterion(
            session, planning_session, "Quick meals", slots=2
        )
        criterion2 = _create_criterion(session, planning_session, "Weekend", slots=2)

        # Fill 1 slot in criterion1
        _create_recipe(session, planning_session, criterion1, "Recipe 1")
        # Fill 1 slot in criterion2
        _create_recipe(session, planning_session, criterion2, "Recipe 2")

        delta = calculate_pitch_generation_delta(session, planning_session.id)

        # Total slots: 2 + 2 = 4
        # Fleshed recipes: 2
        # Unfilled slots: 4 - 2 = 2
        # Target: 2 * 3 = 6
        # Valid pitches: 0
        # Delta: 6 - 0 = 6
        assert delta == 6

    def test_only_planned_recipes_count_as_fleshed(self, session: Session):
        """Only PLANNED recipes reduce unfilled slots (not COOKED/ABANDONED)"""
        planning_session = _create_session(session)
        criterion = _create_criterion(session, planning_session, "Quick meals", slots=3)

        # Create 1 PLANNED recipe
        _create_recipe(session, planning_session, criterion, "Planned")

        # Create 1 COOKED recipe (shouldn't count)
        cooked = _create_recipe(session, planning_session, criterion, "Cooked")
        cooked.state = RecipeState.COOKED
        session.add(cooked)
        session.commit()

        # Create 1 ABANDONED recipe (shouldn't count)
        abandoned = _create_recipe(session, planning_session, criterion, "Abandoned")
        abandoned.state = RecipeState.ABANDONED
        session.add(abandoned)
        session.commit()

        delta = calculate_pitch_generation_delta(session, planning_session.id)

        # Total slots: 3
        # Fleshed recipes (PLANNED only): 1
        # Unfilled slots: 3 - 1 = 2
        # Target: 2 * 3 = 6
        # Valid pitches: 0
        # Delta: 6 - 0 = 6
        assert delta == 6

    def test_combined_scenario_partial_fills_with_pitches(self, session: Session):
        """Complex scenario: some recipes, some valid pitches, multiple criteria"""
        planning_session = _create_session(session)
        criterion1 = _create_criterion(
            session, planning_session, "Quick meals", slots=3
        )
        criterion2 = _create_criterion(session, planning_session, "Weekend", slots=2)

        # Fill 2 slots with recipes
        _create_recipe(session, planning_session, criterion1, "Recipe 1")
        _create_recipe(session, planning_session, criterion2, "Recipe 2")

        # Create inventory
        _create_store_with_inventory(session, "carrots", 20.0, "pounds")

        # Create 4 valid pitches
        for i in range(4):
            _create_pitch(
                session,
                criterion1,
                f"Pitch {i}",
                [{"name": "carrots", "quantity": 1.0, "unit": "pounds"}],
            )

        delta = calculate_pitch_generation_delta(session, planning_session.id)

        # Total slots: 3 + 2 = 5
        # Fleshed recipes: 2
        # Unfilled slots: 5 - 2 = 3
        # Target: 3 * 3 = 9
        # Valid pitches: 4
        # Delta: 9 - 4 = 5
        assert delta == 5
