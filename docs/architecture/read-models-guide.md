# Read Models Implementation Guide

## Overview

This guide explains how read models work in the Harvest Hound application and how to extend them for new features.

## Architecture

Read models implement the **CQRS (Command Query Responsibility Segregation)** pattern:

- **Commands** modify domain aggregates and emit events
- **Queries** read from optimized denormalized views
- **Projections** keep read models up-to-date with domain changes

## Key Components

### 1. Read Model Classes (`app/models/read_models.py`)

Define the structure of denormalized views:

```python
@dataclass
class InventoryItemView:
    store_id: str
    ingredient_id: str
    ingredient_name: str    # Denormalized from ingredient
    store_name: str         # Denormalized from store
    quantity: float
    unit: str
    notes: Optional[str]
    added_at: datetime
```

### 2. View Stores (`app/infrastructure/view_stores.py`)

Handle database operations for read models:

```python
class InventoryItemViewStore:
    def create_table(self) -> None:
        # Create table with proper indexes
        
    def insert_item(self, item: InventoryItemView) -> None:
        # Insert denormalized data
        
    def get_by_store_id(self, store_id: UUID) -> List[InventoryItemView]:
        # Query optimized for UI needs
```

### 3. Projection Handlers (`app/projections/handlers.py`)

React to domain events and update read models:

```python
class InventoryProjectionHandler:
    def handle_inventory_item_added(self, event: InventoryItemAdded):
        # 1. Load ingredient to get name
        # 2. Load store to get name  
        # 3. Create denormalized view record
        # 4. Insert into view store
```

### 4. Projection Registry (`app/projections/registry.py`)

Coordinates event handling:

```python
# Register handlers for specific events
projection_registry.register(InventoryItemAdded, handler.handle_inventory_item_added)
```

## Adding New Read Models

### Step 1: Define Read Model

Create data class in `app/models/read_models.py`:

```python
@dataclass
class RecipeView:
    recipe_id: str
    title: str
    ingredient_count: int  # Computed field
    estimated_time: str
    created_at: datetime
```

### Step 2: Create View Store

Add database operations in `app/infrastructure/view_stores.py`:

```python
class RecipeViewStore:
    def create_table(self) -> None:
        self.session.execute(text("""
            CREATE TABLE IF NOT EXISTS recipe_views (
                recipe_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                ingredient_count INTEGER NOT NULL,
                estimated_time TEXT,
                created_at TIMESTAMP NOT NULL
            )
        """))
```

### Step 3: Create Projection Handler

Add event handling in `app/projections/handlers.py`:

```python
class RecipeProjectionHandler:
    def handle_recipe_created(self, event: RecipeCreated):
        view = RecipeView(
            recipe_id=str(event.recipe_id),
            title=event.title,
            ingredient_count=len(event.ingredients),
            estimated_time=event.estimated_time,
            created_at=event.timestamp
        )
        self.recipe_view_store.insert_recipe(view)
```

### Step 4: Register Events

In your application setup:

```python
projection_registry.register(RecipeCreated, recipe_handler.handle_recipe_created)
projection_registry.register(RecipeUpdated, recipe_handler.handle_recipe_updated)
```

## Best Practices

### 1. Design for UI Needs

Read models should match exactly what the UI needs:

```python
# Good: Matches UI requirements exactly
@dataclass
class StoreListItem:
    store_id: str
    name: str
    item_count: int  # UI shows this directly

# Avoid: Forces UI to calculate or transform
@dataclass 
class StoreWithItems:
    store: Store
    items: List[InventoryItem]  # UI must count these
```

### 2. Include Computed Fields

Pre-calculate values the UI needs:

```python
@dataclass
class InventoryItemView:
    # ... other fields
    ingredient_name: str  # Denormalized for display
    store_name: str       # Avoids N+1 queries
    total_value: float    # quantity * price_per_unit
```

### 3. Handle Multiple Events

Some read models need updates from multiple event types:

```python
class StoreProjectionHandler:
    def handle_store_created(self, event: StoreCreated):
        # Create store view with item_count = 0
        
    def handle_inventory_item_added(self, event: InventoryItemAdded):
        # Increment item_count for the store
        
    def handle_inventory_item_removed(self, event: InventoryItemRemoved):
        # Decrement item_count for the store
```

### 4. Use Proper Indexes

Create indexes for common query patterns:

```sql
CREATE INDEX IF NOT EXISTS idx_inventory_store_id 
ON inventory_item_views(store_id);

CREATE INDEX IF NOT EXISTS idx_inventory_added_at 
ON inventory_item_views(added_at DESC);
```

## Testing Read Models

### 1. Test Projection Handlers

```python
def test_inventory_projection_creates_view():
    # Given: Event with ingredient and store data
    event = InventoryItemAdded(...)
    
    # When: Handler processes event
    handler.handle_inventory_item_added(event)
    
    # Then: View is created with denormalized data
    views = view_store.get_by_store_id(event.store_id)
    assert views[0].ingredient_name == "carrots"
    assert views[0].store_name == "CSA Box"
```

### 2. Test End-to-End

```python
def test_api_returns_denormalized_data():
    # Given: Store and inventory exist
    store_service.create_store("CSA Box")
    store_service.upload_inventory(store_id, "2 lbs carrots")
    
    # When: Querying inventory
    response = client.get(f"/stores/{store_id}/inventory")
    
    # Then: Response includes denormalized fields
    items = response.json()
    assert items[0]["ingredient_name"] == "carrots"
    assert items[0]["store_name"] == "CSA Box"
```

## Troubleshooting

### Inconsistent Read Models

If read models get out of sync with domain state:

1. **Check projection handlers** are registered for all relevant events
2. **Verify event ordering** - some projections may need specific event sequences
3. **Consider rebuilding** read models from event store if necessary

### Performance Issues

If queries are slow:

1. **Add missing indexes** for your query patterns
2. **Denormalize more fields** to avoid joins
3. **Batch updates** for high-volume events

### Complex Projections

For projections requiring multiple aggregates:

1. **Load dependencies** within projection handlers
2. **Use eventual consistency** if cross-aggregate data is acceptable to be slightly stale
3. **Consider sagas** for complex multi-step updates

## Migration Strategy

When changing read model structure:

1. **Add new fields** with default values
2. **Create migration scripts** to populate historical data
3. **Remove old fields** after confirming new ones work
4. **Version read models** if breaking changes are required