---
date: 2025-12-05
feature: admin-config
status: draft
frame: .scratch/frame-admin-config.md
estimated_effort: M
confidence: High
tags: [config, settings, database, crud, frontend]
---

# Technical Implementation Plan: Admin/Config Interface

## Context

### Problem Statement

Before the steel thread can run (CSA delivery → planning → shopping list → cook), foundational configuration needs to exist: household context for recipe generation, pantry assumptions, and grocery stores for shopping list claims. These are set-once-tweak-occasionally settings that shouldn't clutter the main workflow.

### User Stories

**Essential**:
1. **Configure Household Profile** - Set family cooking context once for recipe generation
2. **Configure Pantry** - Define assumed-available staples (unlimited, unclaimed)
3. **Manage Grocery Stores** - CRUD for shopping destinations (Cub, Costco, Co-op)
4. **Remove Scaffolding** - Clean up hello world dishes demo

### Key Acceptance Criteria (TDD Seeds)

From the feature frame:
- Household profile: view, edit, persist, used in prompts
- Pantry: view, edit, used in generation (unlimited, unclaimed)
- Grocery stores: add, edit, delete (if no active claims), at least one must exist
- Scaffolding: remove `/api/dishes`, `dishes.baml`, demo UI; remove `/api/hello` after real endpoints exist

### Scope Boundaries

**In Scope**:
- Database models for HouseholdProfile, Pantry, GroceryStore
- REST APIs for config CRUD
- `/settings` page with text areas and grocery store table
- Default seeding on first run (all three config types)
- Backend API tests + basic frontend component tests

**Out of Scope** (deferred):
- Location filtering/audit view
- Portion hint management UI
- Per-session grocery store selection
- BAML integration (household profile/pantry in prompts) - separate feature

### Relevant Prototype Patterns

From LEARNINGS.md:
- "Household profile as prompt constant - felt 'in the ballpark'"
- "Store management used but infrequent - could be buried in configuration interface"
- "Multiple grocery stores, not singleton - Costco, Cub, Co-op for different rhythms"
- "Three-tier architecture: Explicit inventory, Pantry (singleton), Grocery stores (multiple)"

From codebase exploration:
- SQLModel pattern in `src/backend/models.py` - ready for model definitions
- Router pattern in `src/backend/routes.py` - `/api` prefix, dependency injection
- SvelteKit routing - `+page.svelte` for routes
- Skeleton UI components - cards, inputs, buttons with preset classes

---

## Implementation Phases

### Phase 1: Database Models & Seeding

**Purpose**: Establish data foundation so all subsequent phases have schema and default data to work with.

**Scope**:
- Define SQLModel classes: `HouseholdProfile`, `Pantry`, `GroceryStore`
- Table creation on app startup
- Seeding logic for first-run defaults (placeholder content for all three)

**TDD Focus**:
- Model instantiation and field validation
- Test approach: Unit tests for model classes

