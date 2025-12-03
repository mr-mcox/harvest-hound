"""Thin wrapper exposing BAML functions to routes."""

from baml_client import b
from baml_client.types import Dish


async def get_dishes(ingredient: str) -> list[Dish]:
    """Get creative dish suggestions featuring the given ingredient."""
    return await b.NameDishes(ingredient)
