import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from ..events.domain_events import StoreCreatedWithInventory
from ..infrastructure.event_publisher import EventPublisher
from ..infrastructure.event_store import EventStore
from ..infrastructure.repositories import AggregateNotFoundError
from ..interfaces.parser import InventoryParserProtocol
from ..interfaces.repository import (
    IngredientRepositoryProtocol,
    StoreRepositoryProtocol,
)
from ..interfaces.view_store import (
    InventoryItemViewStoreProtocol,
    StoreViewStoreProtocol,
)
from ..models.ingredient import Ingredient
from ..models.inventory_store import InventoryStore
from ..models.parsed_inventory import ParsedInventoryItem

logger = logging.getLogger(__name__)


@dataclass
class InventoryUploadResult:
    """Result of uploading inventory to a store."""

    items_added: int
    errors: List[str]
    success: bool
    parsing_notes: Optional[str] = None

    @classmethod
    def success_result(cls, items_added: int, parsing_notes: Optional[str] = None) -> "InventoryUploadResult":
        """Create a successful result."""
        return cls(items_added=items_added, errors=[], success=True, parsing_notes=parsing_notes)

    @classmethod
    def error_result(cls, errors: List[str], parsing_notes: Optional[str] = None) -> "InventoryUploadResult":
        """Create an error result."""
        return cls(items_added=0, errors=errors, success=False, parsing_notes=parsing_notes)


@dataclass
class UnifiedCreationResult:
    """Result of unified store creation with inventory processing."""
    
    store_id: UUID
    successful_items: int
    error_message: Optional[str] = None


