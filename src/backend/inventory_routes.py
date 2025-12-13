"""
API routes for inventory management (parse, bulk save, list)
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from baml_client import b
from models import GroceryStore, InventoryItem, get_session
from schemas import (
    InventoryBulkRequest,
    InventoryItemResponse,
    InventoryParseRequest,
    InventoryParseResponse,
    ParsedIngredient,
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
