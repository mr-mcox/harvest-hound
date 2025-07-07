from dataclasses import dataclass
from typing import Any, Dict, List
from uuid import UUID, uuid4

from ..infrastructure.repositories import (
    AggregateNotFoundError,
    IngredientRepository,
    StoreRepository,
)
from ..infrastructure.view_stores import InventoryItemViewStore, StoreViewStore
from ..models.ingredient import Ingredient
from ..models.inventory_store import InventoryStore
from ..models.parsed_inventory import ParsedInventoryItem
from .inventory_parser import InventoryParserClient


@dataclass
class InventoryUploadResult:
    """Result of uploading inventory to a store."""

    items_added: int
    errors: List[str]
    success: bool

    @classmethod
    def success_result(cls, items_added: int) -> "InventoryUploadResult":
        """Create a successful result."""
        return cls(items_added=items_added, errors=[], success=True)

    @classmethod
    def error_result(cls, errors: List[str]) -> "InventoryUploadResult":
        """Create an error result."""
        return cls(items_added=0, errors=errors, success=False)


class StoreService:
    """Application service for inventory store operations."""

    def __init__(
        self,
        store_repository: StoreRepository,
        ingredient_repository: IngredientRepository,
        inventory_parser: InventoryParserClient,
        store_view_store: StoreViewStore,
        inventory_item_view_store: InventoryItemViewStore,
    ):
        self.store_repository = store_repository
        self.ingredient_repository = ingredient_repository
        self.inventory_parser = inventory_parser
        self.store_view_store = store_view_store
        self.inventory_item_view_store = inventory_item_view_store

    def create_store(
        self,
        name: str,
        description: str = "",
        infinite_supply: bool = False,
    ) -> UUID:
        """Create a new inventory store."""
        store_id = uuid4()

        # Create store using domain model
        store, events = InventoryStore.create(
            store_id=store_id,
            name=name,
            description=description,
            infinite_supply=infinite_supply,
        )

        # Persist events through repository
        self.store_repository.save(store, events)

        return store_id

    def upload_inventory(
        self,
        store_id: UUID,
        inventory_text: str,
    ) -> InventoryUploadResult:
        """Upload inventory items to a store by parsing text input."""
        try:
            # Load the store
            store = self.store_repository.load(store_id)

            # Parse the inventory text using LLM
            parsed_items = self._parse_inventory_text(inventory_text)

            items_added = 0

            # Process each parsed item
            for parsed_item in parsed_items:
                # Create or get ingredient
                ingredient_id = self._create_or_get_ingredient(
                    parsed_item.name,
                    parsed_item.unit,
                )

                # Add inventory item to store
                store, events = store.add_inventory_item(
                    ingredient_id=ingredient_id,
                    quantity=parsed_item.quantity,
                    unit=parsed_item.unit,
                )

                # Persist the events
                self.store_repository.save(store, events)
                items_added += 1

            return InventoryUploadResult.success_result(items_added)

        except AggregateNotFoundError:
            # Re-raise store not found errors so API can return 404
            raise
        except Exception as e:
            return InventoryUploadResult.error_result([str(e)])

    def get_all_stores(self) -> List[Dict[str, Any]]:
        """Get list of all stores with item counts."""
        store_views = self.store_view_store.get_all_stores()
        
        return [
            {
                "store_id": str(view.store_id),
                "name": view.name,
                "description": view.description,
                "infinite_supply": view.infinite_supply,
                "item_count": view.item_count,
                "created_at": view.created_at,
            }
            for view in store_views
        ]

    def get_store_inventory(self, store_id: UUID) -> List[Dict[str, Any]]:
        """Get current inventory for a store with ingredient names."""
        inventory_views = self.inventory_item_view_store.get_all_for_store(store_id)
        
        return [
            {
                "ingredient_name": view.ingredient_name,
                "quantity": view.quantity,
                "unit": view.unit,
                "notes": view.notes,
                "added_at": view.added_at,
            }
            for view in inventory_views
        ]

    def _parse_inventory_text(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Parse inventory text using injected parser client."""
        return self.inventory_parser.parse_inventory(inventory_text)

    def _create_or_get_ingredient(self, name: str, default_unit: str) -> UUID:
        """Create a new ingredient or get existing one by name."""
        # For now, always create new ingredients
        # In a full implementation, we'd check for existing ingredients first
        ingredient_id = uuid4()

        ingredient, events = Ingredient.create(
            ingredient_id=ingredient_id,
            name=name,
            default_unit=default_unit,
        )

        self.ingredient_repository.save(ingredient, events)
        return ingredient_id
