---
date: 2025-12-20
feature: ingredient-identity
status: draft
frame: .scratch/frame-ingredient-identity.md
estimated_effort: M
confidence: High
tags: [database, migration, inventory, data-integrity]
---

# TIP: Ingredient Identity & Aggregation

## Context

**Problem Statement**:
When adding ingredients to inventory, duplicates create separate items instead of aggregating quantities. Adding "2 lb carrots" twice creates two inventory items with 2 lbs each, rather than one item with 4 lbs total. This makes it hard to track actual quantities and breaks long-term ingredient tracking. The current soft-delete model (`deleted_at`) also creates resurrection complexity when ingredients return in future deliveries.

**User Stories**:
1. **Essential**: Aggregate duplicate ingredients on import - duplicate (name, unit) pairs should sum quantities
2. **Essential**: Delete sets quantity to zero - enables resurrection via aggregation, simpler lifecycle
3. **Essential**: Database migration enforces identity - UNIQUE(ingredient_name, unit) constraint

**Key Acceptance Criteria** (TDD Seeds):
- Adding "2 lb carrots" when "3 lb carrots" exists → single item with 5 lbs total
- Clicking delete on "3 lb carrots" → item shows 0 lb, filtered from inventory list
- Adding "2 lb carrots" when "0 lb carrots" exists → item shows 2 lb carrots
- Different units create separate items ("2 lb carrots" vs "3 each carrots" → 2 items)
- Planned recipes keep claims even when ingredient is at 0 quantity (show as insufficient)

**Scope Boundaries**:
- ✅ In scope: Aggregation by (name, unit), quantity-based lifecycle, UNIQUE constraint
- ❌ Out of scope: Unit conversion, fuzzy matching, embedding similarity, automatic duplicate migration

**Relevant Prototype Patterns**:

From `src/backend/models.py:68-79`:
- Current soft-delete model with `deleted_at` timestamp
- No UNIQUE constraint on (ingredient_name, unit)

From `src/backend/inventory_routes.py:56-84`:
- Bulk save is insert-only (no upsert logic)
- Parsing via BAML provides normalized ingredient names

From `src/backend/services.py:21-46`:
- Claim matching uses `ingredient_name.lower()` only (not unit-aware)
- Build inventory lookup: `{name.lower(): InventoryItem}`

**Key Learnings**:
- BAML normalization provides singular/lowercase/full-unit names (LEARNINGS.md:381-392)
- Inventory editing heavily used, delete action common (LEARNINGS.md:274-278)
- Claims must persist when ingredient deleted to preserve recipe planning (LEARNINGS.md:96-101)
- Exact case-insensitive matching works well for current use (LEARNINGS.md:13-17)

---

## Implementation Phases

### Phase 1: Pre-Migration Duplicate Cleanup ✓

**Purpose**: Investigate and manually clean existing duplicates before migration. Ensures UNIQUE constraint applies cleanly.

**Scope**: SQL query to detect duplicates, manual or scripted cleanup

**TDD Focus**:
- Write test with sample duplicate data
- Verify cleanup merges correctly (sum quantities, update FK references)
- Test approach: Integration test with test database

**Key Considerations**:
- Detection query: `SELECT ingredient_name, unit, COUNT(*) FROM inventoryitem GROUP BY ingredient_name, unit HAVING COUNT(*) > 1`
- Merge strategy: Sum quantities, keep oldest row, update claim FK references, delete duplicates
- Can be manual SQL if duplicate count is small (hobby project, small dataset)
- Backup harvest.db before cleanup

**Dependencies**: None (first phase)

**Complexity**: S

---

### Phase 2: Database Migration ✓

**Purpose**: Enforce ingredient identity at database level and transition from soft-delete to quantity-based lifecycle.

**Scope**: Alembic migration for schema changes

**TDD Focus**:
- Write migration test (apply + rollback on test database)
- Verify UNIQUE constraint prevents duplicate inserts
- Verify soft-deleted items converted to quantity=0
- Test approach: Run migration on copy of harvest.db, verify manually

**Key Considerations**:
- Backup harvest.db before migration (safety net for rollback)
- Migration steps in order:
  1. Set `quantity = 0` WHERE `deleted_at IS NOT NULL`
  2. Drop `deleted_at` column
  3. Add UNIQUE constraint on (ingredient_name, unit)
- Manual verification: Check inventory counts before/after, verify claims intact
- Rollback: Restore from backup if issues found

**Dependencies**: Phase 1 (duplicates cleaned)

**Complexity**: M

---

### Phase 3: Upsert Logic in Bulk Save ✓

**Purpose**: Enable automatic aggregation when adding ingredients. Transform bulk save from insert-only to intelligent upsert that sums quantities for existing (name, unit) pairs.

**Scope**: Backend API endpoint, SQLAlchemy upsert pattern

