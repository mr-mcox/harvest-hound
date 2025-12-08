"""
Tests for multi-wave generation - claim-aware inventory calculation
"""

from sqlmodel import Session, select

from models import (
    ClaimState,
    GroceryStore,
    IngredientClaim,
    InventoryItem,
    Recipe,
    RecipeState,
)

# --- Test Fixtures ---


def _create_store(session: Session) -> GroceryStore:
    """Create a grocery store"""
    store = GroceryStore(name="CSA Box", description="Weekly delivery")
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


def _create_inventory(
    session: Session, store: GroceryStore, items: list[tuple[str, float, str]]
) -> list[InventoryItem]:
    """Create inventory items: [(name, quantity, unit), ...]"""
    inventory = []
    for name, qty, unit in items:
        item = InventoryItem(
            store_id=store.id,
            ingredient_name=name,
            quantity=qty,
            unit=unit,
        )
        session.add(item)
        inventory.append(item)
    session.commit()
    for item in inventory:
        session.refresh(item)
    return inventory


def _create_recipe_with_claims(
    session: Session,
    name: str,
    claims: list[tuple[InventoryItem, float, str]],
) -> Recipe:
    """Create a recipe with claims: [(inventory_item, quantity, unit), ...]"""
    recipe = Recipe(
        name=name,
        description="Test recipe",
        ingredients=[],
        instructions=["Step 1"],
        active_time_minutes=15,
        total_time_minutes=30,
        servings=4,
        state=RecipeState.PLANNED,
    )
    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    for item, qty, unit in claims:
        claim = IngredientClaim(
            recipe_id=recipe.id,
            inventory_item_id=item.id,
            ingredient_name=item.ingredient_name,
            quantity=qty,
            unit=unit,
            state=ClaimState.RESERVED,
        )
        session.add(claim)
    session.commit()

    return recipe


# --- Available Inventory Calculation Tests ---


