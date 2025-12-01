"""
Harvest Hound Prototype - YOLO Discovery Phase
No tests, no abstractions, just exploration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
import json
import asyncio
from pydantic import BaseModel
import copy

# Add BAML imports (after running: uv run baml-cli generate)
from baml_client import b
from baml_client.types import Recipe as BAMLRecipe, RecipePitch as BAMLRecipePitch

# Database setup - SQLite for simplicity
engine = create_engine("sqlite:///harvest.db")

# --- Domain Models (Simple and Direct) ---

class Store(SQLModel, table=True):
    """Simple store model - figure out polymorphism later"""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    description: str = ""
    store_type: str = "explicit"  # explicit or definition
    definition: Optional[str] = None  # For LLM-inferred stores
    created_at: datetime = Field(default_factory=datetime.now)

class InventoryItem(SQLModel, table=True):
    """Simple inventory tracking"""
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    store_id: UUID = Field(foreign_key="store.id")
    ingredient_name: str
    quantity: float
    unit: str
    notes: str = ""
    added_at: Optional[datetime] = Field(default_factory=datetime.now)

class Recipe(SQLModel, table=True):
    """Recipe storage - keep it simple"""
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    ingredients_json: str  # Just store as JSON for now
    instructions: str
    source: str = "ai_generated"
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

class MealPlan(SQLModel, table=True):
    """Weekly meal planning"""
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    week_of: datetime
    recipes_json: str  # List of recipe IDs as JSON
    status: str = "draft"  # draft, accepted, completed
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

# Create tables
SQLModel.metadata.create_all(engine)

# --- FastAPI App ---
app = FastAPI(title="Harvest Hound Prototype")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- API Models ---
class CreateStoreRequest(BaseModel):
    name: str
    store_type: str = "explicit"
    description: str = ""
    definition: Optional[str] = None

class AddInventoryRequest(BaseModel):
    ingredient_name: str
    quantity: float
    unit: str
    notes: str = ""

class BulkInventoryRequest(BaseModel):
    free_text: str

class UpdateInventoryRequest(BaseModel):
    quantity: float

class UpdateStoreRequest(BaseModel):
    definition: str

class GenerateRecipesRequest(BaseModel):
    additional_context: str = ""  # Changed from csa_contents
    num_recipes: int = 3

def get_inventory_ingredient_names() -> set:
    """Get set of all ingredient names currently in inventory (for filtering claimed ingredients)"""
    with Session(engine) as session:
        items = session.exec(select(InventoryItem)).all()
        return {item.ingredient_name.lower() for item in items}

def load_initial_inventory() -> dict:
    """
    Load initial inventory state from database as a nested dict for quantity tracking.
    Structure: {store_name: {ingredient_name: (quantity, unit)}}
    """
    with Session(engine) as session:
        stores = session.exec(select(Store)).all()
        inventory_state = {}

        for store in stores:
            if store.store_type == "explicit":
                items = session.exec(
                    select(InventoryItem).where(InventoryItem.store_id == store.id)
                ).all()

                if items:
                    inventory_state[store.name] = {
                        item.ingredient_name: (item.quantity, item.unit)
                        for item in items
                    }

        return inventory_state

def format_inventory_for_prompt(available_inventory: dict = None) -> tuple[str, str]:
    """
    Load all stores and format inventory for LLM prompt, split into explicit and definition stores.
    If available_inventory dict is provided, use it for explicit stores (for quantity tracking).
    Returns (explicit_stores_str, definition_stores_str)
    """
    with Session(engine) as session:
        stores = session.exec(select(Store)).all()

        if not stores:
            return ("No explicit inventory available.", "Common pantry staples (olive oil, butter, salt, pepper, etc.)")

        explicit_parts = []
        definition_parts = []

        for store in stores:
            if store.store_type == "definition":
                # Definition stores - just show the definition
                definition_parts.append(f"{store.name}: {store.definition or store.description}")
            else:
                # Explicit stores - show itemized inventory
                if available_inventory and store.name in available_inventory:
                    # Use the tracked inventory (with decremented quantities)
                    items_dict = available_inventory[store.name]
                    if items_dict:
                        item_list = ", ".join([
                            f"{name} ({qty} {unit})"
                            for name, (qty, unit) in items_dict.items()
                            if qty > 0  # Only show items with quantity remaining
                        ])
                        if item_list:
                            explicit_parts.append(f"{store.name}: {item_list}")
                else:
                    # Use database inventory (initial state)
                    items = session.exec(
                        select(InventoryItem).where(InventoryItem.store_id == store.id)
                    ).all()

                    if items:
                        item_list = ", ".join([
                            f"{i.ingredient_name} ({i.quantity} {i.unit})"
                            for i in items
                        ])
                        explicit_parts.append(f"{store.name}: {item_list}")

        explicit_str = "\n".join(explicit_parts) if explicit_parts else "No explicit inventory available."
        definition_str = "\n".join(definition_parts) if definition_parts else "No definition stores configured."

        return (explicit_str, definition_str)

# --- Endpoints ---

@app.get("/")
async def root():
    """Serve the main UI"""
    return FileResponse("static/index.html")

@app.post("/stores")
async def create_store(request: CreateStoreRequest):
    """Create a new store - simple and direct"""
    with Session(engine) as session:
        store = Store(
            name=request.name,
            description=request.description,
            store_type=request.store_type,
            definition=request.definition
        )
        session.add(store)
        session.commit()
        session.refresh(store)
        return {"id": str(store.id), "name": store.name}

@app.get("/stores")
async def list_stores():
    """Get all stores"""
    with Session(engine) as session:
        stores = session.exec(select(Store)).all()
        return [
            {
                "id": str(s.id),
                "name": s.name,
                "type": s.store_type,
                "description": s.description,
                "definition": s.definition
            }
            for s in stores
        ]

@app.delete("/stores/{store_id}")
async def delete_store(store_id: str):
    """Delete a store and all its inventory"""
    with Session(engine) as session:
        # Delete all inventory items first
        items = session.exec(
            select(InventoryItem).where(InventoryItem.store_id == UUID(store_id))
        ).all()
        for item in items:
            session.delete(item)

        # Delete the store
        store = session.get(Store, UUID(store_id))
        if store:
            session.delete(store)
            session.commit()
            return {"success": True}
        return {"success": False, "error": "Store not found"}

@app.patch("/stores/{store_id}")
async def update_store(store_id: str, request: UpdateStoreRequest):
    """Update store definition (for definition-based stores)"""
    with Session(engine) as session:
        store = session.get(Store, UUID(store_id))
        if store:
            store.definition = request.definition
            session.commit()
            return {"success": True}
        return {"success": False, "error": "Store not found"}

@app.post("/stores/{store_id}/inventory")
async def add_inventory(store_id: str, request: AddInventoryRequest):
    """Add inventory to a store"""
    with Session(engine) as session:
        item = InventoryItem(
            store_id=UUID(store_id),
            ingredient_name=request.ingredient_name,
            quantity=request.quantity,
            unit=request.unit,
            notes=request.notes
        )
        session.add(item)
        session.commit()
        return {"success": True, "item_id": str(item.id)}

@app.post("/stores/{store_id}/inventory/bulk")
async def add_bulk_inventory(store_id: str, request: BulkInventoryRequest):
    """Parse free-text and bulk add inventory using BAML"""
    try:
        # Get store to access definition for parsing context
        with Session(engine) as session:
            store = session.get(Store, UUID(store_id))
            store_context = store.definition if store and store.definition else None

        # Call BAML to extract ingredients with store context
        result = await b.ExtractIngredients(
            text=request.free_text,
            store_context=store_context
        )

        added_items = []
        skipped = []

        with Session(engine) as session:
            for ing in result.ingredients:
                # Skip if missing critical info
                if not ing.name or ing.quantity <= 0:
                    skipped.append(f"{ing.name or 'unknown'} (missing data)")
                    continue

                item = InventoryItem(
                    store_id=UUID(store_id),
                    ingredient_name=ing.name,
                    quantity=ing.quantity,
                    unit=ing.unit or "unit"
                )
                session.add(item)
                added_items.append(f"{ing.quantity} {ing.unit or 'unit'} {ing.name}")

            session.commit()

        return {
            "success": True,
            "added": added_items,
            "skipped": skipped,
            "total": len(added_items),
            "notes": result.parsing_notes
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "added": [],
            "skipped": []
        }

@app.get("/stores/{store_id}/inventory")
async def get_inventory(store_id: str):
    """Get inventory for a store"""
    with Session(engine) as session:
        items = session.exec(
            select(InventoryItem).where(InventoryItem.store_id == UUID(store_id))
        ).all()
        return [
            {
                "id": str(i.id),
                "ingredient": i.ingredient_name,
                "quantity": i.quantity,
                "unit": i.unit
            }
            for i in items
        ]

@app.delete("/inventory/{item_id}")
async def delete_inventory_item(item_id: str):
    """Delete an inventory item"""
    with Session(engine) as session:
        item = session.get(InventoryItem, UUID(item_id))
        if item:
            session.delete(item)
            session.commit()
            return {"success": True}
        return {"success": False, "error": "Item not found"}

@app.patch("/inventory/{item_id}")
async def update_inventory_item(item_id: str, request: UpdateInventoryRequest):
    """Update inventory item quantity"""
    with Session(engine) as session:
        item = session.get(InventoryItem, UUID(item_id))
        if item:
            item.quantity = request.quantity
            session.commit()
            return {"success": True}
        return {"success": False, "error": "Item not found"}

@app.get("/generate-pitches")
async def generate_pitches(
    additional_context: str = "",
    num_pitches: int = 10,
    available_inventory_json: str = ""
):
    """
    Generate lightweight recipe pitches for browsing with quantity-aware ingredient tracking
    Accepts optional available_inventory_json to use decremented inventory state
    """
    async def stream_pitches():
        try:
            # Parse inventory if provided, otherwise load from DB
            current_inventory = None
            if available_inventory_json:
                try:
                    current_inventory = json.loads(available_inventory_json)
                except json.JSONDecodeError:
                    pass  # Fall back to DB inventory

            # Load inventory split by store type, using decremented state if available
            explicit_stores, definition_stores = format_inventory_for_prompt(current_inventory)

            # Call BAML to generate all pitches at once
            pitches = await b.GenerateRecipePitches(
                explicit_stores=explicit_stores,
                definition_stores=definition_stores,
                additional_context=additional_context or "No specific context provided",
                num_pitches=num_pitches
            )

            # Stream pitches one at a time for progressive loading
            for i, pitch in enumerate(pitches):
                pitch_dict = {
                    "name": pitch.name,
                    "blurb": pitch.blurb,
                    "why_make_this": pitch.why_make_this,
                    "key_ingredients": pitch.key_ingredients,
                    "explicit_ingredients": [
                        {"name": ing.name, "quantity": ing.quantity, "unit": ing.unit}
                        for ing in pitch.explicit_ingredients
                    ],
                    "active_time": pitch.active_time_minutes
                }

                data = json.dumps({
                    "index": i,
                    "total": len(pitches),
                    "pitch": pitch_dict
                })
                yield f"data: {data}\n\n"

            # Send completion event
            yield f"data: {json.dumps({'complete': True})}\n\n"

        except Exception as e:
            error_data = json.dumps({
                "error": True,
                "message": str(e)
            })
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        stream_pitches(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

class FleshOutRequest(BaseModel):
    pitch_name: str
    additional_context: str = ""
    explicit_ingredients: list = []  # Ingredients claimed by this pitch
    available_inventory: dict = {}  # Current inventory state (after previous claims)

@app.post("/flesh-out-pitch")
async def flesh_out_pitch(request: FleshOutRequest):
    """
    Generate a full recipe from a selected pitch name with quantity-aware claiming
    Accepts available_inventory dict to track decremented quantities
    """
    try:
        # Use provided inventory state or load fresh from DB
        current_inventory = request.available_inventory if request.available_inventory else load_initial_inventory()

        # Format inventory for prompt
        explicit_stores, definition_stores = format_inventory_for_prompt(current_inventory)

        # Use the pitch name as context for generation
        context_with_pitch = f"{request.additional_context}\n\nFocus on creating a full recipe for: {request.pitch_name}"

        baml_recipe = await b.GenerateSingleRecipe(
            explicit_stores=explicit_stores,
            definition_stores=definition_stores,
            additional_context=context_with_pitch,
            recipes_already_generated=f"Fleshing out: {request.pitch_name}"
        )

        recipe_dict = {
            "name": baml_recipe.name,
            "ingredients": [
                f"{ing.quantity} {ing.unit} {ing.name}"
                for ing in baml_recipe.ingredients
            ],
            "instructions": baml_recipe.instructions,
            "active_time": baml_recipe.active_time_minutes,
            "passive_time": baml_recipe.passive_time_minutes,
            "servings": baml_recipe.servings,
            "notes": baml_recipe.notes
        }

        # Claim the explicit ingredients from the pitch
        # Decrement quantities from current_inventory
        updated_inventory = copy.deepcopy(current_inventory)

        for claimed_ing in request.explicit_ingredients:
            ing_name = claimed_ing["name"]
            ing_qty = claimed_ing["quantity"]
            ing_unit = claimed_ing["unit"]

            # Find this ingredient in the inventory and decrement
            for store_name, items in updated_inventory.items():
                if ing_name in items:
                    current_qty, current_unit = items[ing_name]
                    # Simple subtraction (assuming units match - real version would need unit conversion)
                    new_qty = max(0, current_qty - ing_qty)
                    updated_inventory[store_name][ing_name] = (new_qty, current_unit)
                    break

        return {
            "success": True,
            "recipe": recipe_dict,
            "updated_inventory": updated_inventory,
            "claimed_ingredients": request.explicit_ingredients
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/generate-recipes")  # Changed from POST to GET
async def generate_recipes(
    additional_context: str = "",  # Query param
    num_recipes: int = 3  # Query param
):
    """
    Generate recipes using BAML with SSE streaming
    Auto-loads all store inventories
    """
    async def stream_recipes():
        try:
            # Load inventory from all stores
            available_inventory = format_inventory_for_prompt()

            recipes_generated = []

            # Generate recipes one at a time for better streaming UX
            for i in range(num_recipes):
                # Track what we've already generated to avoid duplicates
                recipes_summary = "\n".join([
                    f"- {r['name']}" for r in recipes_generated
                ]) if recipes_generated else "None yet"

                # Call BAML to generate single recipe
                baml_recipe = await b.GenerateSingleRecipe(
                    available_inventory=available_inventory,
                    additional_context=additional_context or "No specific context provided",
                    recipes_already_generated=recipes_summary
                )

                # Convert BAML recipe to dict for frontend
                recipe_dict = {
                    "name": baml_recipe.name,
                    "ingredients": [
                        f"{ing.quantity} {ing.unit} {ing.name}"
                        for ing in baml_recipe.ingredients
                    ],
                    "instructions": baml_recipe.instructions,
                    "active_time": baml_recipe.active_time_minutes,
                    "passive_time": baml_recipe.passive_time_minutes,
                    "servings": baml_recipe.servings,
                    "notes": baml_recipe.notes
                }

                recipes_generated.append(recipe_dict)

                # Stream immediately as SSE
                data = json.dumps({
                    "index": i,
                    "total": num_recipes,
                    "recipe": recipe_dict
                })
                yield f"data: {data}\n\n"

            # Send completion event
            yield f"data: {json.dumps({'complete': True})}\n\n"

        except Exception as e:
            # Send error event
            error_data = json.dumps({
                "error": True,
                "message": str(e)
            })
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        stream_recipes(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/claim-ingredients/{recipe_id}")
async def claim_ingredients(recipe_id: str):
    """
    Test ingredient claiming logic
    Is it complex or just decrement?
    """
    # TODO: Implement claiming logic
    # For now, just return success
    return {
        "success": True,
        "claimed": ["2 lbs carrots", "1 bunch kale"],
        "missing": ["olive oil"],
        "substitutions": []
    }

@app.get("/meal-plans/current")
async def get_current_meal_plan():
    """Get or create current week's meal plan"""
    with Session(engine) as session:
        # TODO: Implement meal plan logic
        return {
            "week_of": datetime.now().isoformat(),
            "recipes": [],
            "status": "draft"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)