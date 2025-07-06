"""
Projection handlers for updating read models in response to domain events.

These handlers implement the event-driven denormalization strategy from ADR-005,
maintaining read models optimized for UI consumption.
"""
from typing import List, Protocol
from uuid import UUID

from ..events.domain_events import InventoryItemAdded, StoreCreated, IngredientCreated
from ..models import Ingredient, InventoryStore
from ..models.read_models import InventoryItemView, StoreView


class IngredientRepository(Protocol):
    """Protocol for ingredient repository dependency."""
    
    def get_by_id(self, ingredient_id: UUID) -> Ingredient | None:
        """Get ingredient by ID."""
        ...


class StoreRepository(Protocol):
    """Protocol for store repository dependency."""
    
    def get_by_id(self, store_id: UUID) -> InventoryStore | None:
        """Get store by ID."""
        ...


class InventoryItemViewStore(Protocol):
    """Protocol for inventory item view store dependency."""
    
    def save_inventory_item_view(self, view: InventoryItemView) -> None:
        """Save inventory item view."""
        ...
    
    def get_by_ingredient_id(self, ingredient_id: UUID) -> List[InventoryItemView]:
        """Get all inventory item views for an ingredient."""
        ...


class StoreViewStore(Protocol):
    """Protocol for store view store dependency."""
    
    def save_store_view(self, view: StoreView) -> None:
        """Save store view."""
        ...
    
    def get_by_store_id(self, store_id: UUID) -> StoreView | None:
        """Get store view by ID."""
        ...


class InventoryProjectionHandler:
    """
    Handles projection events for inventory read models.
    
    Updates denormalized inventory views when domain events occur.
    """
    
    def __init__(
        self,
        ingredient_repo: IngredientRepository,
        store_repo: StoreRepository,
        view_store: InventoryItemViewStore,
    ):
        self.ingredient_repo = ingredient_repo
        self.store_repo = store_repo
        self.view_store = view_store
    
    def handle_inventory_item_added(self, event: InventoryItemAdded) -> None:
        """Create InventoryItemView when inventory item is added."""
        # Fetch related data for denormalization
        ingredient = self.ingredient_repo.get_by_id(event.ingredient_id)
        store = self.store_repo.get_by_id(event.store_id)
        
        if not ingredient or not store:
            # Log error in real implementation
            return
        
        # Create flat view model with denormalized fields
        view = InventoryItemView(
            store_id=event.store_id,
            ingredient_id=event.ingredient_id,
            ingredient_name=ingredient.name,  # Denormalized
            store_name=store.name,            # Denormalized
            quantity=event.quantity,
            unit=event.unit,
            notes=event.notes,
            added_at=event.added_at
        )
        
        self.view_store.save_inventory_item_view(view)
    
    def handle_ingredient_created(self, event: IngredientCreated) -> None:
        """Update all inventory views when ingredient name is updated."""
        # Update all inventory views for this ingredient
        views = self.view_store.get_by_ingredient_id(event.ingredient_id)
        for view in views:
            updated_view = view.model_copy(update={"ingredient_name": event.name})
            self.view_store.save_inventory_item_view(updated_view)


class StoreProjectionHandler:
    """
    Handles projection events for store read models.
    
    Updates denormalized store views when domain events occur.
    """
    
    def __init__(self, view_store: StoreViewStore):
        self.view_store = view_store
    
    def handle_store_created(self, event: StoreCreated) -> None:
        """Create StoreView when store is created."""
        view = StoreView(
            store_id=event.store_id,
            name=event.name,
            description=event.description,
            infinite_supply=event.infinite_supply,
            item_count=0,  # New store starts with 0 items
            created_at=event.created_at,
        )
        
        self.view_store.save_store_view(view)
    
    def handle_inventory_item_added(self, event: InventoryItemAdded) -> None:
        """Increment item count when inventory item is added to store."""
        existing_view = self.view_store.get_by_store_id(event.store_id)
        if existing_view:
            updated_view = existing_view.model_copy(
                update={"item_count": existing_view.item_count + 1}
            )
            self.view_store.save_store_view(updated_view)