class TestCalculateAvailableInventory:
    """Tests for calculating inventory minus reserved claims"""

    def test_no_claims_returns_full_inventory(self, session: Session):
        """With no claims, available equals physical inventory"""
        from services import calculate_available_inventory

        store = _create_store(session)
        _create_inventory(
            session,
            store,
            [
                ("carrots", 2.0, "pounds"),
                ("kale", 1.0, "bunch"),
            ],
        )

        available = calculate_available_inventory(session)

        assert len(available) == 2
        carrot_item = next(i for i in available if i.ingredient_name == "carrots")
        assert carrot_item.quantity == 2.0

    def test_claims_decrement_available_quantity(self, session: Session):
        """Reserved claims reduce available inventory"""
        from services import calculate_available_inventory

        store = _create_store(session)
        items = _create_inventory(
            session,
            store,
            [
                ("carrots", 2.0, "pounds"),
            ],
        )

        # Claim 1.5 pounds of carrots
        _create_recipe_with_claims(
            session,
            "Carrot Soup",
            [
                (items[0], 1.5, "pounds"),
            ],
        )

        available = calculate_available_inventory(session)

        assert len(available) == 1
        assert available[0].ingredient_name == "carrots"
        assert available[0].quantity == 0.5  # 2.0 - 1.5

    def test_multiple_claims_aggregate(self, session: Session):
        """Multiple claims on same ingredient aggregate correctly"""
        from services import calculate_available_inventory

        store = _create_store(session)
        items = _create_inventory(
            session,
            store,
            [
                ("carrots", 3.0, "pounds"),
            ],
        )

        # Two recipes each claiming some carrots
        _create_recipe_with_claims(
            session,
            "Carrot Soup",
            [
                (items[0], 1.0, "pounds"),
            ],
        )
        _create_recipe_with_claims(
            session,
            "Carrot Salad",
            [
                (items[0], 0.5, "pounds"),
            ],
        )

        available = calculate_available_inventory(session)

        assert available[0].quantity == 1.5  # 3.0 - 1.0 - 0.5

    def test_exhausted_inventory_shows_zero(self, session: Session):
        """Fully claimed inventory shows zero, not negative"""
        from services import calculate_available_inventory

        store = _create_store(session)
        items = _create_inventory(
            session,
            store,
            [
                ("carrots", 2.0, "pounds"),
            ],
        )

        # Claim all carrots
        _create_recipe_with_claims(
            session,
            "Carrot Feast",
            [
                (items[0], 2.0, "pounds"),
            ],
        )

        available = calculate_available_inventory(session)

        assert available[0].quantity == 0.0

    def test_overclaimed_inventory_shows_zero(self, session: Session):
        """Over-claimed inventory shows zero (handles edge case)"""
        from services import calculate_available_inventory

        store = _create_store(session)
        items = _create_inventory(
            session,
            store,
            [
                ("carrots", 2.0, "pounds"),
            ],
        )

        # Claim more than available (shouldn't happen, but be defensive)
        _create_recipe_with_claims(
            session,
            "Carrot Overload",
            [
                (items[0], 3.0, "pounds"),
            ],
        )

        available = calculate_available_inventory(session)

        assert available[0].quantity == 0.0  # Not negative

    def test_consumed_claims_not_subtracted(self, session: Session):
        """Only reserved claims affect available inventory, not consumed"""
        from services import calculate_available_inventory

        store = _create_store(session)
        items = _create_inventory(
            session,
            store,
            [
                ("carrots", 2.0, "pounds"),
            ],
        )

        # Create recipe and claim
        recipe = _create_recipe_with_claims(
            session,
            "Carrot Soup",
            [
                (items[0], 1.0, "pounds"),
            ],
        )

        # Mark claim as consumed (recipe was cooked)
        claim = session.exec(
            select(IngredientClaim).where(IngredientClaim.recipe_id == recipe.id)
        ).first()
        claim.state = ClaimState.CONSUMED
        session.commit()

        available = calculate_available_inventory(session)

        # Consumed claims don't reduce available - that inventory is gone
        # But for multi-wave generation, we only care about reserved
        assert available[0].quantity == 2.0  # Full inventory, consumed doesn't block

    def test_multiple_ingredients_calculated_independently(self, session: Session):
        """Each ingredient's claims are calculated independently"""
        from services import calculate_available_inventory

        store = _create_store(session)
        items = _create_inventory(
            session,
            store,
            [
                ("carrots", 2.0, "pounds"),
                ("kale", 1.0, "bunch"),
                ("onions", 3.0, "each"),
            ],
        )

        # Claim some carrots and kale, leave onions untouched
        _create_recipe_with_claims(
            session,
            "Carrot Kale Stir Fry",
            [
                (items[0], 1.0, "pounds"),
                (items[1], 0.5, "bunch"),
            ],
        )

        available = calculate_available_inventory(session)

        carrot = next(i for i in available if i.ingredient_name == "carrots")
        kale = next(i for i in available if i.ingredient_name == "kale")
        onions = next(i for i in available if i.ingredient_name == "onions")

        assert carrot.quantity == 1.0  # 2.0 - 1.0
        assert kale.quantity == 0.5  # 1.0 - 0.5
        assert onions.quantity == 3.0  # Untouched


class TestFormatAvailableInventory:
    """Tests for formatting available inventory for BAML prompt"""

    def test_format_includes_decremented_quantities(self, session: Session):
        """Formatted text shows decremented quantities"""
        from services import calculate_available_inventory, format_available_inventory

        store = _create_store(session)
        items = _create_inventory(
            session,
            store,
            [
                ("carrots", 2.0, "pounds"),
            ],
        )

        _create_recipe_with_claims(
            session,
            "Carrot Soup",
            [
                (items[0], 1.5, "pounds"),
            ],
        )

        available = calculate_available_inventory(session)
        text = format_available_inventory(available, session)

        assert "0.5" in text  # Decremented quantity
        assert "carrots" in text


