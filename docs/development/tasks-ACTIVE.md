# UC #1 Implementation Plan: Create Inventory Store & Bulk-Upload Inventory

## Overview
User creates a new store (e.g., "CSA Box") and uploads inventory via text/CSV input. The system parses ingredients using LLM, creates dynamic ingredient entities, and displays the parsed inventory immediately.

**Target Observable Behavior**: User pastes "2 lbs carrots, 1 bunch kale, 3 tomatoes" and sees structured inventory table within 30 seconds.

---

## Task 1: Core Domain Model
**Goal**: Domain aggregates can be created, store events, and rebuild from events

### 1.1 Basic Domain Classes (*No tests needed - just class definitions*)
- [✓] Create `Ingredient` dataclass with ingredient_id, name, default_unit, created_at
- [✓] Create `InventoryItem` dataclass with store_id, ingredient_id, quantity, unit, notes, added_at
- [✓] Create `InventoryStore` class with store_id, name, description, infinite_supply, inventory_items list
- [✓] Create event dataclasses: `StoreCreated`, `IngredientCreated`, `InventoryItemAdded`

### 1.2 Domain Behavior (*Tests needed*)
- [✓] **Test**: InventoryStore creation generates StoreCreated event with correct store details
- [✓] **Test**: Adding inventory item to store generates InventoryItemAdded event
- [✓] **Test**: InventoryStore can be rebuilt from sequence of StoreCreated + InventoryItemAdded events
- [✓] **Test**: Ingredient creation generates IngredientCreated event with name and default_unit

### 1.3 Refactor: Functional Event Generation (*Tests needed - refactor existing*)
**Goal**: Replace `uncommitted_events` pattern with functional approach returning tuples

- [✓] Create pure functions for domain operations in `app/domain/operations.py`
- [✓] **Refactor Test**: Update InventoryStore.create() to return `(store, events)` tuple
- [✓] **Refactor Test**: Update add_inventory_item() to return `(store, events)` tuple
- [✓] **Refactor Test**: Update Ingredient.create() to return `(ingredient, events)` tuple
- [✓] **Refactor Test**: Update from_events() to work with clean domain models
- [✓] Remove `uncommitted_events` fields from all domain models
- [✓] Update all existing tests to handle tuple returns
- [✓] Ensure all tests still pass with new pattern

---

## Task 2: Event Store Infrastructure
**Goal**: Events can be persisted to SQLite and aggregates reconstructed

### 2.1 Event Store Implementation (*Minimal tests needed*)
- [✓] Create SQLite table schema: `events(stream_id, event_type, event_data, timestamp)`
- [✓] Create `EventStore` class with append_event() and load_events() methods

### 2.2 Event Store Behavior (*Tests needed*)
- [✓] **Test**: EventStore.append_event() persists StoreCreated event to SQLite
- [✓] **Test**: EventStore.load_events() returns events by stream_id in chronological order
- [✓] **Test**: EventStore handles concurrent writes without corruption

### 2.3 Repository Pattern (*Tests needed*)
- [✓] **Test**: IngredientRepository can save Ingredient and reload from IngredientCreated events
- [✓] **Test**: StoreRepository can save InventoryStore and reload from StoreCreated + InventoryItemAdded events
- [✓] **Test**: Repository throws appropriate error when aggregate not found

---

## Task 3: LLM Inventory Parser
**Goal**: Natural language text is parsed into structured inventory items

### 3.1 BAML Setup (*No tests needed - configuration*)
- [ ] Install BAML dependencies and configure client
- [ ] Create inventory parsing prompt template

### 3.2 Parser Implementation and Behavior (*Tests needed*)
- [x] **Test**: Parse "2 lbs carrots" → {"name": "carrot", "quantity": 2.0, "unit": "pound"}
- [ ] **Test**: Parse "1 bunch kale" → {"name": "kale", "quantity": 1.0, "unit": "bunch"}
- [ ] **Test**: Parse multi-line "2 lbs carrots\n1 bunch kale" → 2 parsed items
- [ ] **Test**: Parse CSV format "carrots, 2, lbs" → correct structured output
- [ ] **Test**: Handle parsing errors with meaningful error messages
- [ ] **Test**: Empty input returns empty list (no error)
- [ ] **Test**: Malformed input returns error with original text preserved

### 3.3 BAML-to-Domain Translation (*Tests needed*)
**Goal**: Convert BAML-generated types to domain models cleanly
- [ ] **Test**: BAML InventoryParseResult converts to domain ParsedInventoryItem
- [ ] **Test**: Translation preserves all data fields correctly
- [ ] **Test**: Translation handles missing/null fields gracefully
- [ ] **Test**: Translation validates domain constraints (positive quantities, valid units)

---

## Task 4: Application Services
**Goal**: Orchestrate domain operations with proper error handling

### 4.1 StoreService Class (*No tests needed - just class definition*)
- [ ] Create `StoreService` with create_store() and upload_inventory() methods
- [ ] Create `InventoryUploadResult` dataclass