class StoreService:
    """Application service for inventory store operations."""

    def __init__(
        self,
        store_repository: StoreRepositoryProtocol,
        ingredient_repository: IngredientRepositoryProtocol,
        inventory_parser: InventoryParserProtocol,
        store_view_store: StoreViewStoreProtocol,
        inventory_item_view_store: InventoryItemViewStoreProtocol,
        event_store: Optional[EventStore] = None,
        event_publisher: Optional[EventPublisher] = None,
    ):
        self.store_repository = store_repository
        self.ingredient_repository = ingredient_repository
        self.inventory_parser = inventory_parser
        self.store_view_store = store_view_store
        self.inventory_item_view_store = inventory_item_view_store
        self.event_store = event_store
        self.event_publisher = event_publisher


    def create_store_with_inventory(
        self,
        name: str,
        description: str,
        infinite_supply: bool,
        inventory_text: Optional[str],
    ) -> UnifiedCreationResult:
        """Create store and optionally process inventory in unified operation."""
        # Step 1: Create store directly (inlined from old create_store method)
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
        
        successful_items = 0
        error_message = None
        
        # Step 2: Conditionally process inventory if provided
        if inventory_text is not None:
            try:
                # Process inventory using existing upload_inventory method
                result = self.upload_inventory(store_id, inventory_text)
                if result.success:
                    successful_items = result.items_added
                    # Include parsing notes in error message even for successful scenarios
                    if result.parsing_notes:
                        error_message = result.parsing_notes
                else:
                    # Simple error message aggregation for failures
                    error_message = f"Inventory processing failed: {'; '.join(result.errors)}"
            except Exception as e:
                # Capture any processing failures with simple error message
                error_message = f"Inventory processing error: {str(e)}"
        
        # Step 3: Create and persist StoreCreatedWithInventory event
        unified_event = StoreCreatedWithInventory(
            store_id=store_id,
            successful_items=successful_items,
            error_message=error_message,
        )
        
        # Persist event in event store if available
        if self.event_store:
            self.event_store.append_event(f"unified-creation-{store_id}", unified_event)
        
        # Publish event via event bus if available
        if self.event_publisher:
            self.event_publisher.publish_sync(unified_event)
        
        return UnifiedCreationResult(
            store_id=store_id,
            successful_items=successful_items,
            error_message=error_message,
        )

    def upload_inventory(
        self,
        store_id: UUID,
        inventory_text: str,
    ) -> InventoryUploadResult:
        """Upload inventory items to a store by parsing text input."""
        try:
            # Load the store
            store = self.store_repository.load(store_id)

            # Parse the inventory text using LLM (with notes)
            parsing_notes = None  # Initialize outside try block
            try:
                parsing_result = self.inventory_parser.parse_inventory_with_notes(inventory_text)
                parsed_items = parsing_result.items
                parsing_notes = parsing_result.parsing_notes
                
                logger.info(
                    "LLM parsing succeeded for store %s. Found %d items: %s",
                    store_id,
                    len(parsed_items),
                    [f"{item.name} ({item.quantity} {item.unit})" for item in parsed_items]
                )
            except Exception as parsing_error:
                # Log LLM parsing errors for debugging prompt improvements
                truncated_input = (
                    inventory_text[:100] + "..." 
                    if len(inventory_text) > 100 
                    else inventory_text
                )
                logger.warning(
                    "LLM parsing failed for store %s. Input: %r. Error: %s",
                    store_id,
                    truncated_input,
                    str(parsing_error)
                )
                return InventoryUploadResult.error_result([
                    f"Failed to parse inventory text: {str(parsing_error)}"
                ])

            items_added = 0
            processing_errors = []

            # Process each parsed item (continue processing even if some fail)
            for i, parsed_item in enumerate(parsed_items):
                try:
                    logger.info(
                        "Processing item %d/%d: %s (%s %s)",
                        i + 1,
                        len(parsed_items),
                        parsed_item.name,
                        parsed_item.quantity,
                        parsed_item.unit
                    )
                    
                    # Create or get ingredient
                    ingredient_id = self._create_or_get_ingredient(
                        parsed_item.name,
                        parsed_item.unit,
                    )
                    logger.info("Created/found ingredient with ID: %s", ingredient_id)

                    # Add inventory item to store
                    store, events = store.add_inventory_item(
                        ingredient_id=ingredient_id,
                        quantity=parsed_item.quantity,
                        unit=parsed_item.unit,
                    )
                    logger.info("Generated %d events for item", len(events))

                    # Persist the events
                    self.store_repository.save(store, events)
                    items_added += 1
                    logger.info("Successfully added item %d: %s", items_added, parsed_item.name)

                except ValueError as validation_error:
                    # Handle validation errors for individual items - continue processing others
                    error_msg = f"Invalid item '{parsed_item.name}': {str(validation_error)}"
                    processing_errors.append(error_msg)
                    logger.info(
                        "Validation error for item '%s' in store %s: %s - continuing with remaining items",
                        parsed_item.name,
                        store_id,
                        str(validation_error)
                    )
                except Exception as item_error:
                    # Handle any other errors for individual items - continue processing others
                    error_msg = f"Failed to process item '{parsed_item.name}': {str(item_error)}"
                    processing_errors.append(error_msg)
                    logger.info(
                        "Processing error for item '%s' in store %s: %s - continuing with remaining items",
                        parsed_item.name,
                        store_id,
                        str(item_error)
                    )

            # Determine success - partial success is still success if any items were added
            success = items_added > 0 or len(processing_errors) == 0
            
            return InventoryUploadResult(
                items_added=items_added,
                errors=processing_errors,
                success=success,
                parsing_notes=parsing_notes
            )

        except AggregateNotFoundError:
            # Re-raise store not found errors so API can return 404
            raise
        except Exception as e:
            # Log unexpected errors for debugging
            logger.error(
                "Unexpected error uploading inventory to store %s: %s",
                store_id,
                str(e),
                exc_info=True
            )
            return InventoryUploadResult.error_result([f"System error: {str(e)}"])

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
        """Get current inventory for a store with denormalized view data."""
        inventory_views = self.inventory_item_view_store.get_all_for_store(store_id)
        
        return [
            {
                "store_id": str(view.store_id),
                "ingredient_id": str(view.ingredient_id),
                "ingredient_name": view.ingredient_name,
                "store_name": view.store_name,
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
