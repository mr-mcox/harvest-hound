from typing import Annotated, List, Optional
from uuid import UUID

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.dependencies import (
    SessionLocal,
    create_projection_registry,
    engine,
    get_store_service,
    setup_event_bus_subscribers,
)
from app.infrastructure.database import metadata
from app.infrastructure.event_bus import EventBusManager, InMemoryEventBus
from app.infrastructure.event_publisher import EventPublisher
from app.infrastructure.event_store import EventStore
from app.infrastructure.repositories import (
    IngredientRepository,
    StoreRepository,
)
from app.infrastructure.view_stores import (
    InventoryItemViewStore,
    StoreViewStore,
)
from app.interfaces.service import StoreServiceProtocol

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


# Module-level dependency setup for startup
_startup_completed = False


@app.on_event("startup")
async def startup_event() -> None:
    """Set up event bus and projection registry during app startup."""
    global _startup_completed
    if not _startup_completed:
        # Initialize event bus manager
        app.state.event_bus_manager = EventBusManager(InMemoryEventBus())
        
        # Create tables if they don't exist
        metadata.create_all(bind=engine)
        
        # Create session and dependencies
        session = SessionLocal()
        try:
            # Create dependencies manually for startup
            store_view_store = StoreViewStore(session)
            inventory_item_view_store = InventoryItemViewStore(session)
            
            # Create event store and publisher for repositories
            event_store = EventStore(session=session)
            event_publisher = EventPublisher(app.state.event_bus_manager.event_bus)
            store_repository = StoreRepository(event_store, event_publisher)
            ingredient_repository = IngredientRepository(event_store, event_publisher)
            
            # Create and store projection registry in app state
            app.state.projection_registry = create_projection_registry(
                store_view_store,
                inventory_item_view_store,
                store_repository,
                ingredient_repository
            )
            
            # Subscribe projection handlers to event bus
            await setup_event_bus_subscribers(
                app.state.event_bus_manager,
                store_view_store,
                inventory_item_view_store,
                store_repository,
                ingredient_repository
            )
            
            session.commit()
        finally:
            session.close()
        
        _startup_completed = True


# Import the get_db_session for startup

# All tests now use proper dependency injection


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for Docker containers."""
    return {"status": "healthy", "service": "harvest-hound-backend"}


@app.post("/stores", response_model=CreateStoreResponse, status_code=201)
async def create_store(
    request: CreateStoreRequest,
    store_service: Annotated[StoreServiceProtocol, Depends(get_store_service)]
) -> CreateStoreResponse:
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
async def get_stores(
    store_service: Annotated[StoreServiceProtocol, Depends(get_store_service)]
) -> List[StoreListItem]:
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
    store_id: UUID,
    request: InventoryUploadRequest,
    store_service: Annotated[StoreServiceProtocol, Depends(get_store_service)]
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
async def get_store_inventory(
    store_id: UUID,
    store_service: Annotated[StoreServiceProtocol, Depends(get_store_service)]
) -> List[InventoryItem]:
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
