# Active Development Tasks
---

# UC #1 Implementation Plan: Create Inventory Store & Bulk-Upload Inventory

## Overview
User creates a new store (e.g., "CSA Box") and uploads inventory via text/CSV input. The system parses ingredients using LLM, creates dynamic ingredient entities, and displays the parsed inventory immediately.

**Target Observable Behavior**: User pastes "2 lbs carrots, 1 bunch kale, 3 tomatoes" and sees structured inventory table within 30 seconds.

---

## Task 10: Read Model Projections Implementation (ADR-005)
**Goal**: Implement read model projections to eliminate frontend "smell" and optimize query performance

**REFACTOR NOTE**: This is primarily a refactor changing data structures, not behavior. Most tasks should modify existing tests rather than create new ones.

### 10.1 Backend Read Model Infrastructure (*Tests needed*)
- [✓] **Create read model classes** in `/packages/backend/app/models/read_models.py`
  - [✓] `InventoryItemView` with denormalized fields (ingredient_name, store_name)
  - [✓] `StoreView` with computed fields (item_count)
- [✓] **Create projection handlers** in `/packages/backend/app/projections/handlers.py`
  - [✓] `InventoryProjectionHandler` for inventory events
  - [✓] `StoreProjectionHandler` for store events
- [✓] **Create view stores** in `/packages/backend/app/infrastructure/view_stores.py`
  - [✓] `InventoryItemViewStore` using SQLite Core
  - [✓] `StoreViewStore` using SQLite Core
- [✓] **Create projection registry** in `/packages/backend/app/projections/registry.py`
  - [✓] `ProjectionRegistry` for managing event handlers

### 10.2 Database Schema Updates (*No tests needed - migration*)
- [✓] **Create read model tables** with proper indexes
  - [✓] `inventory_item_views` table with denormalized fields
  - [✓] `store_views` table with computed fields
  - [✓] Add indexes for common query patterns
- [✓] **Update EventStore** to trigger projections
  - [Partial] Keep inline projection logic for backward compatibility
  - [✓] Add projection registry integration

### 10.3 API Layer Updates (*Tests needed*)
- [x] **Add new read model endpoints**
  - [x] `GET /stores/{id}/inventory-view` returning `InventoryItemView[]`
  - [x] `GET /stores-view` returning denormalized store list
- [x] **Update existing endpoints** to use read models
  - [x] Modify `GET /stores/{id}/inventory` to use view store
  - [x] Modify `GET /stores` to use store view
- [x] **Update service layer** to use view stores instead of joins
  - [x] Remove N+1 queries from `StoreService.get_store_inventory()`
  - [x] Add view store dependency injection

### 10.4 Backend Testing (*Modify existing tests*)
- [✓] **Update projection handler tests**
  - [✓] Modify existing event handler tests to verify `InventoryItemView` updates
  - [✓] Update ingredient tests to check view propagation
  - [✓] Update store tests to verify `StoreView` creation
- [ ] **Update view store tests**
  - [ ] Modify existing persistence tests for read model roundtrips
  - [ ] Update query tests to use view stores
- [ ] **Update API endpoint tests**
  - [ ] Modify existing endpoint tests to expect denormalized data
  - [ ] Update response schema assertions to match `InventoryItemView`

### 10.5 Frontend Migration (*Update existing tests*)
- [ ] **Remove interface extensions** (eliminate the "smell")
  - [ ] Delete `InventoryItemWithIngredient` from `/packages/frontend/src/lib/types.ts`
  - [ ] Update imports across all components
- [ ] **Update API calls** to use new endpoints
  - [ ] Change inventory endpoints from `/inventory` to `/inventory-view`
  - [ ] Update store listing endpoints
- [ ] **Update component types**
  - [ ] Replace `InventoryItemWithIngredient` with `InventoryItemView`
  - [ ] Update all component prop types
- [ ] **Regenerate types** from updated backend schemas
  - [ ] Run `python scripts/export_schemas.py`
  - [ ] Run `npm run generate-types`

### 10.6 Frontend Testing (*Modify existing tests*)
- [ ] **Update component tests**
  - [ ] Modify mock data to include `store_name` field
  - [ ] Update type annotations to use `InventoryItemView`
- [ ] **Update integration tests**
  - [ ] Change API endpoint URLs to point to new view endpoints
  - [ ] Update response structure expectations to match flat view models

### 10.7 Documentation Updates (*No tests needed - documentation*)
- [ ] **Update API documentation**
  - [ ] `docs/architecture/interface.md` - new read model endpoints
  - [ ] `docs/features/inventory/design.md` - flat response structures
- [ ] **Update domain documentation**
  - [ ] `docs/architecture/domain-model.md` - read model concepts
  - [ ] `docs/architecture/overview.md` - CQRS patterns
- [ ] **Create implementation guides**
  - [ ] Read model architecture guide
  - [ ] Event projection development guide
  - [ ] Frontend integration guide

### 10.8 Integration Testing (*Modify existing tests*)
- [ ] **Update end-to-end workflow tests**
  - [ ] Modify store creation tests to expect denormalized data
  - [ ] Update inventory upload tests to verify view model responses
  - [ ] Update ingredient update tests to verify view propagation

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
