"""
Business logic services for Harvest Hound
"""

from sqlmodel import Session, select

from models import (
    ClaimState,
    IngredientClaim,
    InventoryItem,
    Recipe,
    RecipeState,
)


def build_inventory_lookup(session: Session) -> dict[str, InventoryItem]:
    """
    Build a lookup dict mapping ingredient names (lowercased) to InventoryItem.

    Returns:
        Dict with lowercased ingredient names as keys, InventoryItem as values
    """
    items = session.exec(select(InventoryItem)).all()
    return {item.ingredient_name.lower(): item for item in items}


def match_ingredient_to_inventory(
    ingredient_name: str,
    lookup: dict[str, InventoryItem],
) -> InventoryItem | None:
    """
    Match an ingredient name to an inventory item using exact (case-insensitive) match.

    Args:
        ingredient_name: Name from recipe ingredient
        lookup: Dict from build_inventory_lookup()

    Returns:
        InventoryItem if matched, None otherwise
    """
    return lookup.get(ingredient_name.lower())


def parse_quantity(quantity_str: str) -> float:
    """
    Parse quantity string to float.
    Handles numeric strings and defaults to 1.0 for non-numeric (e.g., "to taste").

    Args:
        quantity_str: Quantity from recipe ingredient (e.g., "2", "1.5", "to taste")

    Returns:
        Parsed float value, or 1.0 if not parseable
    """
    try:
        return float(quantity_str)
    except (ValueError, TypeError):
        return 1.0


def create_recipe_with_claims(
    session: Session,
    recipe_data: dict,
) -> tuple[Recipe, list[IngredientClaim]]:
    """
    Atomically create a Recipe and its IngredientClaims for matching inventory items.

    All operations happen in a single transaction - if any fail, all are rolled back.

    Args:
        session: Database session
        recipe_data: Dict with recipe fields from BAML output

    Returns:
        Tuple of (saved Recipe, list of created IngredientClaims)
    """
    # Build inventory lookup
    lookup = build_inventory_lookup(session)

    # Create recipe
    recipe = Recipe(
        name=recipe_data["name"],
        description=recipe_data["description"],
        ingredients=recipe_data["ingredients"],
        instructions=recipe_data["instructions"],
        active_time_minutes=recipe_data["active_time_minutes"],
        total_time_minutes=recipe_data["total_time_minutes"],
        servings=recipe_data["servings"],
        notes=recipe_data.get("notes"),
        state=RecipeState.PLANNED,
    )
    session.add(recipe)
    session.flush()  # Get recipe ID without committing

    # Create claims for matching ingredients
    claims = []
    for ingredient in recipe_data["ingredients"]:
        ing_name = ingredient["name"]
        inventory_item = match_ingredient_to_inventory(ing_name, lookup)

        if inventory_item is not None:
            quantity = parse_quantity(ingredient["quantity"])
            claim = IngredientClaim(
                recipe_id=recipe.id,
                inventory_item_id=inventory_item.id,
                ingredient_name=ing_name,
                quantity=quantity,
                unit=ingredient["unit"],
                state=ClaimState.RESERVED,
            )
            session.add(claim)
            claims.append(claim)

    # Commit all together (atomic)
    session.commit()

    # Refresh to get IDs
    session.refresh(recipe)
    for claim in claims:
        session.refresh(claim)

    return recipe, claims
