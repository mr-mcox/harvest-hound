# Inventory Management - Design Document

## Purpose

Enable users to create ingredient stores and upload inventory via simple text/CSV input, providing the foundation for meal planning ingredient availability.

## Core Use Case (UC #1)

**Happy Path**: User creates a "CSA Box" store, pastes "2 lbs carrots, 1 bunch kale, 3 tomatoes", sees parsed inventory displayed immediately with no duplicates or unit conversion issues.

## Domain Model - MVP

### Core Aggregates

```python
class IngredientStore:
    store_id: UUID
    name: str                    # "My CSA Box", "Freezer", "Pantry"
    description: str = ""        # "Weekly CSA delivery" or "Italian/Indian pantry staples"
    infinite_supply: bool = False # True for pantry/grocery stores
    created_at: datetime

    inventory_items: List[InventoryItem]

class Ingredient:
    ingredient_id: UUID
    name: str           # "carrots", "kale", "tomatoes"
    default_unit: str   # "lbs", "bunch", "whole"
    created_at: datetime
```

### Value Objects

```python
class InventoryItem:
    store_id: UUID
    ingredient_id: UUID  # Links to Ingredient aggregate
    quantity: float      # 2.0, 1.0, 3.0
    unit: str           # "lbs", "bunch", "whole"
    notes: str = ""     # Optional user notes
    added_at: datetime
```

**Key Design Decisions:**
- **Ingredient as separate aggregate**: Enables reuse across stores and future recipe linking
- **Dynamic ingredient creation**: Create new Ingredient for each parsed item (no duplicate handling initially)
- **Quantity as float + unit**: Clean separation, defer unit conversion complexity
- **Happy path assumptions**: No duplicates, consistent units, clean LLM parsing

### Domain Events

```python
@dataclass
class StoreCreated:
    store_id: UUID
    name: str
    description: str
    infinite_supply: bool
    timestamp: datetime

@dataclass
class IngredientCreated:
    ingredient_id: UUID
    name: str
    default_unit: str
    timestamp: datetime

@dataclass
class InventoryItemAdded:
    store_id: UUID
    ingredient_id: UUID
    quantity: float
    unit: str
    notes: str
    timestamp: datetime
```

## Application Services - MVP

### LLMInventoryParser

Use LLM to parse natural language inventory input:

```python
class LLMInventoryParser:
    def parse_inventory_text(self, raw_text: str) -> List[ParsedInventoryItem]:
        # LLM prompt: Parse this inventory list into structured data
        # Input: "2 lbs carrots, 1 bunch kale, 3 tomatoes"
        # Output: [
        #   {"name": "carrots", "quantity": 2.0, "unit": "lbs"},
        #   {"name": "kale", "quantity": 1.0, "unit": "bunch"},
        #   {"name": "tomatoes", "quantity": 3.0, "unit": "whole"}
        # ]

@dataclass
class ParsedInventoryItem:
    name: str
    quantity: float
    unit: str
    notes: str = ""
```

**MVP Approach**: Single LLM call with structured output. No complex retry logic or validation.

### StoreService

Orchestrates store creation and inventory upload:

```python
class StoreService:
    def create_store(self, name: str, description: str = "", infinite_supply: bool = False) -> UUID:
        # Create IngredientStore aggregate
        # Emit StoreCreated event
        # Return store_id

    def upload_inventory(self, store_id: UUID, raw_text: str) -> InventoryUploadResult:
        # 1. Parse text with LLM
        # 2. For each parsed item:
        #    - Create new Ingredient (assume no duplicates)
        #    - Create InventoryItem linking to ingredient
        #    - Emit IngredientCreated and InventoryItemAdded events
        # 3. Return success result with created items

@dataclass
class InventoryUploadResult:
    items_added: int
    items: List[InventoryItem]
    errors: List[str] = field(default_factory=list)
```

**Key Simplification**: Always create new Ingredient - no duplicate detection or merging logic.

## API Design - MVP

### Endpoints

