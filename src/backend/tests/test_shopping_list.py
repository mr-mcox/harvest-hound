"""
Tests for shopping list computation algorithm
"""

from fastapi.testclient import TestClient
from sqlmodel import Session

from models import (
    GroceryStore,
    IngredientClaim,
    InventoryItem,
    PlanningSession,
    Recipe,
    RecipeState,
)
from shopping_list import compute_shopping_list


def _create_session(session: Session) -> PlanningSession:
    """Helper to create a planning session"""
    planning_session = PlanningSession(name="Weekly Meal Plan")
    session.add(planning_session)
    session.commit()
    session.refresh(planning_session)
    return planning_session


def _create_store(session: Session) -> GroceryStore:
    """Helper to create a grocery store"""
    store = GroceryStore(name="CSA Box", description="Weekly delivery")
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


def _create_recipe(
    session: Session,
    planning_session: PlanningSession,
    name: str,
    ingredients: list[dict],
) -> Recipe:
    """Helper to create a recipe with ingredients"""
    recipe = Recipe(
        name=name,
        description=f"{name} description",
        ingredients=ingredients,
        instructions=["Step 1"],
        active_time_minutes=30,
        total_time_minutes=60,
        servings=4,
        state=RecipeState.PLANNED,
    )
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


class TestShoppingListComputation:
    """Tests for shopping list computation algorithm"""

    def test_empty_session_returns_empty_list(self, session: Session):
        """No recipes means empty shopping list"""
        planning_session = _create_session(session)

        result = compute_shopping_list(session, planning_session.id)

        assert result.grocery_items == []
        assert result.pantry_staples == []

    def test_single_recipe_single_grocery_item(self, session: Session):
        """Single recipe with one grocery item appears on list"""
        planning_session = _create_session(session)
        _create_recipe(
            session,
            planning_session,
            "Pasta",
            [
                {
                    "name": "pasta",
                    "quantity": "1",
                    "unit": "pound",
                    "purchase_likelihood": 0.8,
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].ingredient_name == "pasta"
        assert result.grocery_items[0].total_quantity == "1 pound"
        assert result.grocery_items[0].purchase_likelihood == 0.8
        assert result.grocery_items[0].used_in_recipes == ["Pasta"]

    def test_pantry_staples_filtered_out(self, session: Session):
        """Ingredients with likelihood < 0.3 don't appear on grocery list"""
        planning_session = _create_session(session)
        _create_recipe(
            session,
            planning_session,
            "Salad",
            [
                {
                    "name": "lettuce",
                    "quantity": "1",
                    "unit": "head",
                    "purchase_likelihood": 0.9,  # Grocery
                },
                {
                    "name": "salt",
                    "quantity": "1",
                    "unit": "tsp",
                    "purchase_likelihood": 0.1,  # Pantry staple
                },
                {
                    "name": "olive oil",
                    "quantity": "2",
                    "unit": "tbsp",
                    "purchase_likelihood": 0.2,  # Pantry staple
                },
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # Only lettuce on grocery list
        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].ingredient_name == "lettuce"

        # Pantry staples appear in separate section
        assert len(result.pantry_staples) == 2
        pantry_names = {item.ingredient_name for item in result.pantry_staples}
        assert pantry_names == {"salt", "olive oil"}

    def test_claimed_ingredients_excluded(self, session: Session):
        """Ingredients with claims (from inventory) don't appear on list"""
        planning_session = _create_session(session)
        store = _create_store(session)

        # Create inventory item
        inventory_item = InventoryItem(
            store_id=store.id,
            ingredient_name="carrots",
            quantity=5.0,
            unit="pounds",
        )
        session.add(inventory_item)
        session.commit()
        session.refresh(inventory_item)

        # Create recipe with carrots
        recipe = _create_recipe(
            session,
            planning_session,
            "Soup",
            [
                {
                    "name": "carrots",
                    "quantity": "2",
                    "unit": "pounds",
                    "purchase_likelihood": 0.7,
                },
                {
                    "name": "onions",
                    "quantity": "3",
                    "unit": "whole",
                    "purchase_likelihood": 0.6,
                },
            ],
        )

        # Create claim for carrots (from inventory)
        claim = IngredientClaim(
            recipe_id=recipe.id,
            inventory_item_id=inventory_item.id,
            ingredient_name="carrots",
            quantity=2.0,
            unit="pounds",
        )
        session.add(claim)
        session.commit()

        result = compute_shopping_list(session, planning_session.id)

        # Only onions on list (carrots claimed from inventory)
        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].ingredient_name == "onions"

    def test_aggregate_same_ingredient_across_recipes(self, session: Session):
        """Same ingredient in multiple recipes gets aggregated"""
        planning_session = _create_session(session)

        _create_recipe(
            session,
            planning_session,
            "Pasta",
            [
                {
                    "name": "tomatoes",
                    "quantity": "2",
                    "unit": "cups",
                    "purchase_likelihood": 0.8,
                }
            ],
        )

        _create_recipe(
            session,
            planning_session,
            "Salad",
            [
                {
                    "name": "tomatoes",
                    "quantity": "1",
                    "unit": "whole",
                    "purchase_likelihood": 0.8,
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # Single aggregated entry for tomatoes
        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].ingredient_name == "tomatoes"
        assert result.grocery_items[0].total_quantity == "2 cups + 1 whole"
        assert result.grocery_items[0].used_in_recipes == ["Pasta", "Salad"]

    def test_grocery_items_sorted_by_likelihood_desc(self, session: Session):
        """Grocery items sorted by purchase_likelihood descending"""
        planning_session = _create_session(session)

        _create_recipe(
            session,
            planning_session,
            "Mixed",
            [
                {
                    "name": "item_low",
                    "quantity": "1",
                    "unit": "unit",
                    "purchase_likelihood": 0.4,
                },
                {
                    "name": "item_high",
                    "quantity": "1",
                    "unit": "unit",
                    "purchase_likelihood": 0.9,
                },
                {
                    "name": "item_mid",
                    "quantity": "1",
                    "unit": "unit",
                    "purchase_likelihood": 0.6,
                },
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # Should be sorted: high (0.9), mid (0.6), low (0.4)
        assert len(result.grocery_items) == 3
        assert result.grocery_items[0].ingredient_name == "item_high"
        assert result.grocery_items[1].ingredient_name == "item_mid"
        assert result.grocery_items[2].ingredient_name == "item_low"

    def test_only_planned_recipes_included(self, session: Session):
        """Only recipes in PLANNED state appear on shopping list"""
        planning_session = _create_session(session)

        # Planned recipe
        _create_recipe(
            session,
            planning_session,
            "Planned",
            [
                {
                    "name": "item1",
                    "quantity": "1",
                    "unit": "unit",
                    "purchase_likelihood": 0.8,
                }
            ],
        )

        # Cooked recipe (should be excluded)
        cooked_recipe = _create_recipe(
            session,
            planning_session,
            "Cooked",
            [
                {
                    "name": "item2",
                    "quantity": "1",
                    "unit": "unit",
                    "purchase_likelihood": 0.8,
                }
            ],
        )
        cooked_recipe.state = RecipeState.COOKED
        session.add(cooked_recipe)
        session.commit()

        result = compute_shopping_list(session, planning_session.id)

        # Only item1 from planned recipe
        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].ingredient_name == "item1"

    def test_threshold_exactly_0_3_is_grocery(self, session: Session):
        """Ingredient with likelihood exactly 0.3 is grocery (boundary test)"""
        planning_session = _create_session(session)

        _create_recipe(
            session,
            planning_session,
            "Boundary",
            [
                {
                    "name": "boundary_item",
                    "quantity": "1",
                    "unit": "unit",
                    "purchase_likelihood": 0.3,  # Exactly at threshold
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # Should be on grocery list (≥0.3)
        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].ingredient_name == "boundary_item"
        assert len(result.pantry_staples) == 0


class TestShoppingListAPIEndpoint:
    """Tests for GET /sessions/{session_id}/shopping-list API endpoint"""

    def test_get_shopping_list_returns_correct_structure(
        self, session: Session, client: TestClient
    ):
        """Happy path: endpoint returns shopping list with correct structure"""
        planning_session = _create_session(session)

        # Create recipe with mixed grocery/pantry items
        _create_recipe(
            session,
            planning_session,
            "Salad",
            [
                {
                    "name": "lettuce",
                    "quantity": "1",
                    "unit": "head",
                    "purchase_likelihood": 0.9,
                },
                {
                    "name": "salt",
                    "quantity": "1",
                    "unit": "tsp",
                    "purchase_likelihood": 0.1,
                },
            ],
        )

        # Call endpoint
        response = client.get(f"/api/sessions/{planning_session.id}/shopping-list")

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "grocery_items" in data
        assert "pantry_staples" in data
        assert isinstance(data["grocery_items"], list)
        assert isinstance(data["pantry_staples"], list)

        # Check content
        assert len(data["grocery_items"]) == 1
        assert data["grocery_items"][0]["ingredient_name"] == "lettuce"
        assert data["grocery_items"][0]["total_quantity"] == "1 head"
        assert data["grocery_items"][0]["purchase_likelihood"] == 0.9
        assert data["grocery_items"][0]["used_in_recipes"] == ["Salad"]

        assert len(data["pantry_staples"]) == 1
        assert data["pantry_staples"][0]["ingredient_name"] == "salt"

    def test_get_shopping_list_empty_session_returns_empty_lists(
        self, session: Session, client: TestClient
    ):
        """Empty session returns empty grocery and pantry lists"""
        planning_session = _create_session(session)

        response = client.get(f"/api/sessions/{planning_session.id}/shopping-list")

        assert response.status_code == 200
        data = response.json()
        assert data["grocery_items"] == []
        assert data["pantry_staples"] == []

    def test_get_shopping_list_session_not_found_returns_404(self, client: TestClient):
        """Non-existent session returns 404"""
        from uuid import uuid4

        fake_id = uuid4()
        response = client.get(f"/api/sessions/{fake_id}/shopping-list")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
