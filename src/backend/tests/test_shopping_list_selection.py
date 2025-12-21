"""
Tests for ShoppingListSelection model and API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from models import (
    PlanningSession,
    Recipe,
    RecipeState,
    ShoppingListSelection,
)
from shopping_list import compute_shopping_list


def _create_session(session: Session) -> PlanningSession:
    """Helper to create a planning session"""
    planning_session = PlanningSession(name="Weekly Meal Plan")
    session.add(planning_session)
    session.commit()
    session.refresh(planning_session)
    return planning_session


class TestShoppingListSelectionBehavior:
    """Tests for ShoppingListSelection linking selections to sessions"""

    def test_can_create_selection_for_session(self, session: Session):
        """Happy path: selection links ingredient checkbox state to session"""
        planning_session = _create_session(session)

        selection = ShoppingListSelection(
            session_id=planning_session.id,
            ingredient_name="tomatoes",
            checked=True,
        )
        session.add(selection)
        session.commit()

        session.expire_all()
        loaded = session.get(ShoppingListSelection, selection.id)

        assert loaded is not None
        assert loaded.session_id == planning_session.id
        assert loaded.ingredient_name == "tomatoes"
        assert loaded.checked is True
        assert loaded.reviewed_at is None

    def test_deleting_planning_session_cascades_to_selections(self, session: Session):
        """When planning session is deleted, its selections are also deleted"""
        planning_session = _create_session(session)

        selection = ShoppingListSelection(
            session_id=planning_session.id,
            ingredient_name="tomatoes",
            checked=True,
        )
        session.add(selection)
        session.commit()
        selection_id = selection.id

        session.delete(planning_session)
        session.commit()

        assert session.get(ShoppingListSelection, selection_id) is None

    def test_checked_defaults_to_false(self, session: Session):
        """Checked field defaults to False when not specified"""
        planning_session = _create_session(session)

        selection = ShoppingListSelection(
            session_id=planning_session.id,
            ingredient_name="lettuce",
        )
        session.add(selection)
        session.commit()

        session.expire_all()
        loaded = session.get(ShoppingListSelection, selection.id)

        assert loaded.checked is False


class TestShoppingListSelectionConstraints:
    """Tests for ShoppingListSelection uniqueness constraints"""

    def test_unique_constraint_prevents_duplicate_ingredient_in_session(
        self, session: Session
    ):
        """Cannot have two selections for same ingredient in same session"""
        planning_session = _create_session(session)

        selection1 = ShoppingListSelection(
            session_id=planning_session.id,
            ingredient_name="onions",
            checked=True,
        )
        session.add(selection1)
        session.commit()

        selection2 = ShoppingListSelection(
            session_id=planning_session.id,
            ingredient_name="onions",
            checked=False,
        )
        session.add(selection2)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_same_ingredient_allowed_in_different_sessions(self, session: Session):
        """Same ingredient can have selections in different sessions"""
        session1 = _create_session(session)
        session2 = _create_session(session)

        selection1 = ShoppingListSelection(
            session_id=session1.id,
            ingredient_name="garlic",
            checked=True,
        )
        selection2 = ShoppingListSelection(
            session_id=session2.id,
            ingredient_name="garlic",
            checked=False,
        )
        session.add(selection1)
        session.add(selection2)
        session.commit()

        assert selection1.id is not None
        assert selection2.id is not None
        assert selection1.id != selection2.id


class TestSelectionAPIEndpoints:
    """Tests for shopping list selection API endpoints"""

    def test_patch_selection_creates_new_selection(self, client: TestClient):
        """PATCH creates selection if it doesn't exist (upsert insert)"""
        # Create a session first
        response = client.post("/api/sessions", json={"name": "Test Session"})
        session_id = response.json()["id"]

        # PATCH to create selection
        response = client.patch(
            f"/api/sessions/{session_id}/shopping-list/selections",
            json={"ingredient_name": "tomatoes", "checked": True},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ingredient_name"] == "tomatoes"
        assert data["checked"] is True

    def test_patch_selection_updates_existing_selection(self, client: TestClient):
        """PATCH updates selection if it already exists (upsert update)"""
        # Create a session
        response = client.post("/api/sessions", json={"name": "Test Session"})
        session_id = response.json()["id"]

        # Create initial selection
        client.patch(
            f"/api/sessions/{session_id}/shopping-list/selections",
            json={"ingredient_name": "onions", "checked": True},
        )

        # Update to unchecked
        response = client.patch(
            f"/api/sessions/{session_id}/shopping-list/selections",
            json={"ingredient_name": "onions", "checked": False},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ingredient_name"] == "onions"
        assert data["checked"] is False

    def test_patch_selection_returns_404_for_nonexistent_session(
        self, client: TestClient
    ):
        """PATCH returns 404 if session doesn't exist"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.patch(
            f"/api/sessions/{fake_id}/shopping-list/selections",
            json={"ingredient_name": "tomatoes", "checked": True},
        )

        assert response.status_code == 404

    def test_get_selections_returns_all_selections_for_session(
        self, client: TestClient
    ):
        """GET returns all selections as ingredient_name: checked dict"""
        # Create a session
        response = client.post("/api/sessions", json={"name": "Test Session"})
        session_id = response.json()["id"]

        # Create some selections
        client.patch(
            f"/api/sessions/{session_id}/shopping-list/selections",
            json={"ingredient_name": "tomatoes", "checked": True},
        )
        client.patch(
            f"/api/sessions/{session_id}/shopping-list/selections",
            json={"ingredient_name": "onions", "checked": False},
        )

        # GET all selections
        response = client.get(f"/api/sessions/{session_id}/shopping-list/selections")

        assert response.status_code == 200
        data = response.json()
        assert data == {"tomatoes": True, "onions": False}

    def test_get_selections_returns_empty_dict_when_no_selections(
        self, client: TestClient
    ):
        """GET returns empty dict when no selections exist"""
        # Create a session
        response = client.post("/api/sessions", json={"name": "Test Session"})
        session_id = response.json()["id"]

        # GET selections (none exist)
        response = client.get(f"/api/sessions/{session_id}/shopping-list/selections")

        assert response.status_code == 200
        assert response.json() == {}

    def test_get_selections_returns_404_for_nonexistent_session(
        self, client: TestClient
    ):
        """GET returns 404 if session doesn't exist"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/sessions/{fake_id}/shopping-list/selections")

        assert response.status_code == 404


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
        session_id=planning_session.id,
    )
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


class TestShoppingListWithSelections:
    """Tests for compute_shopping_list including checked field"""

    def test_shopping_list_items_include_checked_field(self, session: Session):
        """Shopping list items have checked field from selections"""
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
                    "purchase_likelihood": 0.9,
                },
                {
                    "name": "tomatoes",
                    "quantity": "2",
                    "unit": "whole",
                    "purchase_likelihood": 0.8,
                },
            ],
        )

        # Create selection for lettuce (checked)
        selection = ShoppingListSelection(
            session_id=planning_session.id,
            ingredient_name="lettuce",
            checked=True,
        )
        session.add(selection)
        session.commit()

        result = compute_shopping_list(session, planning_session.id)

        # Find items by name
        lettuce = next(
            i for i in result.grocery_items if i.ingredient_name == "lettuce"
        )
        tomatoes = next(
            i for i in result.grocery_items if i.ingredient_name == "tomatoes"
        )

        assert lettuce.checked is True
        assert tomatoes.checked is False  # Default when no selection exists

    def test_shopping_list_checked_defaults_to_false(self, session: Session):
        """Items without selections have checked=False"""
        planning_session = _create_session(session)

        _create_recipe(
            session,
            planning_session,
            "Soup",
            [
                {
                    "name": "carrots",
                    "quantity": "3",
                    "unit": "whole",
                    "purchase_likelihood": 0.7,
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].checked is False

    def test_pantry_staples_also_have_checked_field(self, session: Session):
        """Pantry staples also include checked field"""
        planning_session = _create_session(session)

        _create_recipe(
            session,
            planning_session,
            "Toast",
            [
                {
                    "name": "salt",
                    "quantity": "1",
                    "unit": "pinch",
                    "purchase_likelihood": 0.1,
                }
            ],
        )

        # Create selection for salt
        selection = ShoppingListSelection(
            session_id=planning_session.id,
            ingredient_name="salt",
            checked=True,
        )
        session.add(selection)
        session.commit()

        result = compute_shopping_list(session, planning_session.id)

        assert len(result.pantry_staples) == 1
        assert result.pantry_staples[0].checked is True
