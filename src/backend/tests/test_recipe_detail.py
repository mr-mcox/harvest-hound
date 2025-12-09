"""Tests for recipe detail endpoint"""

from uuid import uuid4

import pytest
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


@pytest.fixture
def session_with_recipe(session: Session) -> tuple[PlanningSession, Recipe]:
    """Create a planning session with a recipe"""
    # Create session
    planning_session = PlanningSession(name="Test Session")
    session.add(planning_session)
    session.commit()
    session.refresh(planning_session)

    # Create recipe
    recipe = Recipe(
        session_id=planning_session.id,
        criterion_id=uuid4(),
        name="Test Recipe",
        description="A test recipe",
        ingredients=[
            {
                "name": "carrot",
                "quantity": "2",
                "unit": "whole",
                "preparation": "diced",
                "notes": None,
            }
        ],
        instructions=["Step 1", "Step 2"],
        active_time_minutes=15,
        total_time_minutes=30,
        servings=2,
        state=RecipeState.PLANNED,
    )
    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    return planning_session, recipe


class TestGetRecipe:
    """Tests for GET /api/recipes/{id} endpoint"""

    def test_get_recipe_success(
        self,
        session: Session,
        client: TestClient,
        session_with_recipe: tuple[PlanningSession, Recipe],
    ):
        """Should return recipe details with claims"""
        _, recipe = session_with_recipe

        # Create grocery store
        store = GroceryStore(name="CSA Box", description="Weekly delivery")
        session.add(store)
        session.commit()
        session.refresh(store)

        # Add an inventory item and claim
        inventory_item = InventoryItem(
            store_id=store.id,
            ingredient_name="carrot",
            quantity=5,
            unit="whole",
        )
        session.add(inventory_item)
        session.commit()
        session.refresh(inventory_item)

        claim = IngredientClaim(
            recipe_id=recipe.id,
            inventory_item_id=inventory_item.id,
            ingredient_name="carrot",
            quantity=2,
            unit="whole",
        )
        session.add(claim)
        session.commit()

        # Request recipe
        response = client.get(f"/api/recipes/{recipe.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(recipe.id)
        assert data["name"] == "Test Recipe"
        assert data["description"] == "A test recipe"
        assert data["state"] == "planned"
        assert len(data["ingredients"]) == 1
        assert len(data["instructions"]) == 2
        assert len(data["claims"]) == 1
        assert data["claims"][0]["ingredient_name"] == "carrot"

    def test_get_recipe_not_found(self, client: TestClient):
        """Should return 404 for non-existent recipe"""
        fake_id = uuid4()
        response = client.get(f"/api/recipes/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_cooked_recipe(
        self,
        session: Session,
        client: TestClient,
        session_with_recipe: tuple[PlanningSession, Recipe],
    ):
        """Should return cooked recipes"""
        _, recipe = session_with_recipe

        # Mark as cooked
        recipe.state = RecipeState.COOKED
        session.add(recipe)
        session.commit()

        response = client.get(f"/api/recipes/{recipe.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["state"] == "cooked"
