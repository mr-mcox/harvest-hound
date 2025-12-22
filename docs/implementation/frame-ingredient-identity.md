# Feature Frame: Ingredient Identity & Aggregation

**Date**: 2025-12-20
**Status**: Draft - Awaiting Alignment

---

## Problem Statement

When adding ingredients to inventory, duplicates create separate items instead of aggregating quantities. Adding "2 lb carrots" twice creates two inventory items with 2 lbs each, rather than one item with 4 lbs total. This makes it hard to track actual quantities and breaks long-term ingredient tracking. The current soft-delete model (`deleted_at`) also creates resurrection complexity when ingredients return in future deliveries.

**From Prototype Discovery**:
- ✅ BAML parsing already normalizes ingredients (singular, lowercase names; full unit names)
- ✅ Exact case-insensitive matching works well for claims
- ⚠️ No deduplication on insert - bulk save always creates new rows
- ⚠️ Soft delete requires resurrection logic when re-adding deleted ingredients

---

## User Stories

### Story 1: Aggregate duplicate ingredients on import
**As a** meal planner
**I want** duplicate ingredients to combine into a single inventory item with summed quantities
**So that** I can see actual total quantities and track ingredients accurately over time

**Acceptance Criteria**:
- [ ] Adding "2 lb carrots" when "3 lb carrots" exists → single item with 5 lbs total
- [ ] Adding "1 bunch kale" when "2 bunches kale" exists → single item with 3 bunches
- [ ] Different units create separate items ("2 lb carrots" vs "3 each carrots" → 2 items)
- [ ] Aggregation happens silently - no special UI notifications
- [ ] Existing priority is preserved (new ingredients don't change existing priority)
- [ ] Planned recipes using the ingredient still show correct available quantities

**From LEARNINGS.md**: BAML ExtractIngredients normalizes to singular/lowercase (line 381-392), providing consistent identity foundation.

### Story 2: Delete sets quantity to zero
**As a** meal planner
**I want** the delete button to set quantity to 0 instead of removing the ingredient
**So that** the next time I get that ingredient, it automatically aggregates without creating duplicates

**Acceptance Criteria**:
- [ ] Clicking delete on "3 lb carrots" → item shows 0 lb carrots
- [ ] Inventory list doesn't show zero-quantity items (filtered out)
- [ ] Adding "2 lb carrots" when "0 lb carrots" exists → item shows 2 lb carrots (increments from 0)
- [ ] Planned recipes keep their claims even when ingredient is at 0 quantity
- [ ] Recipes show as impossible/insufficient when ingredient quantity is 0

**From LEARNINGS.md**: Inventory editing heavily used (line 274-278), simplified lifecycle reduces cognitive load.

### Story 3: Database migration for identity enforcement
**As a** developer
**I want** the database schema updated to enforce ingredient identity
**So that** duplicate ingredients are prevented at the database level

**Acceptance Criteria**:
- [ ] Migration adds unique constraint on (ingredient_name, unit)
- [ ] Migration removes deleted_at column
- [ ] Existing duplicate ingredients are identified and merged before migration runs
- [ ] Migration runs successfully on both dev.db and harvest.db
- [ ] All existing tests pass after migration

**From MVP-CHARTER.md**: Alembic migrations in place (line 137), acceptable to handle bad data manually for hobby project.

---

## Prototype Contrast

| Aspect | Prototype | MVP | Why Change |
|--------|-----------|-----|------------|
| Duplicate handling | Always creates new item | Upsert: aggregate if (name, unit) exists | Tracks actual quantities, prevents duplicate clutter |
| Ingredient identity | Auto-increment ID only | ID (PK) + UNIQUE(ingredient_name, unit) | Database enforces domain uniqueness |
| Delete mechanism | Soft delete (`deleted_at`) | Set `quantity = 0` | Simpler lifecycle, no resurrection logic |
| Claims on deleted items | Preserved by soft delete | Preserved, show negative available | Recipes stay planned even if ingredients gone |
| Inventory filtering | `WHERE deleted_at IS NULL` | `WHERE quantity > 0` | Aligns with quantity-based lifecycle |
| Normalization | BAML parses, no DB enforcement | BAML parses, DB unique constraint enforces | Domain integrity guaranteed |

**Preserve from Prototype**:
- BAML normalization (singular, lowercase, full unit names) - already works great
- Exact case-insensitive matching for claims (`match_ingredient_to_inventory()`)
- Simple string-based ingredient names (no complex embedding schemes)
- Bulk paste workflow (paste → parse → save)

**Fix from Prototype**:
- Duplicate items on re-import (aggregation missing)
- Soft delete resurrection complexity
- No database enforcement of ingredient uniqueness

**Change from Prototype**:
- Add UNIQUE constraint to enforce (ingredient_name, unit) identity
- Remove `deleted_at` field, use `quantity = 0` as lifecycle state
- Upsert logic in bulk save endpoint

---

## Out of Scope (Deferred)

Explicitly NOT part of this feature:
- **Unit conversion**: "1 lb" + "16 oz" stays as separate items (no automatic conversion)
  - Deferred because: Complex conversion logic, low ROI for MVP
  - Workaround: User manually adjusts or accepts separate items
- **Fuzzy name matching**: "carrot" vs "purple carrot" stays separate
  - Deferred because: BAML normalization already handles singular/plural, case
  - Workaround: User can manually merge via delete + quantity adjustment
- **Embedding-based similarity**: No AI matching for ingredient variations
  - Deferred because: Over-engineering, BAML normalization handles 95% of cases
- **Portion size aggregation**: "3x 16oz cans" + "2x 32oz cans" → "5 cans" (total portion sizes not summed)
  - Deferred because: Total quantity (48oz + 64oz) is sufficient for planning, not building auditable inventory
- **Migration of existing duplicates**: Assume fresh DB or manual cleanup
  - Deferred because: Dev.db and harvest.db currently empty (0 bytes)
  - If needed: Manual SQL to merge before applying constraint

**Future Features This Enables**:
- Long-term ingredient usage tracking (quantity deltas over time)
- "Ingredient history" view (quantities over weeks/months)
- Smart CSA ingredient predictions based on past deliveries

---

## Open Risks

**Database Migration Complexity**: Adding UNIQUE constraint requires handling existing duplicates

- **Risk**: If production DB has duplicate (name, unit) combos, migration fails
- **Mitigation**:
  - Check for duplicates before migration: `SELECT ingredient_name, unit, COUNT(*) FROM inventoryitem GROUP BY ingredient_name, unit HAVING COUNT(*) > 1`
  - Provide manual merge script if duplicates found
  - For MVP: Acceptable to require manual cleanup (small dataset)
- **Decision**: Proceed with constraint, document merge process in migration

**Claims on Zero-Quantity Items**: Users might be confused seeing recipes that need ingredients they deleted

- **Risk**: "I deleted carrots, why is Carrot Soup still planned?"
- **Mitigation**:
  - Inventory view shows available quantities (will be 0 or negative for impossible recipes)
  - Recipe validation warns about insufficient ingredients
  - Clear UI messaging: "This recipe needs 2 lb carrots (you have 0 lb)"
- **Decision**: Accept for MVP, improve messaging if confusion emerges in production use