**Key Considerations**:
- Singleton pattern for HouseholdProfile and Pantry (only one row each)
- GroceryStore needs `created_at` for ordering
- Seeding must be idempotent (don't duplicate on restart)

**Dependencies**: None - this is foundational

**Complexity**: S

---

### Phase 2: Singleton Config APIs (Household Profile + Pantry)

**Purpose**: Provide GET/PUT endpoints for the two singleton configs. Simpler than CRUD since there's always exactly one record.

**Scope**:
- `GET /api/config/household-profile` - return current content
- `PUT /api/config/household-profile` - update content
- `GET /api/config/pantry` - return current content
- `PUT /api/config/pantry` - update content

**TDD Focus**:
- GET returns seeded default on fresh DB
- PUT updates content, returns updated record
- PUT with empty content is allowed (user may clear it)
- Test approach: Integration tests with test database

**Key Considerations**:
- Upsert pattern: PUT creates if not exists, updates if exists
- Return `updated_at` timestamp for UI feedback
- Consider shared router prefix `/api/config/`

**Dependencies**: Phase 1 (models and seeding)

**Complexity**: S

---

### Phase 3: Grocery Store CRUD API

**Purpose**: Full CRUD for grocery stores. More complex due to list management and delete constraints.

**Scope**:
- `GET /api/config/grocery-stores` - list all stores
- `POST /api/config/grocery-stores` - create new store
- `GET /api/config/grocery-stores/{id}` - get single store
- `PUT /api/config/grocery-stores/{id}` - update store
- `DELETE /api/config/grocery-stores/{id}` - delete store

**TDD Focus**:
- List returns seeded default store
- Create adds new store, returns with ID
- Update modifies name/description
- Delete removes store (constraint checking deferred - no claims exist yet)
- Prevent deleting last store (at least one must exist)
- Test approach: Integration tests with test database

**Key Considerations**:
- Delete constraint (no active claims) noted but not implemented yet - claims don't exist
- "At least one store" validation on delete
- Order by `created_at` for consistent listing

**Dependencies**: Phase 1 (models)

**Complexity**: S

---

### Phase 4: Settings Page UI

**Purpose**: Create the frontend `/settings` route with all three configuration sections.

**Scope**:
- New route at `/settings`
- Navigation from main page to settings
- Household Profile section: text area, save button
- Pantry section: text area, save button
- Grocery Stores section: table with add/edit/delete

**TDD Focus**:
- Settings page renders with three sections
- Text areas load current values from API
- Save updates persist and show feedback
- Grocery store table shows list, add/edit/delete work
- Test approach: Component tests (mounting, API mocking)

**Key Considerations**:
- Svelte 5 runes for state management
- Skeleton UI components for consistent styling
- Optimistic UI updates vs wait-for-response
- Error handling and loading states
- "Back to main" navigation

**Dependencies**: Phases 2 & 3 (APIs must exist)

**Complexity**: M

---

### Phase 5: Scaffolding Removal

**Purpose**: Clean up demo code now that real endpoints and UI exist.

**Scope**:
- Remove `GET /api/dishes` endpoint
- Remove `GET /api/dishes/stream` endpoint
- Remove `dishes.baml` (or entire file if nothing else in it)
- Remove demo UI from main `+page.svelte`
- Remove `/api/hello` endpoint
- Clean up `baml_functions.py` if dishes functions removed

**TDD Focus**:
- Removed endpoints return 404
- App still starts and serves frontend
- Test approach: Smoke test (app health check)

**Key Considerations**:
- Do this last so we have real endpoints to verify stack
- May need placeholder content on main page after demo removal
- Regenerate BAML client after removing dishes.baml

**Dependencies**: Phases 2-4 (real features must exist first)

**Complexity**: XS

---

## Sequencing Logic

**Why this order**:
1. **Models first** - Everything depends on database schema
2. **Singletons before CRUD** - Simpler pattern, builds confidence
3. **All APIs before UI** - Frontend needs endpoints to call
4. **Scaffolding last** - Keep demo until real features work

**Parallel work possible**:
- Phases 2 & 3 could run in parallel (independent APIs)
- Phase 4 could start UI scaffolding while Phase 3 finishes

**Dependencies constrain**:
- Phase 1 must complete before 2, 3
- Phases 2 & 3 must complete before 4
- Phases 2-4 must complete before 5

---

## High-Level Test Strategy

**TDD throughout** - Write tests before implementation in each phase.

**Test types needed**:
- **Unit tests**: Model validation, helper functions
- **Integration tests**: API endpoints with test database
- **Component tests**: Svelte components with mocked API

**Key scenarios to validate**:
- Fresh database has seeded defaults
- Config updates persist across requests
- Grocery store CRUD operations work correctly
- UI loads data and handles save/error states
- App functions after scaffolding removal

---

## Integration Points

**Backend**:
- `models.py` - New model classes
- `routes.py` - New config router (or separate `config_routes.py`)
- `app.py` - Seeding on startup, remove dishes imports

**Frontend**:
- New `/settings` route
- Main page navigation to settings
- API calls to `/api/config/*` endpoints

**BAML**:
- Remove `dishes.baml`
- Regenerate client
- Note: Actually *using* household profile/pantry in prompts is a separate feature

---

## Risk Assessment

**Low risks** (straightforward implementation):
- Database models are simple (text fields, timestamps)
- CRUD patterns are well-established
- Skeleton UI provides good component foundation

**Medium risks** (watch for):
- Singleton upsert pattern - ensure idempotent behavior
- "At least one grocery store" validation - handle edge cases
- Frontend state management - ensure save feedback is clear

**Mitigation strategies**:
- Test seeding idempotency explicitly
- Write delete validation test before implementing
- Use loading/success/error states consistently in UI

**Steering likelihood**: Low - patterns are clear, no novel architecture

---

## Implementation Notes

**TDD**: Test-Driven Development throughout all phases. Red-green-refactor cycle.

**Prototype patterns to follow**:
- SQLModel pattern from existing `models.py`
- Router organization from `routes.py`
- Svelte 5 runes from demo `+page.svelte`
- Skeleton UI classes from existing components

**Prototype patterns to change**:
- Remove unified "store" concept - use distinct Pantry, Inventory, GroceryStore
- Add dedicated config router vs mixing with other endpoints

**Quality gates**:
- All tests pass before moving to next phase
- `pre-commit run --all-files` passes
- Manual smoke test of settings flow after Phase 4

---

## Overall Complexity Estimate

**Overall**: M (Moderate)

**Confidence**: High

**Justification**:
- Established patterns throughout (CRUD, SQLModel, SvelteKit routing)
- No novel architecture - following existing codebase conventions
- Multiple integration points but all straightforward
- Main complexity is frontend polish (table UI, form handling)
- Low steering likelihood - clear requirements from feature frame

---

## Implementation Tasks

**TIP Reference**: Phases 1-5 above
**Task Sequencing**: Tasks follow phase order. Within phases, SETUP tasks enable NEW BEHAVIOR tasks.

---

## Task 1: Database Models & Seeding (TIP Phase 1)
**Goal**: Establish data foundation with models and idempotent seeding
**TIP Context**: Phase 1 - foundational, no dependencies

### 1.1 Test Infrastructure Setup - **🏗️ SETUP ONLY**
- [x] **Create test directory** - `src/backend/tests/` with `__init__.py`
- [x] **Create conftest.py** - `src/backend/tests/conftest.py` with test database fixture using in-memory SQLite
- [x] **Add pytest dependency** - Add `pytest>=8.0.0` and `httpx>=0.27.0` (for TestClient) to `pyproject.toml` dev dependencies

### 1.2 SQLModel Classes - **🏗️ SETUP ONLY**
- [x] **HouseholdProfile model** - Add to `src/backend/models.py:28` (before `create_all`):
  - Fields: `id: int | None` (primary key), `content: str`, `updated_at: datetime`
  - `table=True` for SQLModel
- [x] **Pantry model** - Add to `src/backend/models.py`:
  - Fields: `id: int | None` (primary key), `content: str`, `updated_at: datetime`
  - `table=True` for SQLModel
- [x] **GroceryStore model** - Add to `src/backend/models.py`:
  - Fields: `id: int | None` (primary key), `name: str`, `description: str`, `created_at: datetime`
  - `table=True` for SQLModel

### 1.3 Seeding Logic - **🧪 NEW BEHAVIOR**
- [x] **Write test** - `src/backend/tests/test_seeding.py::test_seed_creates_defaults_on_empty_db` verifying all three configs exist after seeding
- [x] **Write test** - `test_seed_is_idempotent` verifying running seed twice doesn't duplicate records
- [x] **Create seed function** - `src/backend/models.py::seed_defaults()` that checks for existing records before inserting
- [x] **Default content for HouseholdProfile** - Placeholder text: "Describe your household cooking context..."
- [x] **Default content for Pantry** - Placeholder text: "List your pantry staples (salt, pepper, olive oil, etc.)..."
- [x] **Default GroceryStore** - Name: "Grocery Store", Description: "Default grocery store for shopping lists"
- [x] **Call seed on startup** - Add `seed_defaults()` call in `src/backend/models.py` after `create_all()`

---

## Task 2: Singleton Config APIs (TIP Phase 2)
**Goal**: GET/PUT endpoints for household profile and pantry
**TIP Context**: Phase 2 - depends on Phase 1 models

### 2.1 Config Router Setup - **🏗️ SETUP ONLY**
- [x] **Create config routes file** - `src/backend/config_routes.py` with `APIRouter(prefix="/api/config")`
- [x] **Include in app** - Import and include router in `src/backend/app.py:25`
- [x] **Create Pydantic schemas** - `src/backend/schemas.py` with:
  - `SingletonConfigResponse`: `content: str`, `updated_at: datetime`
  - `SingletonConfigUpdate`: `content: str`

### 2.2 Household Profile API - **🧪 NEW BEHAVIOR**
- [x] **Write test** - `src/backend/tests/test_config_api.py::test_get_household_profile_returns_seeded_default`
- [x] **Write test** - `test_put_household_profile_updates_content`
- [x] **Write test** - `test_put_household_profile_allows_empty_content`
- [x] **Implement GET** - `GET /api/config/household-profile` in `config_routes.py`
- [x] **Implement PUT** - `PUT /api/config/household-profile` with upsert logic

### 2.3 Pantry API - **🧪 NEW BEHAVIOR**
- [x] **Write test** - `test_get_pantry_returns_seeded_default`
- [x] **Write test** - `test_put_pantry_updates_content`
- [x] **Write test** - `test_put_pantry_allows_empty_content`
- [x] **Implement GET** - `GET /api/config/pantry` in `config_routes.py`
- [x] **Implement PUT** - `PUT /api/config/pantry` with upsert logic

---

## Task 3: Grocery Store CRUD API (TIP Phase 3)
**Goal**: Full CRUD for grocery stores with delete constraints
**TIP Context**: Phase 3 - depends on Phase 1 models

### 3.1 Grocery Store Schemas - **🏗️ SETUP ONLY**
- [x] **Add schemas** - Add to `src/backend/schemas.py`:
  - `GroceryStoreCreate`: `name: str`, `description: str`
  - `GroceryStoreUpdate`: `name: str | None`, `description: str | None`
  - `GroceryStoreResponse`: `id: int`, `name: str`, `description: str`, `created_at: datetime`

### 3.2 List and Create - **🧪 NEW BEHAVIOR**
- [x] **Write test** - `src/backend/tests/test_grocery_store_api.py::test_list_grocery_stores_returns_seeded_default`
- [x] **Write test** - `test_create_grocery_store_returns_new_store_with_id`
- [x] **Write test** - `test_list_grocery_stores_ordered_by_created_at`
- [x] **Implement GET list** - `GET /api/config/grocery-stores` in `config_routes.py`
- [x] **Implement POST** - `POST /api/config/grocery-stores`

### 3.3 Read, Update, Delete - **🧪 NEW BEHAVIOR**
- [x] **Write test** - `test_get_grocery_store_by_id`
- [x] **Write test** - `test_get_grocery_store_not_found_returns_404`
- [x] **Write test** - `test_update_grocery_store_modifies_fields`
- [x] **Write test** - `test_delete_grocery_store_removes_record`
- [x] **Write test** - `test_delete_last_grocery_store_returns_400` (at least one must exist)
- [x] **Implement GET by id** - `GET /api/config/grocery-stores/{id}`
- [x] **Implement PUT** - `PUT /api/config/grocery-stores/{id}`
- [x] **Implement DELETE** - `DELETE /api/config/grocery-stores/{id}` with last-store validation

---

## Task 4: Settings Page UI (TIP Phase 4)
**Goal**: Frontend settings page with all configuration sections
**TIP Context**: Phase 4 - depends on Phases 2 & 3 APIs

### 4.1 Settings Route Setup - **🏗️ SETUP ONLY**
- [ ] **Create settings route** - `src/frontend/src/routes/settings/+page.svelte` with basic structure
- [ ] **Add navigation** - Link from main page to `/settings` (button or link in header area)
- [ ] **Page layout** - Three sections with headers: "Household Profile", "Pantry", "Grocery Stores"

### 4.2 Singleton Config Components - **🧪 NEW BEHAVIOR**
- [ ] **Create ConfigTextArea component** - `src/frontend/src/lib/components/ConfigTextArea.svelte`
  - Props: `label: string`, `apiEndpoint: string`, `initialContent: string`
  - Features: text area, save button, loading/success/error states
- [ ] **Write component test** - `src/frontend/src/lib/components/ConfigTextArea.svelte.test.ts`
  - Test: renders with initial content
  - Test: save button calls API and shows success feedback
- [ ] **Integrate HouseholdProfile** - Use ConfigTextArea with `/api/config/household-profile`
- [ ] **Integrate Pantry** - Use ConfigTextArea with `/api/config/pantry`

### 4.3 Grocery Store Table - **🧪 NEW BEHAVIOR**
- [ ] **Create GroceryStoreTable component** - `src/frontend/src/lib/components/GroceryStoreTable.svelte`
  - Features: table view, add button, inline edit, delete with confirmation
  - Svelte 5 runes for state management
- [ ] **Write component test** - `src/frontend/src/lib/components/GroceryStoreTable.svelte.test.ts`
  - Test: renders list of stores
  - Test: add button opens form
  - Test: delete shows confirmation
- [ ] **Load stores on mount** - Fetch from `/api/config/grocery-stores`
- [ ] **Add store flow** - Form with name/description, POST to API
- [ ] **Edit store flow** - Inline editing or modal, PUT to API
- [ ] **Delete store flow** - Confirmation dialog, DELETE to API, handle last-store error

### 4.4 Settings Page Integration - **🧪 NEW BEHAVIOR**
- [ ] **Write page test** - `src/frontend/src/routes/settings/page.svelte.test.ts`
  - Test: page renders all three sections
  - Test: back navigation works
- [ ] **Load initial data** - Fetch household profile, pantry, and grocery stores on mount
- [ ] **Error handling** - Show error states if API calls fail
- [ ] **Back navigation** - "Back to Home" link/button

---

## Task 5: Scaffolding Removal (TIP Phase 5)
**Goal**: Clean up demo code after real features work
**TIP Context**: Phase 5 - do last, depends on Phases 2-4

### 5.1 Backend Cleanup - **🔄 REFACTOR**
- [ ] **Remove dishes endpoints** - Delete lines 23-40 in `src/backend/routes.py` (dishes and dishes/stream)
- [ ] **Remove hello endpoint** - Delete lines 14-20 in `src/backend/routes.py`
- [ ] **Remove baml_functions import** - Remove `from baml_functions import get_dishes, stream_dishes` from routes.py
- [ ] **Delete baml_functions.py** - Remove `src/backend/baml_functions.py` entirely
- [ ] **Delete dishes.baml** - Remove `src/backend/baml_src/dishes.baml`
- [ ] **Regenerate BAML client** - Run `cd src/backend && uv run baml-cli generate`

### 5.2 Frontend Cleanup - **🔄 REFACTOR**
- [ ] **Replace main page** - Update `src/frontend/src/routes/+page.svelte` with:
  - Welcome message: "Harvest Hound - Meal Planning for CSA Deliveries"
  - Link to settings: "Get started by configuring your settings"
  - Placeholder for future features
- [ ] **Remove demo interfaces** - Remove Dish interface and related state from main page

### 5.3 Verification - **🧪 NEW BEHAVIOR**
- [ ] **Write smoke test** - `src/backend/tests/test_smoke.py::test_app_starts_and_serves_frontend`
  - Verify app starts without errors
  - Verify `/` returns HTML
  - Verify `/api/config/household-profile` returns 200
- [ ] **Manual verification** - Start app, visit settings, save config, refresh to confirm persistence

---

## Success Criteria for Implementation

- [ ] All tasks completed and marked as done
- [ ] All tests passing: `cd src/backend && uv run pytest`
- [ ] Frontend builds: `cd src/frontend && npm run build`
- [ ] Pre-commit passes: `pre-commit run --all-files`
- [ ] Manual smoke test: settings page loads, saves work, persists across refresh
- [ ] Scaffolding removed: `/api/dishes` returns 404, `/api/hello` returns 404

**Implementation Note**: Tasks may be reordered, skipped, or added during implementation as reality requires. This task plan is a guide, not a script. Use `implement-tasks` to begin implementation.
