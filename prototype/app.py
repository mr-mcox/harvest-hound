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
    priority: str = "medium"  # low, medium, high, urgent
    added_at: Optional[datetime] = Field(default_factory=datetime.now)

class Recipe(SQLModel, table=True):
    """Recipe storage - keep it simple"""
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    ingredients_json: str  # Just store as JSON for now
    instructions: str
    source: str = "ai_generated"
    state: str = "planned"  # planned, cooked, abandoned
    active_time: int = 0  # minutes
    passive_time: int = 0  # minutes
    servings: int = 1
    notes: str = ""
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    planned_at: Optional[datetime] = Field(default_factory=datetime.now)
    cooked_at: Optional[datetime] = None

class IngredientClaim(SQLModel, table=True):
    """Links recipe to specific ingredient with state tracking"""
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    recipe_id: UUID = Field(foreign_key="recipe.id")
    ingredient_name: str
    store_name: str
    quantity: float
    unit: str
    state: str = "reserved"  # reserved, consumed
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

def load_available_inventory() -> dict:
    """
    Load inventory and subtract reserved claims from planned recipes.
    Returns only the AVAILABLE inventory (physical minus reserved).
    Structure: {store_name: {ingredient_name: (quantity, unit)}}
    """
    # Start with physical inventory
    inventory = load_initial_inventory()

    # Get all reserved claims from planned recipes
    with Session(engine) as session:
        reserved_claims = session.exec(
            select(IngredientClaim).where(IngredientClaim.state == "reserved")
        ).all()

        # Subtract reserved quantities
        for claim in reserved_claims:
            if claim.store_name in inventory:
                if claim.ingredient_name in inventory[claim.store_name]:
                    current_qty, current_unit = inventory[claim.store_name][claim.ingredient_name]
                    # Subtract the reserved amount
                    available_qty = max(0, current_qty - claim.quantity)
                    inventory[claim.store_name][claim.ingredient_name] = (available_qty, current_unit)

    return inventory

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
                    unit=ing.unit or "unit",
                    priority=ing.priority if hasattr(ing, 'priority') and ing.priority else "medium"
                )
                session.add(item)
                added_items.append(f"{ing.quantity} {ing.unit or 'unit'} {ing.name} [{ing.priority if hasattr(ing, 'priority') else 'medium'}]")

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

class UpdatePriorityRequest(BaseModel):
    priority: str  # low, medium, high, urgent

