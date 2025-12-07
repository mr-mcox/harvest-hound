"""
API routes for Harvest Hound
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from models import PlanningSession, db_health, get_session

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
