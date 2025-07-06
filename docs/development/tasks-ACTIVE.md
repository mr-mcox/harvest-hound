# Active Development Tasks

## URGENT: Frontend Test Architecture Fix

**Status**: CRITICAL - Tests failing, blocking clean commits
**Priority**: HIGH - Must complete before continuing UC #1

### Problem Analysis

The frontend API integration work changed the component architecture from:
- **Before**: Testable components accepting props (`inventory`, `onSubmit`)  
- **After**: Self-contained pages managing their own API calls and SvelteKit routing

This broke existing tests that expect the old prop-based interface.

### Root Cause

The tests were written expecting components that accept props, suggesting this was the intended architecture for testability. The current approach couples UI components with data fetching, making them harder to test and less reusable.

### Recommended Solution: Hybrid Architecture

Separate pure UI components from data-fetching page wrappers to maintain both functionality and testability.

### Implementation Plan

#### Phase 1: Extract Pure Components

Create reusable components in `src/lib/components/`:

1. **`InventoryTable.svelte`**
   - Accepts `inventory: InventoryItemWithIngredient[]` prop
   - Pure UI component for displaying inventory data
   - Extracted from current `[id]/+page.svelte`

2. **`InventoryUpload.svelte`** 
   - Accepts `onSubmit: (data: {inventoryText: string}) => Promise<InventoryUploadResult>` prop
   - Pure form component for inventory upload
   - Extracted from current `[id]/upload/+page.svelte`

3. **`StoreCreateForm.svelte`**
   - Already exists but needs interface update to match tests
   - Accepts `onSubmit: (data: StoreFormData) => void` prop
   - Pure form component for store creation

#### Phase 2: Update Pages to Use Components

Transform pages into data-fetching wrappers that handle SvelteKit integration and pass data to pure components.

#### Phase 3: Update Tests

Update test files to import and test pure components instead of pages, removing need for SvelteKit mocking.

#### Phase 4: Verification

Ensure manual functionality still works and all tests pass.

### Files to Change

**New Files**: `src/lib/components/InventoryTable.svelte`, `src/lib/components/InventoryUpload.svelte`

**Modified Files**: All page files and their corresponding test files

### Success Criteria

- [ ] All existing tests pass
- [ ] Manual functionality works identically
- [ ] TypeScript compilation succeeds
- [ ] Components can be rendered in isolation

**Estimated Effort**: 2-3 hours

---

# UC #1 Implementation Plan: Create Inventory Store & Bulk-Upload Inventory

## Overview
User creates a new store (e.g., "CSA Box") and uploads inventory via text/CSV input. The system parses ingredients using LLM, creates dynamic ingredient entities, and displays the parsed inventory immediately.

**Target Observable Behavior**: User pastes "2 lbs carrots, 1 bunch kale, 3 tomatoes" and sees structured inventory table within 30 seconds.

---

## Task 6: REST API
**Goal**: HTTP endpoints support the complete user workflow

### 6.1 API Endpoints (*No tests needed - just FastAPI route definitions*)
- [✓] Create POST /stores endpoint
- [✓] Create GET /stores endpoint
- [✓] Create POST /stores/{id}/inventory endpoint
- [✓] Create GET /stores/{id}/inventory endpoint

### 6.2 API Behavior (*Tests needed*)
- [✓] **Test**: POST /stores with {"name": "CSA Box"} returns 201 with store details
- [✓] **Test**: POST /stores with missing name returns 400 validation error
- [✓] **Test**: GET /stores returns list of all stores with item counts
- [✓] **Test**: POST /stores/{id}/inventory with "2 lbs carrots" returns 201 with parsed items
- [✓] **Test**: POST /stores/{id}/inventory returns 400 for parsing errors
- [✓] **Test**: GET /stores/{id}/inventory returns current inventory with ingredient details
- [✓] **Test**: POST inventory to non-existent store returns 404

---

