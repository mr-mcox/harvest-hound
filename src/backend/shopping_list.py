"""
Shopping list computation logic

Computes grocery shopping lists from planned recipes, subtracting claimed inventory.
"""

from collections import defaultdict
from decimal import Decimal, InvalidOperation
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import Session, select

from models import IngredientClaim, Recipe, RecipeState, ShoppingListSelection


class ShoppingListItem(BaseModel):
    """A single item on the shopping list"""

    ingredient_name: str
    total_quantity: str  # Aggregated quantities as string (e.g., "2 cups + 1 whole")
    purchase_likelihood: float  # Average likelihood across recipes
    used_in_recipes: list[str]  # Recipe names that use this ingredient
    checked: bool = False  # Selection state from ShoppingListSelection


class ShoppingListResponse(BaseModel):
    """Complete shopping list with grocery items and pantry staples"""

    grocery_items: list[ShoppingListItem]  # likelihood >= 0.3, sorted DESC
    pantry_staples: list[ShoppingListItem]  # likelihood < 0.3


def get_ingredient_stats(session: Session) -> dict[str, dict[str, int]]:
    """
    Derive ingredient purchase statistics from reviewed selections.

    Aggregates across all reviewed sessions globally to learn household
    purchasing patterns over time.

    Args:
        session: Database session

    Returns:
        Dict mapping lowercase ingredient name to stats dict with:
        - sessions_observed: Number of reviewed sessions containing this ingredient
        - times_purchased: Number of times ingredient was checked (purchased)
    """
    # Query all reviewed selections
    reviewed_selections = session.exec(
        select(ShoppingListSelection).where(
            ShoppingListSelection.reviewed_at.is_not(None)
        )
    ).all()

    if not reviewed_selections:
        return {}

    # Aggregate by lowercase ingredient name
    stats: dict[str, dict[str, int]] = {}
    for selection in reviewed_selections:
        key = selection.ingredient_name.lower()
        if key not in stats:
            stats[key] = {"sessions_observed": 0, "times_purchased": 0}
        stats[key]["sessions_observed"] += 1
        if selection.checked:
            stats[key]["times_purchased"] += 1

    return stats


def bayesian_update(
    prior: float, sessions_observed: int, times_purchased: int
) -> float:
    """
    Compute Bayesian posterior likelihood from LLM prior and historical data.

    Uses weighted average where weights shift from prior (LLM knowledge) toward
    evidence (user behavior) as more sessions accumulate.

    Args:
        prior: LLM-generated purchase_likelihood (0.0-1.0)
        sessions_observed: Number of reviewed sessions with this ingredient
        times_purchased: Number of times ingredient was checked (purchased)

    Returns:
        Posterior likelihood (0.0-1.0) blending prior and evidence
    """
    if sessions_observed == 0:
        return prior

    empirical = times_purchased / sessions_observed

    # Weight function: favor prior when data is sparse, evidence when abundant
    # w_prior starts at 10, drops to minimum of 5 as sessions accumulate
    # w_evidence grows linearly with sessions
    w_prior = max(5, 10 - sessions_observed)
    w_evidence = sessions_observed

    posterior = (prior * w_prior + empirical * w_evidence) / (w_prior + w_evidence)
    return posterior


def normalize_unit(unit: str) -> str:
    """
    Normalize unit for comparison by removing trailing 's' for plurals.

    Examples:
        "cloves" -> "clove"
        "cups" -> "cup"
        "tsp" -> "tsp" (unchanged)
    """
    if unit.endswith("s") and len(unit) > 1:
        return unit[:-1]
    return unit


def pluralize_unit(unit: str, quantity: Decimal) -> str:
    """
    Return appropriate unit form based on quantity.

    Args:
        unit: Base unit (normalized or original)
        quantity: Numeric quantity

    Returns:
        Pluralized unit if quantity != 1, otherwise singular

    Examples:
        "cup", 2 -> "cups"
        "clove", 5 -> "cloves"
        "each", 3 -> "each" (no pluralization)
        "medium", 2 -> "medium" (size descriptor, no pluralization)
    """
    # Units that never pluralize (already represent plural/collective form)
    NON_PLURALIZING_UNITS = {
        "each",
        # Size descriptors
        "small",
        "medium",
        "large",
        "extra-large",
        "xl",
        # Already plural or collective
        "to taste",
    }

    unit_lower = unit.lower()

    # If unit is in the non-pluralizing set, return as-is
    if unit_lower in NON_PLURALIZING_UNITS:
        return unit

    # Singular form for quantity = 1
    if quantity == 1:
        return unit

    # Add 's' if not already present
    if not unit.endswith("s"):
        return unit + "s"
    return unit


def try_parse_quantity(quantity_str: str) -> Decimal | None:
    """
    Try to parse quantity string as a decimal number.

    Args:
        quantity_str: String like "6", "1.5", "2-3", "to taste"

    Returns:
        Decimal if parseable, None otherwise
    """
    try:
        return Decimal(quantity_str.strip())
    except (InvalidOperation, ValueError):
        return None


