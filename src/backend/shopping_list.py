"""
Shopping list computation logic

Computes grocery shopping lists from planned recipes, subtracting claimed inventory.
"""

from collections import defaultdict
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import Session, select

from models import IngredientClaim, Recipe, RecipeState


class ShoppingListItem(BaseModel):
    """A single item on the shopping list"""

    ingredient_name: str
    total_quantity: str  # Aggregated quantities as string (e.g., "2 cups + 1 whole")
    purchase_likelihood: float  # Average likelihood across recipes
    used_in_recipes: list[str]  # Recipe names that use this ingredient


class ShoppingListResponse(BaseModel):
    """Complete shopping list with grocery items and pantry staples"""

    grocery_items: list[ShoppingListItem]  # likelihood >= 0.3, sorted DESC
    pantry_staples: list[ShoppingListItem]  # likelihood < 0.3


def compute_shopping_list(
    session: Session, planning_session_id: UUID
) -> ShoppingListResponse:
    """
    Compute shopping list for a planning session.

    Algorithm:
    1. Get all PLANNED recipes in the session
    2. For each ingredient in each recipe:
       - Skip if has a claim (from inventory)
       - Aggregate by ingredient name
       - Track quantities, likelihood, and recipe names
    3. Split into grocery (≥0.3) and pantry (<0.3)
    4. Sort grocery items by likelihood DESC

    Args:
        session: Database session
        planning_session_id: UUID of the planning session

    Returns:
        ShoppingListResponse with grocery_items and pantry_staples
    """
    # Get all planned recipes for this session
    recipes = session.exec(
        select(Recipe).where(
            Recipe.session_id == planning_session_id,
            Recipe.state == RecipeState.PLANNED,
        )
    ).all()

    if not recipes:
        return ShoppingListResponse(grocery_items=[], pantry_staples=[])

    # Get all claims to check what's from inventory
    claimed_ingredients = set()
    for recipe in recipes:
        claims = session.exec(
            select(IngredientClaim).where(IngredientClaim.recipe_id == recipe.id)
        ).all()
        for claim in claims:
            # Key is (recipe_id, ingredient_name) to handle same ingredient
            # in different recipes
            claimed_ingredients.add((recipe.id, claim.ingredient_name.lower()))

    # Aggregate ingredients
    # Key: ingredient_name (lowercase for matching)
    # Value: {quantities: [str], likelihoods: [float], recipes: [str]}
    aggregated = defaultdict(
        lambda: {"quantities": [], "likelihoods": [], "recipes": []}
    )

    for recipe in recipes:
        for ing in recipe.ingredients:
            ingredient_name = ing["name"]
            ingredient_name_lower = ingredient_name.lower()

            # Skip if claimed from inventory
            if (recipe.id, ingredient_name_lower) in claimed_ingredients:
                continue

            # Aggregate
            key = ingredient_name_lower
            quantity_str = f"{ing['quantity']} {ing['unit']}"
            aggregated[key]["quantities"].append(quantity_str)
            aggregated[key]["likelihoods"].append(ing.get("purchase_likelihood", 0.5))
            aggregated[key]["recipes"].append(recipe.name)
            # Store original name (first occurrence) for display
            if "display_name" not in aggregated[key]:
                aggregated[key]["display_name"] = ingredient_name

    # Build shopping list items
    grocery_items = []
    pantry_staples = []

    for ingredient_key, data in aggregated.items():
        # Aggregate quantities with " + "
        total_quantity = " + ".join(data["quantities"])

        # Average likelihood across recipes
        avg_likelihood = sum(data["likelihoods"]) / len(data["likelihoods"])

        # Deduplicate recipe names
        unique_recipes = sorted(set(data["recipes"]))

        item = ShoppingListItem(
            ingredient_name=data["display_name"],
            total_quantity=total_quantity,
            purchase_likelihood=avg_likelihood,
            used_in_recipes=unique_recipes,
        )

        # Threshold: <0.3 = pantry, ≥0.3 = grocery
        if avg_likelihood >= 0.3:
            grocery_items.append(item)
        else:
            pantry_staples.append(item)

    # Sort grocery items by likelihood DESC (high confidence first)
    grocery_items.sort(key=lambda x: x.purchase_likelihood, reverse=True)

    return ShoppingListResponse(
        grocery_items=grocery_items,
        pantry_staples=pantry_staples,
    )