## Task 7: Frontend Components
**Goal**: User can complete the workflow through web interface

### 7.1 Frontend Setup (*No tests needed - configuration*)
- [✓] Downgrade TailwindCSS from v4 to v3 for Skeleton UI compatibility
- [✓] Verify Skeleton UI components work with TailwindCSS v3

### 7.2 UI Components (*No tests needed - Svelte components with Skeleton UI*)
- [✓] Create store creation form with name, description, infinite_supply fields using Skeleton form components
- [✓] Create inventory upload page with large text area using Skeleton input components
- [✓] Create inventory display table component using Skeleton table components

### 7.3 UI Behavior (*Tests needed*)
- [✓] **Test**: Store creation form submission calls onSubmit handler with form data
- [✓] **Test**: Form shows validation errors for empty name field
- [✓] **Test**: Inventory upload calls onSubmit handler and shows loading state
- [✓] **Test**: Successful upload displays "X items added" message
- [✓] **Test**: Parse errors show error message with original text
- [✓] **Test**: Inventory table displays ingredient name, quantity, unit columns

---

## Task 8: Component Development Tools
**Goal**: Development infrastructure for building and testing components

### 8.1 Storybook Setup (*No tests needed - configuration*)
- [✓] Configure Storybook with Skeleton UI theme
- [✓] Create base story templates for common component patterns

### 8.2 Component Stories (*No tests needed - development aids*)
- [✓] Create stories for store creation form with various states
- [✓] Create stories for inventory upload component with loading/error states
- [✓] Create stories for inventory table with mock data

---

## Task 9: Integration Testing
**Goal**: End-to-end workflow works with Docker Compose coordination and comprehensive mocked testing

### 9.1 Docker Compose Setup (*No tests needed - configuration*)
- [✓] **Create `docker-compose.yml`** in project root for E2E testing
  - [✓] Backend service with test database
  - [✓] Frontend service with test build
  - [✓] Shared network for service communication
- [✓] **Create `docker-compose.dev.yml`** for local development
  - [✓] Backend service with live reload
  - [✓] Frontend service with dev server
  - [✓] Volume mounts for source code
- [✓] **Create test environment scripts**
  - [✓] `scripts/test-e2e.sh` - Automated E2E test runner
  - [✓] `scripts/dev-start.sh` - Local development startup
  - [✓] `scripts/test-manual.sh` - Manual testing with real LLM

### 9.2 Enhanced Mocked Testing (*Tests needed*)
- [✓] **Create LLM response fixtures** in `tests/fixtures/llm_responses.json`
  - [✓] Successful ingredient parsing responses
  - [✓] Partial parsing responses with errors
  - [✓] Complete parsing failure responses
  - [✓] Edge cases (empty input, malformed text)
- [✓] **Create mock LLM service** in `tests/mocks/llm_service.py`
  - [✓] Deterministic responses based on input patterns
  - [✓] Configurable failure modes for error testing
  - [✓] Timing simulation for performance testing
- [✓] **Backend integration tests with mocked LLM**
  - [✓] Full API workflow with predictable LLM responses
  - [✓] Error handling with simulated LLM failures
  - [✓] Performance testing with fast mocked responses

### 9.3 Integration Testing Infrastructure (*Tests needed*)
- [✓] **Backend integration test suite**
  - [✓] Real database (SQLite in-memory for speed)
  - [✓] Mocked LLM service for predictable responses
  - [✓] Full HTTP request/response cycle testing
- [✓] **Frontend integration test suite**
  - [✓] Real API calls to test backend
  - [✓] Mocked LLM service via backend mock
  - [✓] Full UI interaction workflows
- [✓] **Cross-service integration tests**
  - [✓] Docker Compose test environment
  - [✓] Frontend → Backend → Database flow
  - [✓] Real HTTP communication, mocked external services

