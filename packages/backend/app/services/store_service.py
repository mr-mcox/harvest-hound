from dataclasses import dataclass
from typing import List
from uuid import UUID, uuid4

from ..infrastructure.baml_client import b
from ..infrastructure.repositories import IngredientRepository, StoreRepository
from ..infrastructure.translation import InventoryTranslator
from ..models.ingredient import Ingredient
from ..models.inventory_store import InventoryStore
from ..models.parsed_inventory import ParsedInventoryItem


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
    ):
        self.store_repository = store_repository
        self.ingredient_repository = ingredient_repository
        self.translator = InventoryTranslator()

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

        except Exception as e:
            return InventoryUploadResult.error_result([str(e)])

    def get_store_inventory(self, store_id: UUID) -> List[dict]:
        """Get current inventory for a store with ingredient names."""
        store = self.store_repository.load(store_id)

        inventory_with_names = []
        for item in store.inventory_items:
            # Load ingredient to get name
            ingredient = self.ingredient_repository.load(item.ingredient_id)

            inventory_with_names.append(
                {
                    "ingredient_name": ingredient.name,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "notes": item.notes,
                    "added_at": item.added_at,
                }
            )

        return inventory_with_names

    def _parse_inventory_text(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Parse inventory text using LLM."""
        if not inventory_text.strip():
            return []

        # Use BAML client to parse the text
        baml_ingredients = b.ExtractIngredients(inventory_text)

        # Convert BAML result to domain objects
        return [
            self.translator.to_parsed_inventory_item(ingredient)
            for ingredient in baml_ingredients
        ]

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
