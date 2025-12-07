"""
API routes for Harvest Hound
"""

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from baml_client import b
from models import (
    GroceryStore,
    HouseholdProfile,
    InventoryItem,
    MealCriterion,
    Pantry,
    Pitch,
    PlanningSession,
    db_health,
    get_session,
)

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    """Health check endpoint - verifies stack is working"""
    return {
        "status": "healthy",
        "db_ok": db_health(),
    }


# --- Session CRUD ---


class SessionCreate(BaseModel):
    name: str


class SessionResponse(BaseModel):
    id: UUID
    name: str
    created_at: str

    @classmethod
    def from_model(cls, session: PlanningSession) -> "SessionResponse":
        return cls(
            id=session.id,
            name=session.name,
            created_at=session.created_at.isoformat(),
        )


@router.post("/sessions", status_code=201)
def create_session(
    data: SessionCreate, db: Session = Depends(get_session)
) -> SessionResponse:
    """Create a new planning session"""
    session = PlanningSession(name=data.name)
    db.add(session)
    db.commit()
    db.refresh(session)
    return SessionResponse.from_model(session)


@router.get("/sessions")
def list_sessions(db: Session = Depends(get_session)) -> list[SessionResponse]:
    """List all planning sessions, newest first"""
    sessions = db.exec(
        select(PlanningSession).order_by(PlanningSession.created_at.desc())
    ).all()
    return [SessionResponse.from_model(s) for s in sessions]


@router.get("/sessions/{session_id}")
def get_session_by_id(
    session_id: UUID, db: Session = Depends(get_session)
) -> SessionResponse:
    """Get a specific planning session by ID"""
    session = db.get(PlanningSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse.from_model(session)


# --- Criteria CRUD ---


class CriterionCreate(BaseModel):
    description: str
    slots: int


class CriterionResponse(BaseModel):
    id: UUID
    description: str
    slots: int
    created_at: str

    @classmethod
    def from_model(cls, criterion: MealCriterion) -> "CriterionResponse":
        return cls(
            id=criterion.id,
            description=criterion.description,
            slots=criterion.slots,
            created_at=criterion.created_at.isoformat(),
        )


MAX_CRITERIA_PER_SESSION = 7


@router.post("/sessions/{session_id}/criteria", status_code=201)
def create_criterion(
    session_id: UUID, data: CriterionCreate, db: Session = Depends(get_session)
) -> CriterionResponse:
    """Create a new meal criterion for a session"""
    session = db.get(PlanningSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check max criteria limit
    existing_count = len(
        db.exec(
            select(MealCriterion).where(MealCriterion.session_id == session_id)
        ).all()
    )
    if existing_count >= MAX_CRITERIA_PER_SESSION:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_CRITERIA_PER_SESSION} criteria per session",
        )

    criterion = MealCriterion(
        session_id=session_id,
        description=data.description,
        slots=data.slots,
    )
    db.add(criterion)
    db.commit()
    db.refresh(criterion)
    return CriterionResponse.from_model(criterion)


