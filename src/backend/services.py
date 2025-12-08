"""
Business logic services for Harvest Hound
"""

from copy import copy

from sqlmodel import Session, select

from models import (
    ClaimState,
    GroceryStore,
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
    lookup = build_inventory_lookup(session)

    recipe = Recipe(
        session_id=recipe_data.get("session_id"),
        criterion_id=recipe_data.get("criterion_id"),
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
    session.flush()

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

    session.commit()
    session.refresh(recipe)
    for claim in claims:
        session.refresh(claim)

    return recipe, claims


def calculate_available_inventory(session: Session) -> list[InventoryItem]:
    """
    Calculate available inventory by subtracting reserved claims.

    Returns a list of InventoryItem-like objects with decremented quantities.
    Only RESERVED claims reduce availability (cooked/abandoned recipes have
    claims deleted).

    Args:
        session: Database session

    Returns:
        List of InventoryItem copies with adjusted quantities
    """
    items = session.exec(select(InventoryItem)).all()
    reserved_claims = session.exec(
        select(IngredientClaim).where(IngredientClaim.state == ClaimState.RESERVED)
    ).all()

    claimed_by_item: dict[int, float] = {}
    for claim in reserved_claims:
        item_id = claim.inventory_item_id
        claimed_by_item[item_id] = claimed_by_item.get(item_id, 0.0) + claim.quantity

    available = []
    for item in items:
        adjusted = copy(item)  # Avoid modifying the original
        claimed = claimed_by_item.get(item.id, 0.0)
        adjusted.quantity = max(0.0, item.quantity - claimed)
        available.append(adjusted)

    return available


def format_available_inventory(
    available_items: list[InventoryItem], session: Session
) -> str:
    """
    Format available inventory items grouped by store for BAML prompt.

    Args:
        available_items: List of InventoryItem with adjusted quantities
        session: Database session for store lookups

    Returns:
        Formatted string for BAML prompt
    """
    inventory_by_store: dict[str, list[InventoryItem]] = {}
    for item in available_items:
        store = session.get(GroceryStore, item.store_id)
        store_name = store.name if store else "Unknown Store"
        if store_name not in inventory_by_store:
            inventory_by_store[store_name] = []
        inventory_by_store[store_name].append(item)

    inventory_text = ""
    for store_name, items in inventory_by_store.items():
        inventory_text += f"\n## {store_name}\n"
        for item in items:
            priority_label = f"({item.priority} priority)"
            inventory_text += (
                f"- {item.quantity} {item.unit} "
                f"{item.ingredient_name} {priority_label}\n"
            )

    return inventory_text