@app.patch("/inventory/{item_id}/priority")
async def update_item_priority(item_id: str, request: UpdatePriorityRequest):
    """Update inventory item priority"""
    with Session(engine) as session:
        item = session.get(InventoryItem, UUID(item_id))
        if item:
            item.priority = request.priority
            session.commit()
            return {"success": True, "priority": item.priority}
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
    AUTO-ACCOUNTS for reserved ingredients from planned recipes
    """
    async def stream_pitches():
        try:
            # Parse inventory if provided (from in-session tracking),
            # otherwise load available inventory (physical minus reserved claims)
            current_inventory = None
            if available_inventory_json:
                try:
                    current_inventory = json.loads(available_inventory_json)
                except json.JSONDecodeError:
                    pass  # Fall back to available inventory

            # If no inventory provided, load available inventory (accounts for reserved claims)
            if current_inventory is None:
                current_inventory = load_available_inventory()

            # Load inventory split by store type, using decremented state
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
    AUTO-SAVES recipe to database and creates persistent ingredient claims
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

        # PERSIST RECIPE AND CLAIMS TO DATABASE
        with Session(engine) as session:
            # Create recipe record
            db_recipe = Recipe(
                name=baml_recipe.name,
                ingredients_json=json.dumps([
                    f"{ing.quantity} {ing.unit} {ing.name}"
                    for ing in baml_recipe.ingredients
                ]),
                instructions=baml_recipe.instructions,
                state="planned",
                active_time=baml_recipe.active_time_minutes,
                passive_time=baml_recipe.passive_time_minutes,
                servings=baml_recipe.servings,
                notes=baml_recipe.notes or ""
            )
            session.add(db_recipe)
            session.commit()
            session.refresh(db_recipe)

            recipe_id = db_recipe.id

            # Create ingredient claims for explicit ingredients
            for claimed_ing in request.explicit_ingredients:
                ing_name = claimed_ing["name"]
                ing_qty = claimed_ing["quantity"]
                ing_unit = claimed_ing["unit"]

                # Find which store this ingredient came from
                store_name = None
                for s_name, items in updated_inventory.items():
                    if ing_name in items:
                        store_name = s_name
                        current_qty, current_unit = items[ing_name]
                        # Simple subtraction (assuming units match)
                        new_qty = max(0, current_qty - ing_qty)
                        updated_inventory[s_name][ing_name] = (new_qty, current_unit)
                        break

                # Create claim record
                if store_name:
                    claim = IngredientClaim(
                        recipe_id=recipe_id,
                        ingredient_name=ing_name,
                        store_name=store_name,
                        quantity=ing_qty,
                        unit=ing_unit,
                        state="reserved"
                    )
                    session.add(claim)

            session.commit()

        recipe_dict["id"] = str(recipe_id)  # Include ID for frontend

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

@app.get("/api/inventory/available")
async def get_available_inventory():
    """Get available inventory (physical minus reserved claims)"""
    return {"inventory": load_available_inventory()}

@app.get("/api/inventory/flat")
async def get_flat_inventory():
    """Get all inventory items in a flat list with priority"""
    with Session(engine) as session:
        # Get all stores and their inventory
        stores = session.exec(select(Store)).all()
        store_dict = {str(s.id): s.name for s in stores}

        # Get all inventory items
        items = session.exec(select(InventoryItem)).all()

        # Get reserved claims to calculate available quantities
        reserved_claims = session.exec(
            select(IngredientClaim).where(IngredientClaim.state == "reserved")
        ).all()

        # Build claims lookup: {store_name: {ingredient_name: total_reserved_qty}}
        claims_by_store = {}
        for claim in reserved_claims:
            if claim.store_name not in claims_by_store:
                claims_by_store[claim.store_name] = {}
            if claim.ingredient_name not in claims_by_store[claim.store_name]:
                claims_by_store[claim.store_name][claim.ingredient_name] = 0
            claims_by_store[claim.store_name][claim.ingredient_name] += claim.quantity

        # Build flat list with available quantities
        flat_items = []
        for item in items:
            store_name = store_dict.get(str(item.store_id), "Unknown")

            # Calculate available quantity
            reserved = 0
            if store_name in claims_by_store and item.ingredient_name in claims_by_store[store_name]:
                reserved = claims_by_store[store_name][item.ingredient_name]

            available_qty = max(0, item.quantity - reserved)

            flat_items.append({
                "id": str(item.id),
                "ingredient_name": item.ingredient_name,
                "quantity": item.quantity,
                "available_quantity": available_qty,
                "reserved_quantity": reserved,
                "unit": item.unit,
                "priority": item.priority,
                "store_name": store_name,
                "store_id": str(item.store_id)
            })

        # Sort by priority (urgent > high > medium > low), then by ingredient name
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        flat_items.sort(key=lambda x: (priority_order.get(x["priority"], 2), x["ingredient_name"]))

        return {"items": flat_items}

@app.get("/api/recipes/planned")
async def get_planned_recipes():
    """Get all planned recipes with their ingredient claims"""
    with Session(engine) as session:
        # Get all planned recipes
        recipes = session.exec(
            select(Recipe).where(Recipe.state == "planned")
        ).all()

        result = []
        for recipe in recipes:
            # Get claims for this recipe
            claims = session.exec(
                select(IngredientClaim).where(IngredientClaim.recipe_id == recipe.id)
            ).all()

            result.append({
                "id": str(recipe.id),
                "name": recipe.name,
                "ingredients": json.loads(recipe.ingredients_json),
                "instructions": recipe.instructions,
                "active_time": recipe.active_time,
                "passive_time": recipe.passive_time,
                "servings": recipe.servings,
                "notes": recipe.notes,
                "planned_at": recipe.planned_at.isoformat() if recipe.planned_at else None,
                "claims": [
                    {
                        "ingredient": c.ingredient_name,
                        "quantity": c.quantity,
                        "unit": c.unit,
                        "store": c.store_name
                    }
                    for c in claims
                ]
            })

        return {"recipes": result}

@app.post("/api/recipes/{recipe_id}/cook")
async def cook_recipe(recipe_id: str):
    """
    Mark recipe as cooked - consume ingredient claims and decrement inventory
    """
    with Session(engine) as session:
        # Get recipe
        recipe = session.get(Recipe, UUID(recipe_id))
        if not recipe:
            return {"success": False, "error": "Recipe not found"}

        # Get all claims for this recipe
        claims = session.exec(
            select(IngredientClaim).where(
                IngredientClaim.recipe_id == UUID(recipe_id),
                IngredientClaim.state == "reserved"
            )
        ).all()

        # Decrement inventory for each claim
        for claim in claims:
            # Find the inventory item
            with Session(engine) as inv_session:
                store = inv_session.exec(
                    select(Store).where(Store.name == claim.store_name)
                ).first()

                if store:
                    inv_item = inv_session.exec(
                        select(InventoryItem).where(
                            InventoryItem.store_id == store.id,
                            InventoryItem.ingredient_name == claim.ingredient_name
                        )
                    ).first()

                    if inv_item:
                        # Decrement quantity
                        inv_item.quantity = max(0, inv_item.quantity - claim.quantity)
                        inv_session.commit()

            # Mark claim as consumed
            claim.state = "consumed"

        # Update recipe state
        recipe.state = "cooked"
        recipe.cooked_at = datetime.now()

        session.commit()

        return {"success": True, "message": f"Cooked {recipe.name}!"}

@app.post("/api/recipes/{recipe_id}/abandon")
async def abandon_recipe(recipe_id: str):
    """
    Abandon recipe - release ingredient claims without consuming
    """
    with Session(engine) as session:
        # Get recipe
        recipe = session.get(Recipe, UUID(recipe_id))
        if not recipe:
            return {"success": False, "error": "Recipe not found"}

        # Get all claims for this recipe
        claims = session.exec(
            select(IngredientClaim).where(
                IngredientClaim.recipe_id == UUID(recipe_id),
                IngredientClaim.state == "reserved"
            )
        ).all()

        # Delete claims (they're released, not consumed)
        for claim in claims:
            session.delete(claim)

        # Update recipe state
        recipe.state = "abandoned"

        session.commit()

        return {"success": True, "message": f"Abandoned {recipe.name}"}

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