@router.get("/sessions/{session_id}/criteria")
def list_criteria(
    session_id: UUID, db: Session = Depends(get_session)
) -> list[CriterionResponse]:
    """List all criteria for a session"""
    session = db.get(PlanningSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    criteria = db.exec(
        select(MealCriterion)
        .where(MealCriterion.session_id == session_id)
        .order_by(MealCriterion.created_at)
    ).all()
    return [CriterionResponse.from_model(c) for c in criteria]


@router.delete("/sessions/{session_id}/criteria/{criterion_id}", status_code=204)
def delete_criterion(
    session_id: UUID, criterion_id: UUID, db: Session = Depends(get_session)
) -> None:
    """Delete a criterion from a session"""
    criterion = db.get(MealCriterion, criterion_id)
    if not criterion or criterion.session_id != session_id:
        raise HTTPException(status_code=404, detail="Criterion not found")

    db.delete(criterion)
    db.commit()


# --- Pitches API ---


class PitchResponse(BaseModel):
    id: UUID
    criterion_id: UUID
    name: str
    blurb: str
    why_make_this: str
    inventory_ingredients: list[dict]
    active_time_minutes: int
    created_at: str

    @classmethod
    def from_model(cls, pitch: Pitch) -> "PitchResponse":
        return cls(
            id=pitch.id,
            criterion_id=pitch.criterion_id,
            name=pitch.name,
            blurb=pitch.blurb,
            why_make_this=pitch.why_make_this,
            inventory_ingredients=pitch.inventory_ingredients,
            active_time_minutes=pitch.active_time_minutes,
            created_at=pitch.created_at.isoformat(),
        )


@router.get("/sessions/{session_id}/pitches")
def list_pitches(
    session_id: UUID, db: Session = Depends(get_session)
) -> list[PitchResponse]:
    """List all pitches for a session, ordered by criterion and creation time"""
    session = db.get(PlanningSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get all criteria for this session
    criteria = db.exec(
        select(MealCriterion).where(MealCriterion.session_id == session_id)
    ).all()
    criterion_ids = [c.id for c in criteria]

    if not criterion_ids:
        return []

    # Get all pitches for these criteria
    pitches = db.exec(
        select(Pitch)
        .where(Pitch.criterion_id.in_(criterion_ids))
        .order_by(Pitch.criterion_id, Pitch.created_at)
    ).all()

    return [PitchResponse.from_model(p) for p in pitches]


# --- Pitch Generation (SSE Streaming) ---


def _format_inventory_text(inventory_items: list[InventoryItem], db: Session) -> str:
    """Format inventory items grouped by store with priority"""
    inventory_by_store = {}
    for item in inventory_items:
        store = db.get(GroceryStore, item.store_id)
        store_name = store.name if store else "Unknown Store"
        if store_name not in inventory_by_store:
            inventory_by_store[store_name] = []
        inventory_by_store[store_name].append(item)

    inventory_text = ""
    for store_name, items in inventory_by_store.items():
        inventory_text += f"\n## {store_name}\n"
        for item in items:
            priority_label = f"({item.priority} priority)"
            inventory_text += (
                f"- {item.quantity} {item.unit} "
                f"{item.ingredient_name} {priority_label}\n"
            )
    return inventory_text


@router.get("/sessions/{session_id}/generate-pitches")
async def generate_pitches(session_id: UUID, db: Session = Depends(get_session)):
    """
    Generate recipe pitches for all criteria in a session via SSE streaming.
    Pitches are saved to database as they're generated.
    """

    async def stream_generation():
        try:
            # Verify session exists
            session = db.get(PlanningSession, session_id)
            if not session:
                error_data = json.dumps({"error": True, "message": "Session not found"})
                yield f"data: {error_data}\n\n"
                return

            # Load criteria for this session
            criteria = db.exec(
                select(MealCriterion)
                .where(MealCriterion.session_id == session_id)
                .order_by(MealCriterion.created_at)
            ).all()

            if not criteria:
                error_data = json.dumps(
                    {"error": True, "message": "No criteria found for session"}
                )
                yield f"data: {error_data}\n\n"
                return

            # Load household context from database
            household_profile = db.exec(select(HouseholdProfile)).first()
            pantry = db.exec(select(Pantry)).first()
            grocery_stores = db.exec(select(GroceryStore)).all()
            inventory_items = db.exec(select(InventoryItem)).all()

            # Format context for BAML
            household_profile_text = (
                household_profile.content if household_profile else ""
            )
            pantry_text = pantry.content if pantry else ""

            # Format grocery stores
            grocery_stores_text = "\n".join(
                f"- {store.name}: {store.description}" for store in grocery_stores
            )

            # Format inventory grouped by store with priority
            inventory_text = _format_inventory_text(inventory_items, db)

            # Sequential generation per criterion
            total_criteria = len(criteria)
            for criterion_index, criterion in enumerate(criteria, start=1):
                num_pitches = 3 * criterion.slots

                # Send progress event for criterion start
                progress_data = json.dumps(
                    {
                        "progress": True,
                        "criterion_index": criterion_index,
                        "total_criteria": total_criteria,
                        "criterion_description": criterion.description,
                        "generating_count": num_pitches,
                    }
                )
                yield f"data: {progress_data}\n\n"

                # Call BAML to generate pitches for this criterion
                pitches = await b.GenerateRecipePitches(
                    inventory=inventory_text,
                    pantry_staples=pantry_text,
                    grocery_stores=grocery_stores_text,
                    household_profile=household_profile_text,
                    additional_context=criterion.description,
                    num_pitches=num_pitches,
                )

                # Save each pitch and stream it
                for pitch_index, pitch in enumerate(pitches, start=1):
                    # Save to database
                    db_pitch = Pitch(
                        criterion_id=criterion.id,
                        name=pitch.name,
                        blurb=pitch.blurb,
                        why_make_this=pitch.why_make_this,
                        inventory_ingredients=[
                            {
                                "name": ing.name,
                                "quantity": ing.quantity,
                                "unit": ing.unit,
                            }
                            for ing in pitch.inventory_ingredients
                        ],
                        active_time_minutes=pitch.active_time_minutes,
                    )
                    db.add(db_pitch)
                    db.commit()
                    db.refresh(db_pitch)

                    # Stream pitch event
                    pitch_data = json.dumps(
                        {
                            "pitch": True,
                            "criterion_id": str(criterion.id),
                            "pitch_index": pitch_index,
                            "total_for_criterion": num_pitches,
                            "data": {
                                "id": str(db_pitch.id),
                                "name": db_pitch.name,
                                "blurb": db_pitch.blurb,
                                "why_make_this": db_pitch.why_make_this,
                                "inventory_ingredients": db_pitch.inventory_ingredients,
                                "active_time_minutes": db_pitch.active_time_minutes,
                            },
                        }
                    )
                    yield f"data: {pitch_data}\n\n"

            # Send completion event
            completion_data = json.dumps({"complete": True})
            yield f"data: {completion_data}\n\n"

        except Exception as e:
            error_data = json.dumps({"error": True, "message": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        stream_generation(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
