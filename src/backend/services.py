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
    MealCriterion,
    Pitch,
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


def is_pitch_valid(pitch: Pitch, available_inventory: list[InventoryItem]) -> bool:
    """
    Check if a pitch can be made with available inventory.

    Validation rules (aggressive approach - prefer false negatives):
    - All ingredients must exist in inventory (case-insensitive matching)
    - Units must match exactly (unit mismatch = invalid pitch)
    - Available quantity must be >= required quantity

    Args:
        pitch: Pitch to validate
        available_inventory: List of InventoryItem with decremented quantities

    Returns:
        True if all pitch ingredients can be satisfied, False otherwise
    """
    # Build lookup for fast case-insensitive matching
    inventory_lookup = {
        item.ingredient_name.lower(): item for item in available_inventory
    }

    # Check each ingredient requirement
    for pitch_ingredient in pitch.inventory_ingredients:
        ingredient_name = pitch_ingredient["name"]
        required_quantity = pitch_ingredient["quantity"]
        required_unit = pitch_ingredient["unit"]

        # Find matching inventory item (case-insensitive)
        inventory_item = inventory_lookup.get(ingredient_name.lower())

        if inventory_item is None:
            # Ingredient not in inventory
            return False

        if inventory_item.unit != required_unit:
            # Aggressive invalidation: unit mismatch
            return False

        if inventory_item.quantity < required_quantity:
            # Insufficient quantity
            return False

    # All ingredients satisfied
    return True


def filter_valid_pitches(
    pitches: list[Pitch], available_inventory: list[InventoryItem]
) -> list[Pitch]:
    """
    Filter a list of pitches to only those that can be made with available inventory.

    Args:
        pitches: List of pitches to filter
        available_inventory: List of InventoryItem with decremented quantities

    Returns:
        List of valid pitches (preserves original order)
    """
    return [pitch for pitch in pitches if is_pitch_valid(pitch, available_inventory)]


def calculate_pitch_generation_delta(session: Session, session_id) -> int:
    """
    Calculate how many pitches to generate for a planning session.

    Formula:
    - total_slots = sum of all criterion slots
    - fleshed_recipes = count of PLANNED recipes
    - unfilled_slots = total_slots - fleshed_recipes
    - target_pitches = unfilled_slots * 3
    - delta = max(0, target_pitches - valid_pitches)

    Args:
        session: Database session
        session_id: UUID of the planning session

    Returns:
        Number of pitches to generate (0 if all slots filled or enough pitches)
    """
    # Get all criteria for this session
    criteria = session.exec(
        select(MealCriterion).where(MealCriterion.session_id == session_id)
    ).all()

    if not criteria:
        return 0

    # Calculate total slots across all criteria
    total_slots = sum(criterion.slots for criterion in criteria)

    # Count fleshed-out recipes (PLANNED state only)
    fleshed_recipes_count = session.exec(
        select(Recipe).where(
            Recipe.session_id == session_id,
            Recipe.state == RecipeState.PLANNED,
        )
    ).all()
    fleshed_count = len(fleshed_recipes_count)

    # Calculate unfilled slots
    unfilled_slots = max(0, total_slots - fleshed_count)

    if unfilled_slots == 0:
        # All slots filled, no generation needed
        return 0

    # Calculate target: 3 pitches per unfilled slot
    target_pitches = unfilled_slots * 3

    # Get all pitches for these criteria
    criterion_ids = [c.id for c in criteria]
    pitches = session.exec(
        select(Pitch).where(Pitch.criterion_id.in_(criterion_ids))
    ).all()

    # Filter to only valid pitches (can be made with available inventory)
    available_inventory = calculate_available_inventory(session)
    valid_pitches = filter_valid_pitches(list(pitches), available_inventory)
    valid_count = len(valid_pitches)

    # Calculate delta: how many more pitches needed
    delta = max(0, target_pitches - valid_count)

    return delta


def calculate_criterion_pitch_delta(
    session: Session, session_id, criterion: MealCriterion, available_inventory: list
) -> int:
    """
    Calculate how many pitches to generate for a single criterion.

    Returns 0 if criterion has all slots filled or already has enough pitches.
    """
    # Count PLANNED recipes for this criterion
    planned_recipes = session.exec(
        select(Recipe).where(
            Recipe.session_id == session_id,
            Recipe.criterion_id == criterion.id,
            Recipe.state == RecipeState.PLANNED,
        )
    ).all()
    unfilled_slots = max(0, criterion.slots - len(planned_recipes))

    if unfilled_slots == 0:
        return 0

    # Target: 3 pitches per unfilled slot
    target = unfilled_slots * 3

    # Count existing valid pitches for this criterion
    criterion_pitches = session.exec(
        select(Pitch).where(Pitch.criterion_id == criterion.id)
    ).all()
    valid_pitches = filter_valid_pitches(list(criterion_pitches), available_inventory)
    delta = max(0, target - len(valid_pitches))

    return delta


def calculate_generation_plan(
    session: Session, session_id, available_inventory: list
) -> list[tuple[MealCriterion, int]]:
    """
    Determine which criteria need pitches and how many.

    Returns list of (criterion, num_pitches) tuples.
    Criteria with all slots filled are excluded (delta = 0).

    This is pure business logic - testable without SSE or BAML.
    """
    criteria = session.exec(
        select(MealCriterion)
        .where(MealCriterion.session_id == session_id)
        .order_by(MealCriterion.created_at)
    ).all()

    plan = []
    for criterion in criteria:
        delta = calculate_criterion_pitch_delta(
            session, session_id, criterion, available_inventory
        )
        if delta > 0:
            plan.append((criterion, delta))

    return plan
