"""
Tests for pitch rejection endpoint
"""

from uuid import uuid4

from sqlmodel import Session

from models import GroceryStore, InventoryItem, MealCriterion, Pitch, PlanningSession
from services import (
    calculate_pitch_generation_delta,
)


class TestPitchRejection:
    """Tests for PATCH /api/sessions/{session_id}/pitches/{pitch_id}/reject"""

    def test_reject_pitch_sets_rejected_true(self, client, session: Session):
        """Happy path: rejecting a pitch sets rejected=True"""
        # Create session and criterion
        planning_session = PlanningSession(name="Test Session")
        session.add(planning_session)
        session.commit()
        session.refresh(planning_session)

        criterion = MealCriterion(
            session_id=planning_session.id,
            description="Quick meals",
            slots=3,
        )
        session.add(criterion)
        session.commit()
        session.refresh(criterion)

        # Create pitch
        pitch = Pitch(
            criterion_id=criterion.id,
            name="Quick Pasta",
            blurb="Fast and easy",
            why_make_this="Uses CSA tomatoes",
            inventory_ingredients=[],
            active_time_minutes=20,
        )
        session.add(pitch)
        session.commit()
        session.refresh(pitch)

        # Reject the pitch
        response = client.patch(
            f"/api/sessions/{planning_session.id}/pitches/{pitch.id}/reject"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(pitch.id)
        assert data["rejected"] is True

        # Verify in database (refresh to see committed changes)
        session.expire_all()
        updated_pitch = session.get(Pitch, pitch.id)
        assert updated_pitch.rejected is True

    def test_reject_nonexistent_pitch_returns_404(self, client, session: Session):
        """Error handling: rejecting non-existent pitch returns 404"""
        # Create session
        planning_session = PlanningSession(name="Test Session")
        session.add(planning_session)
        session.commit()
        session.refresh(planning_session)

        fake_pitch_id = uuid4()

        response = client.patch(
            f"/api/sessions/{planning_session.id}/pitches/{fake_pitch_id}/reject"
        )

        assert response.status_code == 404


class TestRejectedPitchesExcludedFromGenerationCount:
    """Tests that rejected pitches are not counted when calculating generation delta"""

    def test_rejected_pitches_excluded_from_generation_count(self, session: Session):
        """
        BUG REPRODUCTION: Rejected pitches should not count toward the pitch quota.

        If we have 3 unfilled slots (target: 9 pitches) and 3 existing pitches
        but 2 are rejected, we should generate 8 more (not 6).
        """
        # Setup: Create session and criterion with 3 slots
        planning_session = PlanningSession(name="Test Session")
        session.add(planning_session)
        session.commit()
        session.refresh(planning_session)

        criterion = MealCriterion(
            session_id=planning_session.id,
            description="Quick dinners",
            slots=3,  # 3 slots = target of 9 pitches (3 * 3)
        )
        session.add(criterion)
        session.commit()
        session.refresh(criterion)

        # Create inventory so pitches are valid
        store = GroceryStore(name="CSA", description="Delivery")
        session.add(store)
        session.commit()
        session.refresh(store)

        inventory_item = InventoryItem(
            store_id=store.id,
            ingredient_name="tomatoes",
            quantity=10.0,
            unit="pounds",
            priority="high",
        )
        session.add(inventory_item)
        session.commit()

        # Create 3 pitches: 1 valid, 2 rejected
        pitch1 = Pitch(
            criterion_id=criterion.id,
            name="Tomato Soup",
            blurb="Valid pitch",
            why_make_this="Good soup",
            inventory_ingredients=[
                {"name": "tomatoes", "quantity": 2.0, "unit": "pounds"}
            ],
            active_time_minutes=20,
            rejected=False,  # Valid pitch
        )
        pitch2 = Pitch(
            criterion_id=criterion.id,
            name="Tomato Salad",
            blurb="Rejected pitch",
            why_make_this="Too boring",
            inventory_ingredients=[
                {"name": "tomatoes", "quantity": 1.0, "unit": "pounds"}
            ],
            active_time_minutes=10,
            rejected=True,  # Rejected!
        )
        pitch3 = Pitch(
            criterion_id=criterion.id,
            name="Tomato Pasta",
            blurb="Also rejected",
            why_make_this="Too common",
            inventory_ingredients=[
                {"name": "tomatoes", "quantity": 1.5, "unit": "pounds"}
            ],
            active_time_minutes=15,
            rejected=True,  # Rejected!
        )
        session.add_all([pitch1, pitch2, pitch3])
        session.commit()

        # Calculate generation delta
        delta = calculate_pitch_generation_delta(session, planning_session.id)

        # EXPECTED: Only 1 valid pitch exists (pitch1), so we need 8 more to reach 9
        # BUG: Function counts all 3 pitches, so it thinks we need only 6 more
        assert delta == 8  # Should generate 8 more pitches (9 - 1 valid)
