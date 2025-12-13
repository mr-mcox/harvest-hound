"""
API routes for inventory management (parse, bulk save, list)
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from baml_client import b
from models import (
    ClaimState,
    GroceryStore,
    IngredientClaim,
    InventoryItem,
    Recipe,
    get_session,
)
from schemas import (
    InventoryBulkRequest,
    InventoryItemResponse,
    InventoryItemUpdate,
    InventoryParseRequest,
    InventoryParseResponse,
    InventoryWithClaimsResponse,
    ParsedIngredient,
    RecipeClaimSummary,
)

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.post("/parse", response_model=InventoryParseResponse)
async def parse_inventory(request: InventoryParseRequest):
    """Parse free-text inventory using BAML. Returns parsed items without saving."""
    result = await b.ExtractIngredients(
        text=request.free_text,
        configuration_instructions=request.configuration_instructions,
    )

    ingredients = [
        ParsedIngredient(
            ingredient_name=ing.name,
            quantity=ing.quantity,
            unit=ing.unit,
            priority=ing.priority,
            portion_size=ing.portion_size,
        )
        for ing in result.ingredients
    ]

    return InventoryParseResponse(
        ingredients=ingredients,
        parsing_notes=result.parsing_notes,
    )


@router.post("/bulk")
async def bulk_save_inventory(
    request: InventoryBulkRequest,
    session: Session = Depends(get_session),
):
    """Bulk save inventory items to database."""
    # Get default store (first one, auto-created by seed_defaults)
    store = session.exec(select(GroceryStore)).first()
    if not store:
        # This shouldn't happen if seed_defaults ran, but handle gracefully
        store = GroceryStore(name="Default Store", description="Auto-created store")
        session.add(store)
        session.commit()
        session.refresh(store)

    for item in request.items:
        inventory_item = InventoryItem(
            store_id=store.id,
            ingredient_name=item.ingredient_name,
            quantity=item.quantity,
            unit=item.unit,
            priority=item.priority,
            portion_size=item.portion_size,
        )
        session.add(inventory_item)

    session.commit()

    return {"saved_count": len(request.items)}


@router.get("", response_model=list[InventoryItemResponse])
async def list_inventory(session: Session = Depends(get_session)):
    """List all inventory items (excludes soft-deleted items)."""
    items = session.exec(
        select(InventoryItem).where(InventoryItem.deleted_at.is_(None))
    ).all()
    return [
        InventoryItemResponse(
            id=item.id,
            ingredient_name=item.ingredient_name,
            quantity=item.quantity,
            unit=item.unit,
            priority=item.priority,
            portion_size=item.portion_size,
            added_at=item.added_at,
        )
        for item in items
    ]


@router.delete("/{item_id}")
async def delete_inventory_item(item_id: int, session: Session = Depends(get_session)):
    """Soft delete an inventory item by setting deleted_at timestamp."""
    from datetime import UTC, datetime

    from fastapi import HTTPException

    # Find the item
    item = session.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    # Soft delete by setting deleted_at
    item.deleted_at = datetime.now(UTC)
    session.add(item)
    session.commit()

    return {"deleted": True, "id": item_id}


@router.patch("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: int,
    update: InventoryItemUpdate,
    session: Session = Depends(get_session),
):
    """Update inventory item (partial update for quantity and/or priority)."""
    from fastapi import HTTPException

    # Find the item
    item = session.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    # Validate quantity > 0 if provided
    if update.quantity is not None:
        if update.quantity <= 0:
            raise HTTPException(
                status_code=400, detail="Quantity must be greater than 0"
            )
        item.quantity = update.quantity

    # Update priority if provided
    if update.priority is not None:
        item.priority = update.priority

    session.add(item)
    session.commit()
    session.refresh(item)

    return InventoryItemResponse(
        id=item.id,
        ingredient_name=item.ingredient_name,
        quantity=item.quantity,
        unit=item.unit,
        priority=item.priority,
        portion_size=item.portion_size,
        added_at=item.added_at,
    )


@router.get("/with-claims", response_model=list[InventoryWithClaimsResponse])
async def list_inventory_with_claims(session: Session = Depends(get_session)):
    """List inventory items with claims (available qty and claiming recipes)."""
    # Get all non-deleted inventory items
    items = session.exec(
        select(InventoryItem).where(InventoryItem.deleted_at.is_(None))
    ).all()

    # Get all RESERVED claims with recipe names (using join)
    reserved_claims = session.exec(
        select(IngredientClaim, Recipe)
        .join(Recipe, IngredientClaim.recipe_id == Recipe.id)
        .where(IngredientClaim.state == ClaimState.RESERVED)
    ).all()

    # Build a mapping: inventory_item_id -> list of claims
    claims_by_item: dict[int, list[RecipeClaimSummary]] = {}
    reserved_by_item: dict[int, float] = {}

    for claim, recipe in reserved_claims:
        item_id = claim.inventory_item_id

        # Track total reserved quantity
        reserved_by_item[item_id] = reserved_by_item.get(item_id, 0.0) + claim.quantity

        # Build claim summary
        if item_id not in claims_by_item:
            claims_by_item[item_id] = []

        claims_by_item[item_id].append(
            RecipeClaimSummary(
                recipe_id=str(recipe.id),
                recipe_name=recipe.name,
                quantity=claim.quantity,
                unit=claim.unit,
            )
        )

    # Build response with available quantities
    result = []
    for item in items:
        reserved = reserved_by_item.get(item.id, 0.0)
        available = max(0.0, item.quantity - reserved)

        result.append(
            InventoryWithClaimsResponse(
                id=item.id,
                ingredient_name=item.ingredient_name,
                quantity=item.quantity,
                available=available,
                unit=item.unit,
                priority=item.priority,
                portion_size=item.portion_size,
                added_at=item.added_at,
                claims=claims_by_item.get(item.id, []),
            )
        )

    return result
