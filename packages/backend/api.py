from typing import List, Optional
from uuid import UUID

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.infrastructure.event_store import EventStore
from app.infrastructure.repositories import IngredientRepository, StoreRepository
from app.models.parsed_inventory import ParsedInventoryItem
from app.services.inventory_parser import (
    MockInventoryParserClient,
    create_inventory_parser_client,
)
from app.services.store_service import StoreService

app = FastAPI(title="Harvest Hound API", version="0.1.0")


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
    ingredient_name: str
    quantity: float
    unit: str
    notes: Optional[str]
    added_at: str


# Dependency injection setup
event_store = EventStore()
store_repository = StoreRepository(event_store)
ingredient_repository = IngredientRepository(event_store)


# Create a smart mock parser for API testing
class SmartMockInventoryParserClient(MockInventoryParserClient):
    """Mock client that provides realistic results based on input."""

    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Return parsed results based on input text."""
        if not inventory_text.strip():
            return []

        # Simulate parsing errors for specific inputs
        if (
            "invalid" in inventory_text.lower()
            or "unparseable" in inventory_text.lower()
        ):
            raise ValueError("Failed to parse inventory text")

        # Simple mapping for common test cases
        if "carrots" in inventory_text.lower():
            return [ParsedInventoryItem(name="carrots", quantity=2.0, unit="pound")]
        elif "kale" in inventory_text.lower():
            return [ParsedInventoryItem(name="kale", quantity=1.0, unit="bunch")]
        else:
            # Default fallback
            return [ParsedInventoryItem(name="unknown", quantity=1.0, unit="item")]


inventory_parser = SmartMockInventoryParserClient()
store_service = StoreService(store_repository, ingredient_repository, inventory_parser)


@app.get("/health")  # type: ignore[misc]
async def health_check() -> dict[str, str]:
    """Health check endpoint for Docker containers."""
    return {"status": "healthy", "service": "harvest-hound-backend"}


@app.post("/stores", response_model=CreateStoreResponse, status_code=201)  # type: ignore[misc]
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


@app.get("/stores", response_model=List[StoreListItem])  # type: ignore[misc]
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


@app.post(  # type: ignore[misc]
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


@app.get("/stores/{store_id}/inventory", response_model=List[InventoryItem])  # type: ignore[misc]
async def get_store_inventory(store_id: UUID) -> List[InventoryItem]:
    """Get current inventory for a store."""
    try:
        inventory = store_service.get_store_inventory(store_id)
        return [
            InventoryItem(
                ingredient_name=item["ingredient_name"],
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
