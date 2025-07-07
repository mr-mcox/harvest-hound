from typing import List, Optional
from uuid import UUID

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.event_store import EventStore
from app.infrastructure.repositories import IngredientRepository, StoreRepository
from app.infrastructure.view_stores import InventoryItemViewStore, StoreViewStore
from app.projections.handlers import InventoryProjectionHandler, StoreProjectionHandler
from app.projections.registry import ProjectionRegistry
from app.services.store_service import StoreService

app = FastAPI(title="Harvest Hound API", version="0.1.0")

# Add CORS middleware to allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class CreateStoreRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    infinite_supply: Optional[bool] = False


class CreateStoreResponse(BaseModel):
    store_id: UUID
    name: str
    description: str
    infinite_supply: bool


class StoreListItem(BaseModel):
    store_id: UUID
    name: str
    description: str
    item_count: int


class InventoryUploadRequest(BaseModel):
    inventory_text: str


class InventoryUploadResponse(BaseModel):
    items_added: int
    errors: List[str]
    success: bool


class InventoryItem(BaseModel):
    store_id: str
    ingredient_id: str
    ingredient_name: str
    store_name: str
    quantity: float
    unit: str
    notes: Optional[str]
    added_at: str


# Database setup for view stores
# Use temporary database for tests, persistent for production
import os
import tempfile

if os.getenv("PYTEST_CURRENT_TEST"):
    # For tests, use a temporary file that gets cleaned up
    temp_dir = tempfile.mkdtemp()
    DATABASE_URL = f"sqlite:///{temp_dir}/test_view_store.db"
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///view_store.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

# Dependency injection setup
session = SessionLocal()
store_view_store = StoreViewStore(session)
inventory_item_view_store = InventoryItemViewStore(session)

# Event store with projection registry  
event_store = EventStore(session=session, projection_registry=None)  # Will add later
store_repository = StoreRepository(event_store)
ingredient_repository = IngredientRepository(event_store)

# Set up projection registry and handlers
projection_registry = ProjectionRegistry()
store_projection_handler = StoreProjectionHandler(store_view_store)
inventory_projection_handler = InventoryProjectionHandler(
    ingredient_repository, 
    store_repository,
    inventory_item_view_store
)

# Import event types for registration
from app.events.domain_events import StoreCreated, InventoryItemAdded, IngredientCreated

# Register specific event handlers
projection_registry.register(StoreCreated, store_projection_handler.handle_store_created)
projection_registry.register(InventoryItemAdded, store_projection_handler.handle_inventory_item_added)
projection_registry.register(InventoryItemAdded, inventory_projection_handler.handle_inventory_item_added)
projection_registry.register(IngredientCreated, inventory_projection_handler.handle_ingredient_created)

# Update event store with projection registry
event_store.projection_registry = projection_registry

# Import the fixture-based mock parser for comprehensive testing
from tests.mocks.llm_service import MockLLMInventoryParser

# Use fixture-based mock parser for comprehensive testing scenarios
inventory_parser = MockLLMInventoryParser()
store_service = StoreService(
    store_repository, 
    ingredient_repository, 
    inventory_parser,
    store_view_store,
    inventory_item_view_store
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for Docker containers."""
    return {"status": "healthy", "service": "harvest-hound-backend"}


@app.post("/stores", response_model=CreateStoreResponse, status_code=201)
async def create_store(request: CreateStoreRequest) -> CreateStoreResponse:
    """Create a new inventory store."""
    store_id = store_service.create_store(
        name=request.name,
        description=request.description or "",
        infinite_supply=request.infinite_supply or False,
    )

    return CreateStoreResponse(
        store_id=store_id,
        name=request.name,
        description=request.description or "",
        infinite_supply=request.infinite_supply or False,
    )


@app.get("/stores", response_model=List[StoreListItem])
async def get_stores() -> List[StoreListItem]:
    """Get list of all stores."""
    stores_data = store_service.get_all_stores()
    return [
        StoreListItem(
            store_id=UUID(store["store_id"]),
            name=store["name"],
            description=store["description"],
            item_count=store["item_count"],
        )
        for store in stores_data
    ]


@app.post(
    "/stores/{store_id}/inventory",
    response_model=InventoryUploadResponse,
    status_code=201,
)
async def upload_inventory(
    store_id: UUID, request: InventoryUploadRequest
) -> InventoryUploadResponse:
    """Upload inventory to a store."""
    try:
        result = store_service.upload_inventory(store_id, request.inventory_text)

        # If the service returned an error result, return 400 Bad Request
        if not result.success:
            response = InventoryUploadResponse(
                items_added=result.items_added,
                errors=result.errors,
                success=result.success,
            )
            raise HTTPException(status_code=400, detail=response.model_dump())

        return InventoryUploadResponse(
            items_added=result.items_added, errors=result.errors, success=result.success
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Store not found or other unexpected errors
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/stores/{store_id}/inventory", response_model=List[InventoryItem])
async def get_store_inventory(store_id: UUID) -> List[InventoryItem]:
    """Get current inventory for a store."""
    try:
        inventory = store_service.get_store_inventory(store_id)
        return [
            InventoryItem(
                store_id=item["store_id"],
                ingredient_id=item["ingredient_id"],
                ingredient_name=item["ingredient_name"],
                store_name=item["store_name"],
                quantity=item["quantity"],
                unit=item["unit"],
                notes=item["notes"],
                added_at=item["added_at"].isoformat(),
            )
            for item in inventory
        ]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


def main() -> None:
    """Run the FastAPI server."""
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
