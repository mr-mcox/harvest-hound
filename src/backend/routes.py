"""
API routes for Harvest Hound
"""

from fastapi import APIRouter

from models import db_health

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    """Health check endpoint - verifies stack is working"""
    return {
        "status": "healthy",
        "db_ok": db_health(),
    }