**TDD Focus** (write tests FIRST):
- Test: Adding duplicate (name, unit) increments existing quantity
- Test: Different units create separate items
- Test: Existing priority preserved (new ingredients don't change priority)
- Then implement upsert logic to make tests pass

**Key Considerations**:
- SQLAlchemy upsert pattern: Check if (name, unit) exists, then INSERT or UPDATE
- Query: `SELECT * FROM inventoryitem WHERE ingredient_name = ? AND unit = ? AND quantity > 0`
- If exists: `UPDATE quantity = quantity + new_quantity`
- If not exists: `INSERT new row`
- Preserve existing `priority`, `portion_size`, `store_id` on upsert
- Transaction safety: All upserts in single commit

**Dependencies**: Phase 2 (UNIQUE constraint must exist)

**Complexity**: M

---

### Phase 4: Unit-Aware Claim Matching ✓

**Purpose**: Update claim matching to consider both ingredient name AND unit, preventing impossible claims from being created. Currently matches by name only, which breaks with UNIQUE(name, unit) constraint.

**Scope**: Backend services, claim creation logic, inventory lookup

**TDD Focus** (write tests FIRST):
- Test: Claims match on both name and unit
- Test: "2 lb carrots" doesn't match "3 each carrots" inventory item
- Test: Unit mismatch prevents claim creation
- Then update matching logic to make tests pass

**Key Considerations**:
- Current: `build_inventory_lookup()` uses `{name.lower(): InventoryItem}`
- Updated: Use `{(name.lower(), unit): InventoryItem}` as key
- Update `match_ingredient_to_inventory()` to accept unit parameter
- Update all callers to pass unit alongside name
- Pitch validation already checks unit mismatch (services.py:228-230) - this aligns with that

**Dependencies**: None (can happen anytime, but logically after migration)

**Complexity**: S

---

### Phase 5: Delete Sets Quantity to Zero ✓

**Purpose**: Replace soft-delete with quantity-based lifecycle. Simpler model that enables automatic aggregation on re-import.

**Scope**: Backend delete endpoint, lifecycle logic

**TDD Focus** (write tests FIRST):
- Test: Delete sets `quantity = 0` (not `deleted_at`)
- Test: Zero-quantity items filtered from inventory list
- Test: Re-adding increments from 0 (aggregation works)
- Test: Edge case - negative available quantities when claims exceed inventory
- Then update delete endpoint and filtering to make tests pass

**Key Considerations**:
- Change `DELETE /inventory/{item_id}` endpoint: `item.quantity = 0` instead of `item.deleted_at = now()`
- Update list filtering: `WHERE quantity > 0` instead of `WHERE deleted_at IS NULL`
- Claims preserved on zero-quantity items (FK still valid)
- Recipes show as "insufficient inventory" when ingredient at 0

**Dependencies**: Phase 2 (deleted_at column removed)

**Complexity**: S

---

### Phase 6: Frontend Filtering & Display

**Purpose**: Update UI to reflect quantity-based lifecycle and show zero-quantity items appropriately in different contexts.

**Scope**: Frontend inventory list, recipe validation UI

**TDD Focus** (write tests FIRST):
- Test: Inventory list excludes zero-quantity items
- Test: Recipes with insufficient ingredients show clear messaging
- Test: Available quantity calculation respects claims
- Test: E2E flow - delete → list updates → re-add → aggregates
- Then update UI components to make tests pass

**Key Considerations**:
- Update inventory API query to filter `quantity > 0`
- Recipe validation UI: "This recipe needs 2 lb carrots (you have 0 lb available)"
- Available quantity can be negative if claims exceed inventory
- No special "deleted" state in UI (quantity is source of truth)

**Dependencies**: Phase 5 (delete logic changed)

**Complexity**: S

---

## Sequencing Logic

**Why this order minimizes risk**:
1. **Phase 1 before Phase 2**: Must clean duplicates before adding UNIQUE constraint (prevents migration failure)
2. **Phase 2 before Phase 3**: Upsert logic depends on UNIQUE constraint existing
3. **Phase 2 before Phase 5**: Can't remove deleted_at until column is gone
4. **Phase 5 before Phase 6**: Frontend filtering depends on backend lifecycle change
5. **Phase 7 last**: Validates complete implementation

**Where parallel work is possible**:
- Phase 4 (unit-aware matching) can happen anytime after Phase 2 (doesn't depend on other phases)
- Test writing can start early, run after implementation

**Critical path**: Phase 1 → Phase 2 → Phase 3/5 → Phase 6

**TDD applied throughout**: Each phase (except migration) follows red-green-refactor - write failing tests first, implement to pass, refactor for clarity

---

## High-Level Test Strategy (TDD Throughout)

**Red-Green-Refactor cycle**:
- Each phase: Write failing tests FIRST (red)
- Implement minimum code to pass tests (green)
- Refactor for clarity and maintainability

**Test types by phase**:
- **Phase 1**: Integration test with sample duplicate data
- **Phase 2**: Migration test (apply + rollback on test DB copy)
- **Phase 3**: Unit tests for upsert logic, API integration tests
- **Phase 4**: Unit tests for matching logic
- **Phase 5**: Unit + integration tests for delete endpoint, edge case tests for negative quantities
- **Phase 6**: E2E tests for UI filtering and messaging

**Core test scenarios** (from acceptance criteria):
1. Aggregate on import: "2 lb carrots" + "3 lb carrots" → "5 lb carrots" total
2. Zero-quantity lifecycle: Delete → 0 lb → re-add → increments from 0
3. Unit separation: "2 lb carrots" vs "3 each carrots" → separate items
4. Claim persistence: Recipe keeps claim when ingredient deleted (shows insufficient inventory)
5. Edge case: Claims exceed inventory → negative available quantity

---

## Integration Points

**Backend**:
- Database schema (models.py) - add UNIQUE constraint, remove deleted_at
- Inventory routes (inventory_routes.py) - upsert bulk save, quantity-based delete
- Services (services.py) - unit-aware claim matching
- Shopping list (shopping_list.py) - may need unit-aware aggregation

**Frontend**:
- Inventory list component - filter quantity > 0
- Recipe validation UI - show insufficient inventory messaging
- Available quantity display - handle negative values

**Database**:
- Alembic migration - schema changes, data transformation
- Cleanup script - pre-migration duplicate merging

**BAML**:
- No changes needed - normalization already provides consistent identity foundation

---

## Risk Assessment

**Medium Risk: Migration with Production Data**
- **Risk**: Existing duplicates cause UNIQUE constraint violation, migration fails
- **Mitigation**:
  - Phase 1 detects and cleans duplicates before migration
  - Backup harvest.db before migration (safety net for rollback)
  - Test migration on copy of harvest.db first
  - Manual verification after migration (check counts, verify claims intact)
- **Contingency**: Restore from backup, fix issues manually, retry
- **Steering likelihood**: Low - small dataset (hobby project), manual cleanup acceptable

**Low Risk: Claim FK Updates During Duplicate Merge**
- **Risk**: Claims reference InventoryItem IDs being deleted during merge
- **Mitigation**:
  - Phase 1 cleanup updates claim FK references before deleting duplicates
  - Transaction atomicity ensures consistency
- **Contingency**: Manual SQL to fix FK references if needed
- **Steering likelihood**: Low - straightforward logic with test coverage

**Low Risk: Zero-Quantity Display Confusion**
- **Risk**: Users confused by recipes showing claimed ingredients they "deleted"
- **Mitigation**:
  - Clear UI messaging: "This recipe needs 2 lb carrots (you have 0 lb available)"
  - Inventory list filters out zero-quantity items
  - Recipe validation shows insufficient inventory warning
- **Contingency**: Improve messaging based on user feedback
- **Steering likelihood**: Low - acceptance criteria define expected behavior clearly

---

## Implementation Notes

**TDD**: Test-Driven Development throughout all phases
- Write acceptance criteria as failing tests first
- Implement minimum code to pass tests
- Refactor for clarity and maintainability
- Each phase has specific test approach defined

**Prototype Patterns to Follow**:
- BAML normalization for ingredient identity (models.py:68-79, LEARNINGS.md:381-392)
- Atomic transactions for claim creation (services.py:66-123) - use `session.flush()` pattern
- Soft-delete FK preservation approach (inventory_routes.py) - inspires zero-quantity preservation
- Exact case-insensitive matching (services.py:21-46) - extend to unit-aware matching

**Prototype Patterns to Change**:
- Insert-only bulk save → intelligent upsert (inventory_routes.py:56-84)
- Name-only claim matching → (name, unit) matching (services.py:21-46)
- Soft delete → quantity-based lifecycle (inventory_routes.py delete endpoint)
- deleted_at filtering → quantity > 0 filtering (all list endpoints)

**Quality Gates**:
- All acceptance criteria tests pass
- Migration applies cleanly on test database
- No orphaned claims after duplicate merge
- Regression tests pass (existing functionality preserved)
- Manual testing: Add duplicates → verify aggregation, delete → verify zero-quantity → re-add → verify increment

---

## Overall Complexity Estimate

**T-shirt size**: M (Moderate)

**Confidence**: High

**Justification**:
- **Database migration**: Straightforward with backup safety net and manual verification (medium complexity)
- **Multiple integration points**: Backend API, frontend UI, database schema, claim logic (medium complexity)
- **Novel patterns**: Upsert logic not in prototype, but SQLAlchemy pattern is standard (low-medium complexity)
- **Clear acceptance criteria**: Well-defined user stories and test scenarios (reduces complexity)
- **TDD approach**: Tests first reduce implementation uncertainty and rework (reduces complexity)
- **Small dataset**: Hobby project with manageable data size makes cleanup practical (reduces complexity)

**Overall**: Moderate complexity due to multiple integration points and novel upsert pattern, but well-scoped with clear test strategy and safety nets (backup, manual verification). High confidence because approach is straightforward and risks are mitigated.

---

## Next Step

Use `implement-tasks "docs/development/tips/tip-ingredient-identity.md"` to begin phase-by-phase implementation with just-in-time tactical planning.
