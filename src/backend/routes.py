"""
API routes for Harvest Hound
"""

from fastapi import APIRouter
from models import db_health

router = APIRouter(prefix="/api")


@router.get("/hello")
def hello():
    """Hello world endpoint - verifies stack is working"""
    return {
        "message": "Hello from Harvest Hound!",
        "db_ok": db_health(),
    }
