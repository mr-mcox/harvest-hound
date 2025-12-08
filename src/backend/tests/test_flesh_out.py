"""
Tests for flesh-out endpoint - recipe generation with atomic claim creation
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

from sqlmodel import Session

from models import (
    ClaimState,
    GroceryStore,
    InventoryItem,
    MealCriterion,
    PlanningSession,
    RecipeState,
)

# --- Test Fixtures ---


def _create_session_with_criterion(
    db: Session,
) -> tuple[PlanningSession, MealCriterion]:
    """Create a planning session with one criterion"""
    session = PlanningSession(name="Test Week")
    db.add(session)
    db.commit()
    db.refresh(session)

    criterion = MealCriterion(
        session_id=session.id,
        description="Quick weeknight dinners",
        slots=2,
    )
    db.add(criterion)
    db.commit()
    db.refresh(criterion)

    return session, criterion


def _create_store_with_inventory(
    db: Session,
) -> tuple[GroceryStore, list[InventoryItem]]:
    """Create a store with inventory items for testing"""
    store = GroceryStore(name="CSA Box", description="Weekly delivery")
    db.add(store)
    db.commit()
    db.refresh(store)

    items = [
        InventoryItem(
            store_id=store.id,
            ingredient_name="carrots",
            quantity=2.0,
            unit="pounds",
        ),
        InventoryItem(
            store_id=store.id,
            ingredient_name="kale",
            quantity=1.0,
            unit="bunch",
        ),
    ]
    for item in items:
        db.add(item)
    db.commit()
    for item in items:
        db.refresh(item)

    return store, items


class TestIngredientMatching:
    """Tests for matching recipe ingredients to inventory items"""

    def test_exact_match_returns_inventory_item(self, session: Session):
        """Exact name match finds the inventory item"""
        from services import build_inventory_lookup

        store, items = _create_store_with_inventory(session)

        lookup = build_inventory_lookup(session)

        assert "carrots" in lookup
        assert lookup["carrots"].id == items[0].id

    def test_case_insensitive_match(self, session: Session):
        """Matching is case-insensitive"""
        from services import build_inventory_lookup

        store, items = _create_store_with_inventory(session)

        lookup = build_inventory_lookup(session)

        # Lookup should work regardless of case
        assert "carrots" in lookup
        assert "Carrots" not in lookup  # Keys are lowercased
        # But we need case-insensitive lookup in the matching function
        from services import match_ingredient_to_inventory

        result = match_ingredient_to_inventory("Carrots", lookup)
        assert result is not None
        assert result.id == items[0].id

    def test_no_match_returns_none(self, session: Session):
        """Non-matching ingredient returns None"""
        from services import build_inventory_lookup, match_ingredient_to_inventory

        store, items = _create_store_with_inventory(session)

        lookup = build_inventory_lookup(session)
        result = match_ingredient_to_inventory("chicken", lookup)

        assert result is None

    def test_empty_inventory_returns_empty_lookup(self, session: Session):
        """Empty inventory produces empty lookup"""
        from services import build_inventory_lookup

        lookup = build_inventory_lookup(session)

        assert lookup == {}


# --- Atomic Claim Creation Tests ---


class TestAtomicClaimCreation:
    """Tests for atomic recipe save + claim creation"""

    def test_claims_created_for_matching_ingredients(self, session: Session):
        """Claims are created for ingredients that match inventory"""
        from services import create_recipe_with_claims

        store, items = _create_store_with_inventory(session)

        # Simulate a recipe with ingredients
        recipe_data = {
            "name": "Carrot Soup",
            "description": "Warming soup",
            "ingredients": [
                {"name": "carrots", "quantity": "2", "unit": "pounds"},
                {
                    "name": "onion",
                    "quantity": "1",
                    "unit": "medium",
                },  # Not in inventory
            ],
            "instructions": ["Chop carrots", "Cook soup"],
            "active_time_minutes": 15,
            "total_time_minutes": 45,
            "servings": 4,
            "notes": None,
        }

        recipe, claims = create_recipe_with_claims(session, recipe_data)

        # Recipe should be saved
        assert recipe.id is not None
        assert recipe.name == "Carrot Soup"

        # Only carrots should have a claim (onion not in inventory)
        assert len(claims) == 1
        assert claims[0].ingredient_name == "carrots"
        assert claims[0].inventory_item_id == items[0].id
        assert claims[0].state == ClaimState.RESERVED

    def test_all_claims_succeed_or_none(self, session: Session):
        """Atomic: all claims succeed together"""
        from services import create_recipe_with_claims

        store, items = _create_store_with_inventory(session)

        recipe_data = {
            "name": "Kale Carrot Stir Fry",
            "description": "Quick and healthy",
            "ingredients": [
                {"name": "carrots", "quantity": "1", "unit": "pound"},
                {"name": "kale", "quantity": "1", "unit": "bunch"},
            ],
            "instructions": ["Prep vegetables", "Stir fry"],
            "active_time_minutes": 20,
            "total_time_minutes": 20,
            "servings": 2,
            "notes": None,
        }

        recipe, claims = create_recipe_with_claims(session, recipe_data)

        # Both ingredients should have claims
        assert len(claims) == 2
        claim_names = {c.ingredient_name for c in claims}
        assert claim_names == {"carrots", "kale"}

        # All claims should reference the recipe
        for claim in claims:
            assert claim.recipe_id == recipe.id

    def test_quantity_parsed_from_string(self, session: Session):
        """Claim quantity is parsed from string format"""
        from services import create_recipe_with_claims

        store, items = _create_store_with_inventory(session)

        recipe_data = {
            "name": "Carrot Sticks",
            "description": "Simple snack",
            "ingredients": [
                {"name": "carrots", "quantity": "1.5", "unit": "pounds"},
            ],
            "instructions": ["Cut carrots"],
            "active_time_minutes": 5,
            "total_time_minutes": 5,
            "servings": 4,
            "notes": None,
        }

        recipe, claims = create_recipe_with_claims(session, recipe_data)

        assert len(claims) == 1
        assert claims[0].quantity == 1.5

    def test_non_numeric_quantity_defaults_to_one(self, session: Session):
        """Non-numeric quantities like 'to taste' default to 1.0"""
        from services import create_recipe_with_claims

        store, items = _create_store_with_inventory(session)

        recipe_data = {
            "name": "Kale Chips",
            "description": "Crispy snack",
            "ingredients": [
                {"name": "kale", "quantity": "to taste", "unit": "bunch"},
            ],
            "instructions": ["Bake kale"],
            "active_time_minutes": 10,
            "total_time_minutes": 25,
            "servings": 2,
            "notes": None,
        }

        recipe, claims = create_recipe_with_claims(session, recipe_data)

        assert len(claims) == 1
        assert claims[0].quantity == 1.0  # Default for non-numeric

    def test_recipe_state_is_planned(self, session: Session):
        """New recipes from flesh-out have 'planned' state"""
        from services import create_recipe_with_claims

        store, items = _create_store_with_inventory(session)

        recipe_data = {
            "name": "Test Recipe",
            "description": "Test",
            "ingredients": [],
            "instructions": ["Step 1"],
            "active_time_minutes": 10,
            "total_time_minutes": 10,
            "servings": 2,
            "notes": None,
        }

        recipe, claims = create_recipe_with_claims(session, recipe_data)

        assert recipe.state == RecipeState.PLANNED

    def test_recipe_session_id_is_set(self, session: Session):
        """Recipe session_id is set from recipe_data"""
        from services import create_recipe_with_claims

        # Create a planning session
        planning_session = PlanningSession(name="Test Week")
        session.add(planning_session)
        session.commit()
        session.refresh(planning_session)

        recipe_data = {
            "session_id": planning_session.id,
            "name": "Test Recipe",
            "description": "Test",
            "ingredients": [],
            "instructions": ["Step 1"],
            "active_time_minutes": 10,
            "total_time_minutes": 10,
            "servings": 2,
            "notes": None,
        }

        recipe, claims = create_recipe_with_claims(session, recipe_data)

        assert recipe.session_id == planning_session.id

    def test_recipe_criterion_id_is_set(self, session: Session):
        """Recipe criterion_id is set from recipe_data"""
        from services import create_recipe_with_claims

        # Create a planning session and criterion
        planning_session = PlanningSession(name="Test Week")
        session.add(planning_session)
        session.commit()
        session.refresh(planning_session)

        criterion = MealCriterion(
            session_id=planning_session.id,
            description="Quick weeknight dinners",
            slots=2,
        )
        session.add(criterion)
        session.commit()
        session.refresh(criterion)

        recipe_data = {
            "session_id": planning_session.id,
            "criterion_id": criterion.id,
            "name": "Test Recipe",
            "description": "Test",
            "ingredients": [],
            "instructions": ["Step 1"],
            "active_time_minutes": 10,
            "total_time_minutes": 10,
            "servings": 2,
            "notes": None,
        }

        recipe, claims = create_recipe_with_claims(session, recipe_data)

        assert recipe.criterion_id == criterion.id


# --- Flesh-Out Endpoint Integration Tests ---


class TestFleshOutEndpoint:
    """Integration tests for the flesh-out endpoint"""

    def test_flesh_out_single_pitch_success(self, client, session: Session):
        """Successfully flesh out a single pitch"""
        # Setup
        planning_session, criterion = _create_session_with_criterion(session)
        store, items = _create_store_with_inventory(session)

        # Mock BAML response - use MagicMock for data objects
        mock_ingredient = MagicMock()
        mock_ingredient.name = "carrots"
        mock_ingredient.quantity = "2"
        mock_ingredient.unit = "pounds"
        mock_ingredient.preparation = "julienned"
        mock_ingredient.notes = None
        mock_ingredient.purchase_likelihood = 0.8

        mock_recipe = MagicMock()
        mock_recipe.name = "Honey Glazed Carrots"
        mock_recipe.description = "Sweet caramelized carrots"
        mock_recipe.ingredients = [mock_ingredient]
        mock_recipe.instructions = ["Cut carrots", "Glaze with honey", "Roast"]
        mock_recipe.active_time_minutes = 15
        mock_recipe.total_time_minutes = 45
        mock_recipe.servings = 4
        mock_recipe.notes = None

        # Use AsyncMock for the coroutine function itself
        async def mock_flesh_out(*args, **kwargs):
            return mock_recipe

        with patch("routes.b.FleshOutRecipe", side_effect=mock_flesh_out):
            response = client.post(
                f"/api/sessions/{planning_session.id}/flesh-out-pitches",
                json={
                    "pitches": [
                        {
                            "name": "Honey Glazed Carrots",
                            "blurb": "Sweet and caramelized",
                            "inventory_ingredients": [
                                {"name": "carrots", "quantity": 2.0, "unit": "pounds"}
                            ],
                            "criterion_id": str(criterion.id),
                        }
                    ]
                },
            )

        assert response.status_code == 200
        data = response.json()

        # Check for errors first to help debug
        assert data["errors"] == [], f"Unexpected errors: {data['errors']}"
        assert len(data["recipes"]) == 1
        assert data["recipes"][0]["name"] == "Honey Glazed Carrots"
        assert len(data["recipes"][0]["claims"]) == 1
        assert data["recipes"][0]["claims"][0]["ingredient_name"] == "carrots"

    def test_flesh_out_batch_pitches(self, client, session: Session):
        """Flesh out multiple pitches in a batch"""
        planning_session, criterion = _create_session_with_criterion(session)
        store, items = _create_store_with_inventory(session)

        # Mock BAML to return different recipes
        call_count = 0

        async def mock_flesh_out(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            mock_ing = MagicMock()
            mock = MagicMock()

            if call_count == 1:
                mock_ing.name = "carrots"
                mock_ing.quantity = "1"
                mock_ing.unit = "pound"
                mock_ing.preparation = "chopped"
                mock_ing.notes = None
                mock_ing.purchase_likelihood = 0.7
                mock.name = "Carrot Soup"
                mock.description = "Warming soup"
            else:
                mock_ing.name = "kale"
                mock_ing.quantity = "1"
                mock_ing.unit = "bunch"
                mock_ing.preparation = "torn"
                mock_ing.notes = None
                mock_ing.purchase_likelihood = 0.6
                mock.name = "Kale Salad"
                mock.description = "Fresh and healthy"

            mock.ingredients = [mock_ing]
            mock.instructions = ["Step 1", "Step 2"]
            mock.active_time_minutes = 15
            mock.total_time_minutes = 30
            mock.servings = 4
            mock.notes = None
            return mock

        with patch("routes.b.FleshOutRecipe", side_effect=mock_flesh_out):
            response = client.post(
                f"/api/sessions/{planning_session.id}/flesh-out-pitches",
                json={
                    "pitches": [
                        {
                            "name": "Carrot Soup",
                            "blurb": "Warming",
                            "inventory_ingredients": [
                                {"name": "carrots", "quantity": 1.0, "unit": "pound"}
                            ],
                            "criterion_id": str(criterion.id),
                        },
                        {
                            "name": "Kale Salad",
                            "blurb": "Fresh",
                            "inventory_ingredients": [
                                {"name": "kale", "quantity": 1.0, "unit": "bunch"}
                            ],
                            "criterion_id": str(criterion.id),
                        },
                    ]
                },
            )

        assert response.status_code == 200
        data = response.json()

        assert len(data["recipes"]) == 2
        recipe_names = {r["name"] for r in data["recipes"]}
        assert recipe_names == {"Carrot Soup", "Kale Salad"}

    def test_flesh_out_session_not_found(self, client):
        """Returns 404 for non-existent session"""
        fake_id = uuid4()
        response = client.post(
            f"/api/sessions/{fake_id}/flesh-out-pitches",
            json={"pitches": []},
        )

        assert response.status_code == 404

    def test_flesh_out_empty_pitches_list(self, client, session: Session):
        """Empty pitches list returns empty response"""
        planning_session, criterion = _create_session_with_criterion(session)

        response = client.post(
            f"/api/sessions/{planning_session.id}/flesh-out-pitches",
            json={"pitches": []},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["recipes"] == []
        assert data["errors"] == []

    def test_flesh_out_includes_purchase_likelihood(self, client, session: Session):
        """Verify purchase_likelihood is included in ingredient response"""
        planning_session, criterion = _create_session_with_criterion(session)
        store, items = _create_store_with_inventory(session)

        # Mock BAML response with purchase_likelihood
        mock_ingredient = MagicMock()
        mock_ingredient.name = "coconut milk"
        mock_ingredient.quantity = "1"
        mock_ingredient.unit = "can (13.5 oz)"
        mock_ingredient.preparation = None
        mock_ingredient.notes = "Full-fat preferred"
        mock_ingredient.purchase_likelihood = 0.1  # Low - pantry staple

        mock_recipe = MagicMock()
        mock_recipe.name = "Coconut Curry"
        mock_recipe.description = "Creamy curry"
        mock_recipe.ingredients = [mock_ingredient]
        mock_recipe.instructions = ["Cook curry"]
        mock_recipe.active_time_minutes = 30
        mock_recipe.total_time_minutes = 45
        mock_recipe.servings = 4
        mock_recipe.notes = None

        async def mock_flesh_out(*args, **kwargs):
            return mock_recipe

        with patch("routes.b.FleshOutRecipe", side_effect=mock_flesh_out):
            response = client.post(
                f"/api/sessions/{planning_session.id}/flesh-out-pitches",
                json={
                    "pitches": [
                        {
                            "name": "Coconut Curry",
                            "blurb": "Creamy and delicious",
                            "inventory_ingredients": [],
                            "criterion_id": str(criterion.id),
                        }
                    ]
                },
            )

        assert response.status_code == 200
        data = response.json()

        # Verify purchase_likelihood is in the response
        assert len(data["recipes"]) == 1
        recipe = data["recipes"][0]
        assert len(recipe["ingredients"]) == 1
        ingredient = recipe["ingredients"][0]
        assert "purchase_likelihood" in ingredient
        assert ingredient["purchase_likelihood"] == 0.1
