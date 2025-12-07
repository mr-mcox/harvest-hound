"""
Tests for Session, MealCriterion, and Pitch domain models

These tests focus on CASCADE delete behavior, which is SQLite-specific
and requires foreign key pragma to be enabled. CRUD operations are
tested implicitly through API integration tests.
"""

from sqlmodel import Session as DBSession
from sqlmodel import select

from models import MealCriterion, Pitch, PlanningSession


def test_cascade_delete_session_to_criteria(session: DBSession):
    """Deleting a session cascades to delete its criteria"""
    planning_session = PlanningSession(name="Week of Dec 1")
    session.add(planning_session)
    session.commit()

    criterion = MealCriterion(
        session_id=planning_session.id,
        description="Quick meals",
        slots=3,
    )
    session.add(criterion)
    session.commit()

    session_id = planning_session.id

    # Delete session
    session.delete(planning_session)
    session.commit()

    # Criteria should be cascade deleted
    criteria = session.exec(
        select(MealCriterion).where(MealCriterion.session_id == session_id)
    ).all()

    assert len(criteria) == 0


def test_cascade_delete_criterion_to_pitches(session: DBSession):
    """Deleting a criterion cascades to delete its pitches"""
    planning_session = PlanningSession(name="Week of Dec 1")
    session.add(planning_session)
    session.commit()

    criterion = MealCriterion(
        session_id=planning_session.id,
        description="Quick meals",
        slots=3,
    )
    session.add(criterion)
    session.commit()

    pitch = Pitch(
        criterion_id=criterion.id,
        name="Stir Fry",
        blurb="Fast",
        why_make_this="CSA veggies",
        inventory_ingredients=["carrots"],
        active_time_minutes=20,
    )
    session.add(pitch)
    session.commit()

    criterion_id = criterion.id

    # Delete criterion
    session.delete(criterion)
    session.commit()

    # Pitches should be cascade deleted
    pitches = session.exec(
        select(Pitch).where(Pitch.criterion_id == criterion_id)
    ).all()

    assert len(pitches) == 0