### 4.2 Store Creation Behavior (*Tests needed*)
- [ ] **Test**: StoreService.create_store("CSA Box") returns UUID and persists StoreCreated event
- [ ] **Test**: create_store() with infinite_supply=True sets flag correctly in event
- [ ] **Test**: create_store() with duplicate name succeeds (no uniqueness constraint)

### 4.3 Inventory Upload Behavior (*Tests needed*)
- [ ] **Test**: upload_inventory() parses "2 lbs carrots" and creates new Ingredient with name="carrots"
- [ ] **Test**: upload_inventory() creates InventoryItem linking to ingredient via ingredient_id
- [ ] **Test**: upload_inventory() emits both IngredientCreated and InventoryItemAdded events
- [ ] **Test**: upload_inventory() returns InventoryUploadResult with items_added=1
- [ ] **Test**: upload_inventory() handles LLM parsing errors and returns error in result
- [ ] **Test**: get_store_inventory() returns current inventory with ingredient names

---

## Task 5: Read Model Projections
**Goal**: Fast queries for UI without rebuilding aggregates

### 5.1 Projection Tables (*No tests needed - just SQL schema*)
- [ ] Create `ingredients` table for ingredient lookups
- [ ] Create `stores` table for store list queries
- [ ] Create `current_inventory` view joining stores + inventory_items + ingredients

### 5.2 Projection Behavior (*Tests needed*)
- [ ] **Test**: IngredientCreated event updates ingredients table
- [ ] **Test**: StoreCreated event updates stores table with store details
- [ ] **Test**: InventoryItemAdded event updates current_inventory view with ingredient name
- [ ] **Test**: Store list query returns store_id, name, description, item_count
- [ ] **Test**: Inventory query returns items with ingredient_name, quantity, unit
- [ ] **Test**: Ingredient lookup by ID uses projection table (performance optimization)

---

## Task 6: REST API
**Goal**: HTTP endpoints support the complete user workflow

### 6.1 API Endpoints (*No tests needed - just Flask route definitions*)
- [ ] Create POST /stores endpoint
- [ ] Create GET /stores endpoint
- [ ] Create POST /stores/{id}/inventory endpoint
- [ ] Create GET /stores/{id}/inventory endpoint

### 6.2 API Behavior (*Tests needed*)
- [ ] **Test**: POST /stores with {"name": "CSA Box"} returns 201 with store details
- [ ] **Test**: POST /stores with missing name returns 400 validation error
- [ ] **Test**: GET /stores returns list of all stores with item counts
- [ ] **Test**: POST /stores/{id}/inventory with "2 lbs carrots" returns 201 with parsed items
- [ ] **Test**: POST /stores/{id}/inventory returns 400 for parsing errors
- [ ] **Test**: GET /stores/{id}/inventory returns current inventory with ingredient details
- [ ] **Test**: POST inventory to non-existent store returns 404

---

## Task 7: Frontend Components
**Goal**: User can complete the workflow through web interface

### 7.1 UI Components (*No tests needed - just HTML/JS*)
- [ ] Create store creation form with name, description, infinite_supply fields
- [ ] Create inventory upload page with large text area
- [ ] Create inventory display table component

### 7.2 UI Behavior (*Tests needed*)
- [ ] **Test**: Store creation form submission calls POST /stores and shows success message
- [ ] **Test**: Form shows validation errors for empty name field
- [ ] **Test**: Inventory upload calls POST /stores/{id}/inventory and shows loading state
- [ ] **Test**: Successful upload displays "X items added" and updates inventory table
- [ ] **Test**: Parse errors show error message with original text
- [ ] **Test**: Inventory table displays ingredient name, quantity, unit columns

---

## Task 8: Integration Testing
**Goal**: End-to-end workflow works as expected

### 8.1 Happy Path Integration (*Tests needed*)
- [ ] **Test**: Create "CSA Box" store → upload "2 lbs carrots, 1 bunch kale" → see 2 items in table
- [ ] **Test**: Store list shows "CSA Box" with item_count=2
- [ ] **Test**: Page refresh preserves all data (event sourcing working)
- [ ] **Test**: Multiple stores maintain separate inventories

### 8.2 Error Handling Integration (*Tests needed*)
- [ ] **Test**: Invalid inventory text shows error without crashing
- [ ] **Test**: Network errors show appropriate user messages
- [ ] **Test**: LLM service unavailable shows graceful error

### 8.3 Performance Requirements (*Tests needed*)
- [ ] **Test**: Store creation completes in <1 second
- [ ] **Test**: LLM parsing completes in <10 seconds for typical inventory
- [ ] **Test**: Inventory display loads in <2 seconds

---

## Success Criteria

**MVP Complete When:**
1. User can create a store in under 30 seconds
2. User can upload inventory text and see parsed results immediately
3. LLM correctly parses 90%+ of common inventory formats
4. All inventory data persists across application restarts
5. Clean separation between ingredients and inventory enables future recipe features

**Ready for UC #2 When:**
- All testable behaviors above are working
- Code is maintainable with proper separation of concerns
- Error handling covers common failure modes
- UI provides clear feedback for all user actions
