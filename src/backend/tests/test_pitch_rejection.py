"""
Tests for pitch rejection endpoint
"""

from uuid import uuid4

from sqlmodel import Session

from models import MealCriterion, Pitch, PlanningSession


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
