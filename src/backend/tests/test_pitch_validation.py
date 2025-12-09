"""
Tests for pitch validation logic - determining if pitches
can be made with available inventory
"""

from sqlmodel import Session

from models import GroceryStore, InventoryItem, Pitch
from services import calculate_available_inventory, filter_valid_pitches, is_pitch_valid


def _create_grocery_store(session: Session) -> GroceryStore:
    """Helper to create a grocery store for inventory items"""
    store = GroceryStore(name="CSA Box", description="Weekly delivery")
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


def _create_inventory_item(
    session: Session,
    store: GroceryStore,
    name: str,
    quantity: float,
    unit: str,
) -> InventoryItem:
    """Helper to create an inventory item"""
    item = InventoryItem(
        store_id=store.id,
        ingredient_name=name,
        quantity=quantity,
        unit=unit,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


class TestIsPitchValid:
    """Tests for is_pitch_valid() function - core validation logic"""

    def test_pitch_with_all_ingredients_available_is_valid(self, session: Session):
        """Happy path: pitch with all ingredients available in sufficient quantity"""
        store = _create_grocery_store(session)
        _create_inventory_item(session, store, "carrots", 2.0, "pounds")
        _create_inventory_item(session, store, "onions", 3.0, "whole")

        available_inventory = calculate_available_inventory(session)

        pitch = Pitch(
            name="Carrot Soup",
            blurb="Delicious soup",
            why_make_this="Use carrots",
            inventory_ingredients=[
                {"name": "carrots", "quantity": 1.5, "unit": "pounds"},
                {"name": "onions", "quantity": 2.0, "unit": "whole"},
            ],
            active_time_minutes=30,
            criterion_id=None,  # Not needed for validation
        )

        assert is_pitch_valid(pitch, available_inventory) is True

    def test_pitch_with_missing_ingredient_is_invalid(self, session: Session):
        """Pitch requires ingredient not in inventory"""
        store = _create_grocery_store(session)
        _create_inventory_item(session, store, "carrots", 2.0, "pounds")

        available_inventory = calculate_available_inventory(session)

        pitch = Pitch(
            name="Carrot Onion Soup",
            blurb="Needs onions",
            why_make_this="Use carrots and onions",
            inventory_ingredients=[
                {"name": "carrots", "quantity": 1.0, "unit": "pounds"},
                {
                    "name": "onions",
                    "quantity": 1.0,
                    "unit": "whole",
                },  # Not in inventory
            ],
            active_time_minutes=30,
            criterion_id=None,
        )

        assert is_pitch_valid(pitch, available_inventory) is False

    def test_pitch_with_unit_mismatch_is_invalid(self, session: Session):
        """Aggressive invalidation: same ingredient but different units"""
        store = _create_grocery_store(session)
        _create_inventory_item(session, store, "onions", 3.0, "whole")

        available_inventory = calculate_available_inventory(session)

        pitch = Pitch(
            name="Pickled Onions",
            blurb="Needs sliced onions",
            why_make_this="Use onions",
            inventory_ingredients=[
                {"name": "onions", "quantity": 1.0, "unit": "cups"},  # Different unit
            ],
            active_time_minutes=15,
            criterion_id=None,
        )

        assert is_pitch_valid(pitch, available_inventory) is False

    def test_pitch_with_insufficient_quantity_is_invalid(self, session: Session):
        """Pitch requires more than available quantity"""
        store = _create_grocery_store(session)
        _create_inventory_item(session, store, "carrots", 1.0, "pounds")

        available_inventory = calculate_available_inventory(session)

        pitch = Pitch(
            name="Lots of Carrots",
            blurb="Needs many carrots",
            why_make_this="Use ALL the carrots",
            inventory_ingredients=[
                {"name": "carrots", "quantity": 2.0, "unit": "pounds"},  # Not enough
            ],
            active_time_minutes=45,
            criterion_id=None,
        )

        assert is_pitch_valid(pitch, available_inventory) is False

    def test_pitch_with_exact_quantity_available_is_valid(self, session: Session):
        """Edge case: pitch uses exactly all available quantity"""
        store = _create_grocery_store(session)
        _create_inventory_item(session, store, "carrots", 2.0, "pounds")

        available_inventory = calculate_available_inventory(session)

        pitch = Pitch(
            name="Use All Carrots",
            blurb="Exactly 2 pounds",
            why_make_this="Perfect amount",
            inventory_ingredients=[
                {"name": "carrots", "quantity": 2.0, "unit": "pounds"},
            ],
            active_time_minutes=30,
            criterion_id=None,
        )

        assert is_pitch_valid(pitch, available_inventory) is True

    def test_ingredient_name_matching_is_case_insensitive(self, session: Session):
        """Case-insensitive matching: 'Black Radish' matches 'black radish'"""
        store = _create_grocery_store(session)
        _create_inventory_item(session, store, "Black Radish", 2.0, "whole")

        available_inventory = calculate_available_inventory(session)

        pitch = Pitch(
            name="Radish Salad",
            blurb="Fresh radish",
            why_make_this="Use radish",
            inventory_ingredients=[
                {"name": "black radish", "quantity": 1.0, "unit": "whole"},  # Lowercase
            ],
            active_time_minutes=10,
            criterion_id=None,
        )

        assert is_pitch_valid(pitch, available_inventory) is True

    def test_pitch_with_multiple_ingredients_all_must_be_valid(self, session: Session):
        """If ANY ingredient is invalid, the entire pitch is invalid"""
        store = _create_grocery_store(session)
        _create_inventory_item(session, store, "carrots", 5.0, "pounds")
        _create_inventory_item(session, store, "onions", 1.0, "whole")  # Only 1 onion

        available_inventory = calculate_available_inventory(session)

        pitch = Pitch(
            name="Veggie Soup",
            blurb="Needs lots of onions",
            why_make_this="Use veggies",
            inventory_ingredients=[
                {"name": "carrots", "quantity": 2.0, "unit": "pounds"},  # Valid
                {
                    "name": "onions",
                    "quantity": 3.0,
                    "unit": "whole",
                },  # Invalid (need 3, have 1)
            ],
            active_time_minutes=45,
            criterion_id=None,
        )

        assert is_pitch_valid(pitch, available_inventory) is False

    def test_pitch_with_no_ingredients_is_valid(self, session: Session):
        """Edge case: pitch with empty ingredients list"""
        _create_grocery_store(session)
        available_inventory = calculate_available_inventory(session)

        pitch = Pitch(
            name="No Ingredients Needed",
            blurb="Magic recipe",
            why_make_this="No reason",
            inventory_ingredients=[],
            active_time_minutes=0,
            criterion_id=None,
        )

        assert is_pitch_valid(pitch, available_inventory) is True

    def test_pitch_with_zero_quantity_inventory_is_invalid(self, session: Session):
        """Inventory with zero quantity should not satisfy pitch"""
        store = _create_grocery_store(session)
        _create_inventory_item(session, store, "carrots", 0.0, "pounds")

        available_inventory = calculate_available_inventory(session)

        pitch = Pitch(
            name="Carrot Dish",
            blurb="Needs carrots",
            why_make_this="Use carrots",
            inventory_ingredients=[
                {"name": "carrots", "quantity": 1.0, "unit": "pounds"},
            ],
            active_time_minutes=20,
            criterion_id=None,
        )

        assert is_pitch_valid(pitch, available_inventory) is False


class TestFilterValidPitches:
    """Tests for filter_valid_pitches() helper function"""

    def test_filters_out_invalid_pitches(self, session: Session):
        """Only pitches with all ingredients available are returned"""
        store = _create_grocery_store(session)
        _create_inventory_item(session, store, "carrots", 3.0, "pounds")
        _create_inventory_item(session, store, "onions", 2.0, "whole")

        available_inventory = calculate_available_inventory(session)

        valid_pitch = Pitch(
            name="Carrot Soup",
            blurb="Has ingredients",
            why_make_this="Use carrots",
            inventory_ingredients=[
                {"name": "carrots", "quantity": 2.0, "unit": "pounds"},
            ],
            active_time_minutes=30,
            criterion_id=None,
        )

        invalid_pitch_missing = Pitch(
            name="Potato Soup",
            blurb="Missing potatoes",
            why_make_this="Use potatoes",
            inventory_ingredients=[
                {"name": "potatoes", "quantity": 3.0, "unit": "pounds"},
            ],
            active_time_minutes=40,
            criterion_id=None,
        )

        invalid_pitch_unit_mismatch = Pitch(
            name="Onion Salad",
            blurb="Wrong units",
            why_make_this="Use onions",
            inventory_ingredients=[
                {
                    "name": "onions",
                    "quantity": 1.0,
                    "unit": "cups",
                },  # Have 'whole', need 'cups'
            ],
            active_time_minutes=10,
            criterion_id=None,
        )

        pitches = [valid_pitch, invalid_pitch_missing, invalid_pitch_unit_mismatch]
        filtered = filter_valid_pitches(pitches, available_inventory)

        assert len(filtered) == 1
        assert filtered[0].name == "Carrot Soup"

    def test_returns_all_pitches_when_all_are_valid(self, session: Session):
        """When inventory is abundant, all pitches are valid"""
        store = _create_grocery_store(session)
        _create_inventory_item(session, store, "carrots", 10.0, "pounds")
        _create_inventory_item(session, store, "onions", 10.0, "whole")

        available_inventory = calculate_available_inventory(session)

        pitch1 = Pitch(
            name="Carrot Soup",
            blurb="Soup",
            why_make_this="Use carrots",
            inventory_ingredients=[
                {"name": "carrots", "quantity": 2.0, "unit": "pounds"}
            ],
            active_time_minutes=30,
            criterion_id=None,
        )

        pitch2 = Pitch(
            name="Onion Rings",
            blurb="Rings",
            why_make_this="Use onions",
            inventory_ingredients=[
                {"name": "onions", "quantity": 3.0, "unit": "whole"}
            ],
            active_time_minutes=20,
            criterion_id=None,
        )

        pitches = [pitch1, pitch2]
        filtered = filter_valid_pitches(pitches, available_inventory)

        assert len(filtered) == 2

    def test_returns_empty_list_when_no_pitches_are_valid(self, session: Session):
        """When inventory is empty, no pitches are valid"""
        _create_grocery_store(session)
        available_inventory = calculate_available_inventory(session)

        pitch = Pitch(
            name="Needs Ingredients",
            blurb="Can't make this",
            why_make_this="No ingredients",
            inventory_ingredients=[
                {"name": "anything", "quantity": 1.0, "unit": "pounds"}
            ],
            active_time_minutes=30,
            criterion_id=None,
        )

        pitches = [pitch]
        filtered = filter_valid_pitches(pitches, available_inventory)

        assert len(filtered) == 0

    def test_preserves_order_of_valid_pitches(self, session: Session):
        """Filter maintains original order of pitches"""
        store = _create_grocery_store(session)
        _create_inventory_item(session, store, "carrots", 10.0, "pounds")

        available_inventory = calculate_available_inventory(session)

        pitch_a = Pitch(
            name="A Recipe",
            blurb="First",
            why_make_this="A",
            inventory_ingredients=[
                {"name": "carrots", "quantity": 1.0, "unit": "pounds"}
            ],
            active_time_minutes=10,
            criterion_id=None,
        )

        pitch_b = Pitch(
            name="B Recipe",
            blurb="Second",
            why_make_this="B",
            inventory_ingredients=[
                {"name": "carrots", "quantity": 2.0, "unit": "pounds"}
            ],
            active_time_minutes=20,
            criterion_id=None,
        )

        pitch_c = Pitch(
            name="C Recipe",
            blurb="Third",
            why_make_this="C",
            inventory_ingredients=[
                {"name": "carrots", "quantity": 3.0, "unit": "pounds"}
            ],
            active_time_minutes=30,
            criterion_id=None,
        )

        pitches = [pitch_a, pitch_b, pitch_c]
        filtered = filter_valid_pitches(pitches, available_inventory)

        assert len(filtered) == 3
        assert filtered[0].name == "A Recipe"
        assert filtered[1].name == "B Recipe"
        assert filtered[2].name == "C Recipe"
