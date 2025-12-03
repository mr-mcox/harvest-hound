"""Thin wrapper exposing BAML functions to routes."""

import json
from collections.abc import AsyncGenerator

from baml_client import b
from baml_client.types import Dish


async def get_dishes(ingredient: str) -> list[Dish]:
    """Get creative dish suggestions featuring the given ingredient."""
    return await b.NameDishes(ingredient)


async def stream_dishes(ingredient: str) -> AsyncGenerator[str, None]:
    """Stream dish suggestions one at a time as SSE events."""
    try:
        stream = b.stream.NameDishes(ingredient)
        last_count = 0

        async for partial in stream:
                for dish in partial[last_count:]:
                    dish_data = json.dumps(
                        {
                            "name": dish.name,
                            "description": dish.description,
                        }
                    )
                    yield f"data: {dish_data}\n\n"
                last_count = len(partial)

        yield f"data: {json.dumps({'complete': True})}\n\n"

    except Exception as e:
        error_data = json.dumps(
            {
                "error": True,
                "message": str(e),
            }
        )
        yield f"data: {error_data}\n\n"
