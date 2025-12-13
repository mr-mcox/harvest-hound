---
date: 2025-12-12
feature: inventory-editing
status: draft
frame: .scratch/frame-inventory-editing.md
estimated_effort: M
confidence: High
tags: [inventory, crud, ui-table]
---

# Technical Implementation Plan: Inventory Editing

## Context

**Problem Statement**: Users can import ingredients via bulk parse but cannot manage their inventory after import. Need to delete spoiled/confusing items, adjust quantities as items are consumed outside the app (roasting potatoes for tonight), and update priorities as expiration approaches (black radish won't last much longer).

**User Stories** (all essential):
1. Delete inventory items (soft-delete for FK integrity with IngredientClaim)
2. Adjust item quantities inline (reflect consumption outside app)
3. Update item priorities (bump urgency as expiration approaches)

**Key Acceptance Criteria** (TDD seeds):
- Inline editing with minimal friction (fewest clicks possible)
- Auto-save on blur/enter (quantity) and on change (priority)
- Soft delete pattern preserves FK integrity
- Items with quantity = 0 hidden from view
- Click-to-edit for priority (clean UI, no always-visible dropdown)
- Minimal validation (server rejects quantity <= 0, client snaps back)

**Scope Boundaries**:
- **In scope**: Delete, quantity editing, priority editing on saved inventory items
- **Out of scope**: Location field, claim visibility, sorting/filtering UI, portioning-aware UX, bulk operations

**Relevant Prototype Patterns**:
- Backend model: `prototype/app.py:36-45` - InventoryItem flat structure
- API endpoints: `prototype/app.py:298-407` - RESTful CRUD patterns
- Priority system: Four-tier (low/medium/high/urgent) with color-coding
- Bulk import: `prototype/baml_src/inventory.baml` - Works great, preserve as-is
- UI: Vanilla JS with priority badges and color-coded borders

**Key Learnings**:
- Delete heavily used during import cleanup (LEARNINGS.md:279)
- Cycling badge UX problem: item disappears when clicked in sorted list (LEARNINGS.md:639-640)
- Flat view with priority reduces cognitive load (LEARNINGS.md:329-333)
- 60% of actual inventory already feels long, need table structure (LEARNINGS.md:653-657)

---

## Implementation Phases

### Phase 1: Soft Delete Pattern ✓

**Purpose**: Enable safe deletion that preserves foreign key integrity with IngredientClaim table.

**Scope**: Backend migration and API update

**TDD Focus**:
- Acceptance: "Deleted items are soft-deleted (preserves FK integrity with claims)"
- Test approach: Integration tests verifying deleted_at behavior and FK integrity

**Key Considerations**:
- Single migration adds `deleted_at: datetime | None` column to InventoryItem
- Update DELETE endpoint to set `deleted_at = now()` instead of removing row
- Update all GET endpoints to filter `WHERE deleted_at IS NULL`
- Verify claims on deleted items still exist (FK integrity maintained)

**Dependencies**: None (foundation for other phases)

**Complexity**: S

---

### Phase 2: Consolidated Update Endpoint

**Purpose**: Simplify API by consolidating separate quantity and priority update endpoints into single partial update endpoint.

**Scope**: Backend API refactoring

**TDD Focus**:
- Acceptance: "Editing quantity updates immediately" and "Changing priority updates immediately"
- Test approach: API integration tests for partial updates (quantity only, priority only, both)

**Key Considerations**:
- Merge `PATCH /inventory/{id}` (quantity) and `PATCH /inventory/{id}/priority` into single endpoint
- Support partial updates using Optional fields
- Validation: quantity > 0 (server rejects <= 0), priority in enum (low/medium/high/urgent)
- Simpler frontend integration (single API call for any update)

**Dependencies**: None (can run parallel to Phase 1)

**Complexity**: S

---

### Phase 3: Table Structure & Display

**Purpose**: Convert read-only list to table layout that supports inline editing and avoids painful rewrite later.

**Scope**: Frontend UI restructuring

**TDD Focus**:
- Acceptance: "Items with quantity = 0 are hidden from inventory view"
- Test approach: E2E tests for table rendering and filtering

**Key Considerations**:
- Table columns: Ingredient | Quantity | Unit | Priority | Portion Size | Actions
- Preserve priority color-coding from prototype (border + badge)
- Static display first (no editing controls yet)
- Filter items where quantity = 0 or deleted_at IS NOT NULL
- Sets up structure for deferred features (location, claims columns)

**Dependencies**: Phase 1 (soft delete filtering), Phase 2 (API ready)

**Complexity**: M

---

### Phase 4: Delete Action

**Purpose**: Enable users to remove spoiled/confusing inventory items with low friction.

**Scope**: Frontend delete action wired to soft delete API

**TDD Focus**:
- Acceptance: "Clicking delete removes item from inventory view immediately"
- Test approach: E2E test for delete action and optimistic UI update

**Key Considerations**:
- Trash icon in Actions column
- No confirmation dialog (soft delete is low risk, frame decision)
- Optimistic UI update (remove from table immediately)
- Error handling (restore item on API failure)
- DELETE API call to soft delete endpoint

**Dependencies**: Phase 1 (soft delete API), Phase 3 (table structure)

**Complexity**: XS

---

### Phase 5: Inline Quantity Editing

**Purpose**: Allow users to adjust quantities as items are consumed outside the app.

**Scope**: Frontend inline editing for quantity field

**TDD Focus**:
- Acceptance: "Quantity is inline-editable with minimal friction (fewest clicks possible)"
- Test approach: E2E test for click-to-edit, auto-save, validation

**Key Considerations**:
- Click-to-edit pattern (quantity displays as text, click to show input)
- Auto-save on blur/enter
- Minimal validation: server rejects quantity <= 0, client snaps back to previous value
- Optimistic update with rollback on error
- Number input (type="number", step="0.01" for decimals)

**Dependencies**: Phase 2 (consolidated PATCH API), Phase 3 (table structure)

**Complexity**: S

---

### Phase 6: Inline Priority Editing

**Purpose**: Allow users to bump urgency as items approach spoiling.

**Scope**: Frontend inline editing for priority field

**TDD Focus**:
- Acceptance: "No cycling behavior (explicit selection replaces cycling badge problem)"
- Test approach: E2E test for click-to-edit dropdown, auto-save, visual feedback

**Key Considerations**:
- Click-to-edit pattern (priority badge displays, click to show dropdown)
- Dropdown options: Low, Medium, High, Urgent
- Auto-save on change (selection triggers API call)
- Visual feedback (color update reflects new priority immediately)
- Optimistic update with rollback on error
- Avoids cycling badge problem from prototype (LEARNINGS.md:639-640)

**Dependencies**: Phase 2 (consolidated PATCH API), Phase 3 (table structure)

**Complexity**: S

---

## Sequencing Logic

**Why this order minimizes risk**:
1. Backend foundation first (Phases 1-2) enables frontend work without API blockers
2. Table structure (Phase 3) sets up UI foundation before adding interactions
3. Delete (Phase 4) is simplest interaction, validates table + API integration early
4. Quantity and priority editing (Phases 5-6) follow established patterns from Phase 4

**Where parallel work is possible**:
- Phase 1 and Phase 2 are independent (backend migration vs API refactoring)
- Phase 5 and Phase 6 use identical click-to-edit pattern (could implement simultaneously)

**Where dependencies constrain sequencing**:
- Phase 3 requires Phase 1 (soft delete filtering) and Phase 2 (API ready)
- Phases 4-6 all require Phase 3 (table structure must exist)

**How phases build on each other**:
- Phases 1-2: Backend foundation
- Phase 3: UI foundation
- Phases 4-6: Progressive enhancement of table interactions

---

## High-Level Test Strategy

**TDD throughout with red-green-refactor cycle per phase**:

**Phase 1 (Soft Delete)**:
- Integration tests: Verify deleted_at behavior, FK integrity with IngredientClaim
- Test: Delete item with claims → item soft-deleted, claims persist

**Phase 2 (Consolidated API)**:
- API integration tests: Partial updates (quantity only, priority only, both)
- Test: PATCH with quantity → updates quantity, priority unchanged
- Test: PATCH with invalid quantity (0, negative) → 400 error

**Phase 3 (Table Structure)**:
- E2E tests: Table rendering, column structure, filtering
- Test: Items with quantity = 0 hidden from view
- Test: Soft-deleted items hidden from view

**Phase 4 (Delete Action)**:
- E2E tests: Delete button click, optimistic update, error handling
- Test: Click trash → item removed immediately → API success → item stays removed
- Test: Click trash → API failure → item restored with error message

**Phase 5 (Quantity Editing)**:
- E2E tests: Click-to-edit, auto-save, validation, rollback
- Test: Click quantity → input appears → edit → blur → saves
- Test: Edit to invalid value → snaps back to previous value

**Phase 6 (Priority Editing)**:
- E2E tests: Click-to-edit dropdown, auto-save, visual feedback
- Test: Click priority → dropdown appears → select → saves with color update

**Key scenarios to validate** (from acceptance criteria):
- Soft delete preserves FK integrity (items with claims can be deleted)
- Inline editing has minimal friction (fewest clicks possible)
- Auto-save on blur/enter (quantity) and on change (priority)
- Items with quantity = 0 hidden from view
- Click-to-edit pattern works cleanly

---

## Integration Points

**Backend**:
- Database migration (add deleted_at column to InventoryItem)
- InventoryItem model (soft delete support)
- DELETE endpoint (soft delete instead of hard delete)
- PATCH endpoint (consolidated partial updates)
- GET endpoints (filter deleted items)

**Frontend**:
- Inventory list component (convert to table)
- Table structure (columns for ingredient, quantity, unit, priority, portion size, actions)
- Delete action (trash icon + API integration)
- Inline editing components (quantity input, priority dropdown)
- Optimistic updates (UI changes before API confirmation)

**Database**:
- Migration adds deleted_at column
- FK integrity with IngredientClaim table preserved

---

## Risk Assessment

**High risks with mitigation strategies**:
1. **Table UI restructure breaks existing workflows**
   - Mitigation: Preserve bulk import flow exactly as-is (frame specifies)
   - Mitigation: Use same priority color-coding from prototype
   - Contingency: Can roll back to list view if table causes issues

2. **Soft delete breaks queries elsewhere in app**
   - Mitigation: Update ALL GET endpoints to filter deleted_at IS NULL in Phase 1
   - Mitigation: Grep for InventoryItem queries to find all usages
   - Contingency: Add database index on deleted_at for performance

**Medium risks to watch**:
1. **Click-to-edit UX feels clunky on mobile**
   - Watch: User feedback on mobile interaction
   - No mitigation planned yet (defer to user testing)

2. **Optimistic updates confusing if API slow**
   - Watch: User feedback on update latency
   - Mitigation: Loading states if latency becomes issue

**Steering likelihood**: Low
- Clear acceptance criteria with aligned UX decisions
- Established patterns from prototype to follow
- Straightforward CRUD operations with no novel architecture

---

## Implementation Notes

**TDD**: Test-Driven Development throughout all phases
- Write failing test first (red)
- Implement minimum code to pass (green)
- Refactor for clarity (refactor)

**Prototype patterns to follow**:
- `prototype/app.py:298-407` - RESTful API endpoint patterns
- `prototype/app.py:36-45` - InventoryItem model structure
- Prototype priority color scheme (urgent=red, high=orange, medium=green, low=gray)
- Vanilla JS component patterns for click-to-edit

**Prototype patterns to change**:
- Cycling badge → click-to-edit dropdown (avoids disappearing item problem)
- Read-only list → editable table (supports inline actions)
- Hard delete → soft delete (preserves FK integrity)

**Quality gates**:
- All tests passing (unit, integration, E2E per phase)
- Pre-commit hooks pass (formatting, linting)
- Soft delete verified with FK integrity intact
- Table structure supports deferred features (location, claims columns ready to add)

**General guidance**:
- Minimal clicks for common operations (delete, quantity adjust, priority change)
- Optimistic updates for snappy UX (rollback on error)
- Click-to-edit pattern keeps UI clean (no always-visible form controls)
- Preserve bulk import flow exactly as-is (works great, don't break it)

---

## Overall Complexity Estimate

**Overall**: M (Moderate)

**Confidence**: High

**Justification**:
- **Pattern novelty**: Low - follows established CRUD patterns from prototype
- **Decision density**: Low - feature frame has aligned UX decisions, clear acceptance criteria
- **Context coordination**: Moderate - backend + frontend + migration coordination
- **Integration points**: Moderate - 6 backend changes, table UI restructure, 3 inline editing interactions
- **Steering needs**: Low - clear requirements, no architectural uncertainty

**Main complexity drivers**:
1. UI restructure from list to table (Phase 3) - most significant change
2. Coordination across backend migration, API updates, and frontend (Phases 1-3)
3. Click-to-edit pattern implementation (Phases 5-6) - standard but needs care

**What keeps this Moderate vs Simple**:
- Table UI restructure is non-trivial
- Multiple integration points (migration + API + UI)
- Need to preserve existing bulk import flow

**What prevents this from being Complex**:
- No novel patterns (prototype has similar CRUD operations)
- Clear acceptance criteria from aligned feature frame
- Straightforward soft delete pattern (well-established)
- No architectural decisions needed