def aggregate_quantities(quantities: list[str], units: list[str]) -> str:
    """
    Aggregate quantities intelligently: sum if all numeric and same normalized unit,
    otherwise concatenate with " + ".

    Args:
        quantities: List of quantity strings (e.g., ["6", "4", "6"])
        units: List of unit strings (e.g., ["clove", "clove", "cloves"])

    Returns:
        Aggregated quantity string (e.g., "16 cloves" or "6 clove + to taste clove")
    """
    # Normalize all units
    normalized_units = [normalize_unit(u) for u in units]

    # Check if all units normalize to the same thing
    if len(set(normalized_units)) != 1:
        # Different units, just concatenate
        return " + ".join(f"{q} {u}" for q, u in zip(quantities, units))

    base_unit = normalized_units[0]

    # Try to parse all quantities as numbers
    parsed = [try_parse_quantity(q) for q in quantities]

    # If all are numeric, sum them
    if all(p is not None for p in parsed):
        total = sum(parsed)  # type: ignore
        # Use appropriate plural form
        display_unit = pluralize_unit(base_unit, total)
        # Format without unnecessary decimal places
        if total % 1 == 0:
            return f"{int(total)} {display_unit}"
        else:
            return f"{total} {display_unit}"

    # Otherwise, fall back to concatenation
    return " + ".join(f"{q} {u}" for q, u in zip(quantities, units))


def _get_claimed_ingredients(session: Session, recipes: list[Recipe]) -> set[tuple]:
    """
    Get set of (recipe_id, ingredient_name_lower) tuples for claimed ingredients.

    Claimed ingredients are those sourced from inventory and should be
    excluded from the shopping list.
    """
    claimed = set()
    for recipe in recipes:
        claims = session.exec(
            select(IngredientClaim).where(IngredientClaim.recipe_id == recipe.id)
        ).all()
        for claim in claims:
            claimed.add((recipe.id, claim.ingredient_name.lower()))
    return claimed


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
    3. Apply Bayesian refinement using historical purchase data
    4. Split into grocery (≥0.3) and pantry (<0.3)
    5. Sort grocery items by likelihood DESC

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

    # Get claimed ingredients (from inventory) to exclude from shopping list
    claimed_ingredients = _get_claimed_ingredients(session, recipes)

    # Aggregate ingredients
    # Key: ingredient_name (lowercase for matching)
    # Value: {quantities: [str], units: [str], likelihoods: [float], recipes: [str]}
    aggregated = defaultdict(
        lambda: {"quantities": [], "units": [], "likelihoods": [], "recipes": []}
    )

    for recipe in recipes:
        for ing in recipe.ingredients:
            ingredient_name = ing["name"]
            ingredient_name_lower = ingredient_name.lower()

            # Skip if claimed from inventory
            if (recipe.id, ingredient_name_lower) in claimed_ingredients:
                continue

            # Aggregate - store quantities and units separately
            key = ingredient_name_lower
            aggregated[key]["quantities"].append(ing["quantity"])
            aggregated[key]["units"].append(ing["unit"])
            aggregated[key]["likelihoods"].append(ing.get("purchase_likelihood", 0.5))
            aggregated[key]["recipes"].append(recipe.name)
            # Store original name (first occurrence) for display
            if "display_name" not in aggregated[key]:
                aggregated[key]["display_name"] = ingredient_name

    # Load selections for this session to populate checked state
    selections = session.exec(
        select(ShoppingListSelection).where(
            ShoppingListSelection.session_id == planning_session_id
        )
    ).all()
    selection_map = {s.ingredient_name.lower(): s.checked for s in selections}

    # Get historical ingredient stats for Bayesian refinement
    ingredient_stats = get_ingredient_stats(session)

    # Build shopping list items
    grocery_items = []
    pantry_staples = []

    for ingredient_key, data in aggregated.items():
        # Intelligently aggregate quantities (sum if possible, otherwise concatenate)
        total_quantity = aggregate_quantities(data["quantities"], data["units"])

        # Average likelihood across recipes (LLM prior)
        avg_likelihood = sum(data["likelihoods"]) / len(data["likelihoods"])

        # Apply Bayesian refinement if historical data exists
        stats = ingredient_stats.get(ingredient_key)
        if stats:
            avg_likelihood = bayesian_update(
                prior=avg_likelihood,
                sessions_observed=stats["sessions_observed"],
                times_purchased=stats["times_purchased"],
            )

        # Deduplicate recipe names
        unique_recipes = sorted(set(data["recipes"]))

        # Look up checked state from selections (default False)
        checked = selection_map.get(ingredient_key, False)

        item = ShoppingListItem(
            ingredient_name=data["display_name"],
            total_quantity=total_quantity,
            purchase_likelihood=avg_likelihood,
            used_in_recipes=unique_recipes,
            checked=checked,
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
