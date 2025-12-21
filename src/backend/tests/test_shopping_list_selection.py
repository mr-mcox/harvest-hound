"""
Tests for ShoppingListSelection model
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from models import (
    PlanningSession,
    ShoppingListSelection,
)


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
