"""
API routes for Harvest Hound
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from models import MealCriterion, PlanningSession, db_health, get_session

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
