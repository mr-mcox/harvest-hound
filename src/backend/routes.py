"""
API routes for Harvest Hound
"""

from fastapi import APIRouter

from baml_functions import get_dishes
from models import db_health

router = APIRouter(prefix="/api")


@router.get("/hello")
def hello():
    """Hello world endpoint - verifies stack is working"""
    return {
        "message": "Hello from Harvest Hound!",
        "db_ok": db_health(),
    }


@router.get("/dishes")
async def dishes(ingredient: str):
    """Get creative dish suggestions featuring an ingredient"""
    dish_list = await get_dishes(ingredient)
    return [{"name": d.name, "description": d.description} for d in dish_list]
