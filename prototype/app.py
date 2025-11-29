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
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    store_id: UUID = Field(foreign_key="store.id")
    ingredient_name: str
    quantity: float
    unit: str
    notes: str = ""
    added_at: datetime = Field(default_factory=datetime.now)

class Recipe(SQLModel, table=True):
    """Recipe storage - keep it simple"""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    ingredients_json: str  # Just store as JSON for now
    instructions: str
    source: str = "ai_generated"
    created_at: datetime = Field(default_factory=datetime.now)

class MealPlan(SQLModel, table=True):
    """Weekly meal planning"""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    week_of: datetime
    recipes_json: str  # List of recipe IDs as JSON
    status: str = "draft"  # draft, accepted, completed
    created_at: datetime = Field(default_factory=datetime.now)

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

class GenerateRecipesRequest(BaseModel):
    csa_contents: str
    num_recipes: int = 3

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
                "description": s.description
            }
            for s in stores
        ]

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

@app.post("/generate-recipes")
async def generate_recipes(request: GenerateRecipesRequest):
    """
    Generate recipes using BAML - with SSE streaming
    This is where we'll test streaming value
    """
    async def stream_recipes():
        # TODO: Integrate BAML here
        # For now, mock streaming response
        recipes = [
            {
                "name": "Roasted Root Vegetables",
                "ingredients": ["carrots", "beets", "potatoes"],
                "instructions": "1. Chop vegetables\n2. Toss with oil\n3. Roast at 425°F"
            },
            {
                "name": "Kale Caesar Salad",
                "ingredients": ["kale", "parmesan", "croutons"],
                "instructions": "1. Massage kale\n2. Add dressing\n3. Top with cheese"
            },
            {
                "name": "Carrot Ginger Soup",
                "ingredients": ["carrots", "ginger", "onion"],
                "instructions": "1. Sauté aromatics\n2. Add carrots\n3. Simmer and blend"
            }
        ]
        
        for i, recipe in enumerate(recipes):
            # Simulate streaming delay
            await asyncio.sleep(0.5)
            
            # Send as SSE format
            data = json.dumps({
                "index": i,
                "total": len(recipes),
                "recipe": recipe
            })
            yield f"data: {data}\n\n"
        
        # Send completion event
        yield f"data: {json.dumps({'complete': True})}\n\n"
    
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