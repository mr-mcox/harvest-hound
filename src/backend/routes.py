"""
API routes for Harvest Hound
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from baml_functions import get_dishes, stream_dishes
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


@router.get("/dishes/stream")
async def dishes_stream(ingredient: str):
    """Stream creative dish suggestions one at a time via SSE"""
    return StreamingResponse(
        stream_dishes(ingredient),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