### 9.4 Happy Path Integration (*Tests needed*)
- [x] **Test**: Create "CSA Box" store → upload "2 lbs carrots, 1 bunch kale" → see 2 items in table
- [x] **Test**: Store list shows "CSA Box" with item_count=2
- [x] **Test**: Page refresh preserves all data (event sourcing working)
- [x] **Test**: Multiple stores maintain separate inventories

### 9.5 Error Handling Integration (*Tests needed*)
- [x] **Test**: Invalid inventory text shows error without crashing
- [x] **Test**: Network errors show appropriate user messages
- [x] **Test**: LLM service unavailable shows graceful error
- [x] **Test**: Partial parsing results display correctly

### 9.6 Performance Testing Setup (*Tests needed*)
- [✓] **Test**: Store creation completes in <1 second
- [✓] **Test**: Mocked LLM parsing completes in <100ms (baseline)
- [✓] **Test**: Inventory display loads in <2 seconds
- [✓] **Test**: Concurrent store creation handles 10 simultaneous requests

### 9.7 Manual Testing Options (*No tests needed - documentation*)
- [✓] **Create manual test scenarios** in `docs/testing/manual-tests.md`
  - [✓] Real LLM integration test procedures
  - [✓] Performance testing with actual API calls
  - [✓] Edge case exploration guidelines
- [✓] **Create testing environment configs**
  - [✓] `config/test-real-llm.env` - Real LLM service configuration
  - [✓] `config/test-mock-llm.env` - Mocked LLM service configuration

### 9.8 Frontend API Integration (*Tests needed*)
- [✓] **Frontend API communication infrastructure**
  - [✓] Add CORS middleware to backend for cross-origin requests
  - [✓] Create centralized API utility module (`src/lib/api.ts`)
  - [✓] Update all frontend API calls to use proper base URLs
- [✓] **Complete store management API integration**
  - [✓] Store creation: `POST /stores` with form data and navigation
  - [✓] Store detail view: `GET /stores/{id}/inventory` with loading states
  - [✓] Inventory upload: `POST /stores/{id}/inventory` with success handling
- [✓] **Maintain backend type synchronization**
  - [✓] Use `InventoryItemWithIngredient` from generated backend types
  - [✓] Ensure frontend types match backend schemas

### 9.9 Frontend Component Test Architecture Fix (*Tests needed - URGENT*)
**Status**: CRITICAL - Tests failing, blocking clean commits

**Problem**: Frontend API integration changed component architecture from testable prop-based components to self-contained pages that manage their own API calls. This broke existing tests that expect the old interface.

- [ ] **Extract pure UI components** in `src/lib/components/`
  - [ ] `InventoryTable.svelte` - accepts `inventory: InventoryItemWithIngredient[]` prop
  - [ ] `InventoryUpload.svelte` - accepts `onSubmit: (data: {inventoryText: string}) => Promise<InventoryUploadResult>` prop  
  - [ ] Update `StoreCreateForm.svelte` to match original test interface
- [ ] **Transform pages into data-fetching wrappers**
  - [ ] `src/routes/stores/[id]/+page.svelte` - loads data and passes to `InventoryTable`
  - [ ] `src/routes/stores/[id]/upload/+page.svelte` - handles API calls and passes handler to `InventoryUpload`
  - [ ] `src/routes/stores/create/+page.svelte` - handles API calls and passes handler to `StoreCreateForm`
- [ ] **Update component tests to use pure components**
  - [ ] Update test imports to use `$lib/components/` instead of pages
  - [ ] Remove SvelteKit mocking (`$page.params.id`, `apiGet`/`apiPost`, `goto`)
  - [ ] Test pure UI behavior with mock data

**Root Cause**: Original test structure indicates hybrid architecture was intended design - pure components for testability, page wrappers for SvelteKit integration.

**Success Criteria**: All tests pass, manual functionality identical, TypeScript compilation succeeds, components can be rendered in isolation.

---