```
POST /stores
{
  "name": "CSA Box",
  "description": "Weekly delivery",
  "infinite_supply": false
}
→ {
    "store_id": "uuid",
    "name": "CSA Box",
    "description": "Weekly delivery",
    "infinite_supply": false
  }

POST /stores/{store_id}/inventory
{
  "inventory_text": "2 lbs carrots\n1 bunch kale\n3 tomatoes"
}
→ {
    "items_added": 3,
    "errors": [],
    "success": true
  }

GET /stores/{store_id}/inventory
→ [
    {
      "store_id": "uuid",
      "ingredient_id": "uuid1",
      "ingredient_name": "carrots",    // Denormalized from ingredient
      "store_name": "CSA Box",         // Denormalized from store
      "quantity": 2.0,
      "unit": "lbs",
      "notes": "",
      "added_at": "2025-07-07T10:30:00Z"
    },
    {
      "store_id": "uuid",
      "ingredient_id": "uuid2",
      "ingredient_name": "kale",
      "store_name": "CSA Box",
      "quantity": 1.0,
      "unit": "bunch",
      "notes": "",
      "added_at": "2025-07-07T10:30:00Z"
    }
  ]

GET /stores
→ [
    {
      "store_id": "uuid",
      "name": "CSA Box",
      "description": "Weekly delivery",
      "item_count": 3,              // Computed from inventory items
      "infinite_supply": false
    }
  ]
```

**Key Changes from Read Model Implementation:**
- **Denormalized responses**: `ingredient_name` and `store_name` included in inventory items
- **Flat array responses**: Direct arrays instead of nested objects
- **Computed fields**: `item_count` calculated from actual inventory
- **Simplified upload response**: Focus on success/error status rather than item details

## Infrastructure - MVP

### Event Store
- SQLite with simple events table: `(stream_id, event_type, event_data, timestamp)`
- Stream per aggregate: `ingredient-{id}`, `store-{id}`
- No snapshots initially - rebuild aggregates from events

### Read Models (Event Projections)
- **`store_views` table**: Denormalized store data with computed `item_count`
- **`inventory_item_views` table**: Flat view with `ingredient_name` and `store_name` denormalized
- **Projection handlers**: `StoreProjectionHandler` and `InventoryProjectionHandler` update views on events
- **Synchronous updates**: Views updated immediately when events are stored (no eventual consistency)
- **Optimized queries**: Eliminates N+1 queries and frontend data merging

### LLM Integration
- BAML integration for structured parsing
- Single completion call per inventory upload
- Basic error handling for malformed LLM responses

## Implementation Order

### Phase 1: Core Domain
1. `Ingredient` and `IngredientStore` aggregates
2. `InventoryItem` value object
3. Domain events with SQLite event store
4. Basic aggregate loading from events

### Phase 2: LLM Integration
1. BAML setup for inventory parsing
2. `LLMInventoryParser` with structured output
3. Error handling for LLM failures

### Phase 3: Application Services
1. `StoreService` orchestrating creation and upload
2. Read model projections from events
3. Basic validation and error handling

### Phase 4: API & UI
1. REST endpoints for store CRUD and inventory upload
2. Frontend forms for store creation
3. Text area for inventory input
4. Table display of parsed inventory with ingredient details

## Happy Path Assumptions (Deferred Complexity)

### No Duplicate Handling
- Always create new Ingredient for each parsed item
- User sees multiple "carrots" entries if they upload twice
- **Future**: Ingredient matching and merging logic

### No Unit Conversion
- Store quantities exactly as parsed by LLM
- Assume user provides consistent units
- **Future**: Convert "1 lb" + "16 oz" → "2 lbs"

### Simple Error Handling
- LLM parsing failures return generic error
- No partial success scenarios
- **Future**: Retry logic, partial uploads, detailed error reporting

### Single User Context
- No user authentication or multi-tenancy
- All stores global to application
- **Future**: User-scoped stores and permissions

## Success Metrics - MVP

- User can create store in <30 seconds
- LLM correctly parses 90%+ of common inventory formats
- Inventory displays immediately after upload
- Clean ingredient/store separation enables future recipe integration
- Zero configuration required for basic usage

---

This design prioritizes getting UC #1 working end-to-end with LLM-powered parsing and clean domain separation, while explicitly deferring complex edge cases for future iterations.