class TestMultiWaveWorkflow:
    """Integration tests for multi-wave generation workflow"""

    def test_second_wave_sees_decremented_inventory(self, session: Session):
        """
        Simulates: generate pitches → flesh out → generate more pitches
        Verifies second wave sees reduced quantities.
        """
        from services import (
            calculate_available_inventory,
            create_recipe_with_claims,
            format_available_inventory,
        )

        # Setup: CSA box with carrots and kale
        store = _create_store(session)
        _create_inventory(
            session,
            store,
            [
                ("carrots", 2.0, "pounds"),
                ("kale", 1.0, "bunch"),
            ],
        )

        # Wave 1: Check initial inventory
        wave1_available = calculate_available_inventory(session)
        wave1_text = format_available_inventory(wave1_available, session)

        assert "2.0" in wave1_text  # Full carrots
        assert "1.0" in wave1_text  # Full kale

        # Simulate: User selects a pitch, we flesh it out
        # This creates a recipe with claims
        recipe_data = {
            "name": "Carrot Soup",
            "description": "Warming soup",
            "ingredients": [
                {"name": "carrots", "quantity": "1.5", "unit": "pounds"},
            ],
            "instructions": ["Cook", "Blend"],
            "active_time_minutes": 15,
            "total_time_minutes": 45,
            "servings": 4,
            "notes": None,
        }
        create_recipe_with_claims(session, recipe_data)

        # Wave 2: Check decremented inventory
        wave2_available = calculate_available_inventory(session)
        wave2_text = format_available_inventory(wave2_available, session)

        # Carrots should be decremented (2.0 - 1.5 = 0.5)
        assert "0.5" in wave2_text
        # Kale should still be full
        assert "1.0" in wave2_text

        # Verify carrots are actually decremented in the data structure
        carrot_item = next(i for i in wave2_available if i.ingredient_name == "carrots")
        assert carrot_item.quantity == 0.5

    def test_exhausted_ingredient_shows_zero_in_second_wave(self, session: Session):
        """When ingredient is fully claimed, second wave sees zero quantity"""
        from services import (
            calculate_available_inventory,
            create_recipe_with_claims,
        )

        store = _create_store(session)
        _create_inventory(
            session,
            store,
            [
                ("carrots", 2.0, "pounds"),
            ],
        )

        # Flesh out a recipe that uses ALL carrots
        recipe_data = {
            "name": "Carrot Feast",
            "description": "Uses all carrots",
            "ingredients": [
                {"name": "carrots", "quantity": "2.0", "unit": "pounds"},
            ],
            "instructions": ["Use all carrots"],
            "active_time_minutes": 30,
            "total_time_minutes": 60,
            "servings": 6,
            "notes": None,
        }
        create_recipe_with_claims(session, recipe_data)

        # Wave 2: Carrots should be exhausted
        wave2_available = calculate_available_inventory(session)
        carrot_item = next(i for i in wave2_available if i.ingredient_name == "carrots")

        assert carrot_item.quantity == 0.0

    def test_multiple_recipes_accumulate_claims(self, session: Session):
        """Multiple fleshed-out recipes accumulate claims correctly"""
        from services import (
            calculate_available_inventory,
            create_recipe_with_claims,
        )

        store = _create_store(session)
        _create_inventory(
            session,
            store,
            [
                ("carrots", 3.0, "pounds"),
            ],
        )

        # Recipe 1: Use 1 pound
        create_recipe_with_claims(
            session,
            {
                "name": "Recipe 1",
                "description": "First",
                "ingredients": [
                    {"name": "carrots", "quantity": "1.0", "unit": "pounds"}
                ],
                "instructions": ["Step 1"],
                "active_time_minutes": 10,
                "total_time_minutes": 10,
                "servings": 2,
                "notes": None,
            },
        )

        available_after_1 = calculate_available_inventory(session)
        carrot_1 = next(i for i in available_after_1 if i.ingredient_name == "carrots")
        assert carrot_1.quantity == 2.0  # 3.0 - 1.0

        # Recipe 2: Use another 0.5 pounds
        create_recipe_with_claims(
            session,
            {
                "name": "Recipe 2",
                "description": "Second",
                "ingredients": [
                    {"name": "carrots", "quantity": "0.5", "unit": "pounds"}
                ],
                "instructions": ["Step 1"],
                "active_time_minutes": 10,
                "total_time_minutes": 10,
                "servings": 2,
                "notes": None,
            },
        )

        available_after_2 = calculate_available_inventory(session)
        carrot_2 = next(i for i in available_after_2 if i.ingredient_name == "carrots")
        assert carrot_2.quantity == 1.5  # 3.0 - 1.0 - 0.5