## Task 10: Read Model Projections Implementation (ADR-005)
**Goal**: Implement read model projections to eliminate frontend "smell" and optimize query performance

### 10.1 Backend Read Model Infrastructure (*Tests needed*)
- [ ] **Create read model classes** in `/packages/backend/app/models/read_models.py`
  - [ ] `InventoryItemView` with denormalized fields (ingredient_name, store_name)
  - [ ] `StoreView` with computed fields (item_count)
- [ ] **Create projection handlers** in `/packages/backend/app/projections/handlers.py`
  - [ ] `InventoryProjectionHandler` for inventory events
  - [ ] `StoreProjectionHandler` for store events
- [ ] **Create view stores** in `/packages/backend/app/infrastructure/view_stores.py`
  - [ ] `InventoryItemViewStore` using SQLAlchemy Core
  - [ ] `StoreViewStore` using SQLAlchemy Core
- [ ] **Create projection registry** in `/packages/backend/app/projections/registry.py`
  - [ ] `ProjectionRegistry` for managing event handlers

### 10.2 Database Schema Updates (*No tests needed - migration*)
- [ ] **Create read model tables** with proper indexes
  - [ ] `inventory_item_views` table with denormalized fields
  - [ ] `store_views` table with computed fields
  - [ ] Add indexes for common query patterns
- [ ] **Update EventStore** to trigger projections
  - [ ] Remove inline projection logic
  - [ ] Add projection registry integration

### 10.3 API Layer Updates (*Tests needed*)
- [ ] **Add new read model endpoints**
  - [ ] `GET /stores/{id}/inventory-view` returning `InventoryItemView[]`
  - [ ] `GET /stores-view` returning denormalized store list
- [ ] **Update existing endpoints** to use read models
  - [ ] Modify `GET /stores/{id}/inventory` to use view store
  - [ ] Modify `GET /stores` to use store view
- [ ] **Update service layer** to use view stores instead of joins
  - [ ] Remove N+1 queries from `StoreService.get_store_inventory()`
  - [ ] Add view store dependency injection

### 10.4 Backend Testing (*Tests needed*)
- [ ] **Test projection handlers**
  - [ ] `InventoryItemAdded` event updates `InventoryItemView`
  - [ ] `IngredientCreated` event updates existing inventory views
  - [ ] `StoreCreated` event creates `StoreView`
- [ ] **Test view stores**
  - [ ] Roundtrip tests for read model persistence
  - [ ] Query performance tests
- [ ] **Test API endpoints**
  - [ ] New endpoints return correct denormalized data
  - [ ] Response schemas match `InventoryItemView` structure

### 10.5 Frontend Migration (*Tests needed*)
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

### 10.6 Frontend Testing (*Tests needed*)
- [ ] **Update component tests**
  - [ ] Mock data includes `store_name` field
  - [ ] Type annotations use `InventoryItemView`
- [ ] **Update integration tests**
  - [ ] API endpoint URLs point to new view endpoints
  - [ ] Response structure matches flat view models

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

### 10.8 Integration Testing (*Tests needed*)
- [ ] **End-to-end workflow tests**
  - [ ] Create store → upload inventory → view denormalized data
  - [ ] Multiple stores maintain separate read models
  - [ ] Ingredient name updates propagate to all inventory views
- [ ] **Performance verification**
  - [ ] Read model queries faster than joined queries
  - [ ] Event projection latency acceptable (<100ms)
  - [ ] No N+1 queries in service layer

### 10.9 Migration Strategy (*Tests needed*)
- [ ] **Dual endpoint support** during transition
  - [ ] Keep old endpoints functional
  - [ ] Add read model endpoints in parallel
- [ ] **Data migration**
  - [ ] Populate read model tables from existing events
  - [ ] Verify projection consistency
- [ ] **Cleanup phase**
  - [ ] Remove old join-based endpoints
  - [ ] Remove frontend interface extensions

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
