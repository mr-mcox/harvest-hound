"""Store creation orchestrator service for unified store and inventory creation."""

import asyncio
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from ..events.domain_events import StoreCreatedWithInventory
from ..infrastructure.event_publisher import EventPublisher
from ..infrastructure.event_store import EventStore
from ..interfaces.parser import InventoryParserProtocol
from ..interfaces.service import StoreServiceProtocol


@dataclass
class OrchestrationResult:
    """Result of unified store creation with inventory processing."""
    
    store_id: UUID
    successful_items: int
    error_message: Optional[str] = None


class StoreCreationOrchestrator:
    """Application service for unified store creation with optional inventory processing."""
    
    def __init__(
        self,
        store_service: StoreServiceProtocol,
        inventory_parser: InventoryParserProtocol,
        event_store: EventStore,
        event_publisher: EventPublisher,
    ):
        """Initialize orchestrator with required dependencies.
        
        Args:
            store_service: Service for store operations
            inventory_parser: Parser for inventory text processing
            event_store: Event store for persisting orchestration events
            event_publisher: Event publisher for broadcasting events
        """
        self.store_service = store_service
        self.inventory_parser = inventory_parser
        self.event_store = event_store
        self.event_publisher = event_publisher
    
    def create_store_with_inventory(
        self,
        name: str,
        description: str,
        infinite_supply: bool,
        inventory_text: Optional[str],
    ) -> OrchestrationResult:
        """Create store and optionally process inventory in unified operation.
        
        Args:
            name: Store name
            description: Store description
            infinite_supply: Whether store has infinite supply
            inventory_text: Optional inventory text to process
            
        Returns:
            Orchestration result with store_id, successful_items, and error_message
        """
        # Step 1: Create store using existing StoreService
        store_id = self.store_service.create_store(
            name=name,
            description=description,
            infinite_supply=infinite_supply,
        )
        
        successful_items = 0
        error_message = None
        
        # Step 2: Conditionally process inventory if provided
        if inventory_text is not None:
            try:
                # Parse inventory with enhanced parsing that reports partial success
                parsing_result = self.inventory_parser.parse_inventory_with_notes(inventory_text)
                
                if parsing_result.successful_items:
                    # Process successfully parsed items using existing StoreService
                    result = self.store_service.upload_inventory(store_id, inventory_text)
                    if result.success:
                        successful_items = result.items_added
                        # Include parsing notes as error message if some items failed to parse
                        error_message = parsing_result.parsing_notes
                    else:
                        # StoreService processing failed even with parsed items
                        error_message = f"Processing failed: {'; '.join(result.errors)}"
                        if parsing_result.parsing_notes:
                            error_message += f". Parsing notes: {parsing_result.parsing_notes}"
                else:
                    # No items could be parsed successfully
                    error_message = parsing_result.parsing_notes or "No items could be parsed from inventory text"
                    
            except Exception as e:
                # Capture any processing failures with simple error message
                error_message = f"Inventory processing error: {str(e)}"
        
        # Step 3: Create and persist StoreCreatedWithInventory event
        orchestration_event = StoreCreatedWithInventory(
            store_id=store_id,
            successful_items=successful_items,
            error_message=error_message,
        )
        
        # Persist event in event store with orchestration stream
        self.event_store.append_event(f"orchestration-{store_id}", orchestration_event)
        
        # Publish event via event bus
        try:
            # Run async publish in sync context
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.event_publisher.publish_async(orchestration_event))
        except RuntimeError:
            # No event loop running, create one
            asyncio.run(self.event_publisher.publish_async(orchestration_event))
        except Exception:
            # If event publishing fails, don't fail the operation
            pass
        
        return OrchestrationResult(
            store_id=store_id,
            successful_items=successful_items,
            error_message=error_message,
        )