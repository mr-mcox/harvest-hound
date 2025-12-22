# Feature Frame: Inventory Editing

**Date**: 2025-12-12
**Status**: Draft - Awaiting Alignment

---

## Problem Statement

Users can import ingredients via bulk parse but cannot manage their inventory after import. Need to delete spoiled/confusing items, adjust quantities as items are consumed outside the app (roasting potatoes for tonight), and update priorities as expiration approaches (black radish won't last much longer).

**From Prototype Discovery**:
- Bulk import works great and is heavily used (LEARNINGS.md:268-278)
- Delete only exists on pending imports, not saved inventory
- No quantity or priority editing exists for saved inventory
- Current 60% of actual inventory already feels long (LEARNINGS.md:653-657)

---

## User Stories

### Story 1: Delete inventory items
**As a** meal planner
**I want** to delete inventory items
**So that** I can remove spoiled items or confusing entries that shouldn't be tracked

**Acceptance Criteria**:
- [ ] Each inventory item has a trash/delete action
- [ ] Clicking delete removes item from inventory view immediately
- [ ] Deleted items are soft-deleted (preserves FK integrity with claims)
- [ ] Items with quantity = 0 are hidden from inventory view

**From LEARNINGS.md**: Line 279-283 (Delete works great during import, heavily used for cleanup)

### Story 2: Adjust item quantities
**As a** meal planner
**I want** to adjust ingredient quantities inline
**So that** I can reflect consumption outside the app (roasted some potatoes, now have less)

**Acceptance Criteria**:
- [ ] Quantity is inline-editable with minimal friction (fewest clicks possible)
- [ ] Editing quantity updates immediately (auto-save on blur/enter)
- [ ] Quantity must be > 0 (enforced client & server - if want 0, must delete)
- [ ] Changes persist to database
- [ ] Simple number input sufficient (no portioning-aware UX needed for MVP)

**From LEARNINGS.md**: Line 279-283 (Update quantity "janky" for count-based items - needs better UX)

### Story 3: Update item priorities
**As a** meal planner
**I want** to explicitly set ingredient priority
**So that** I can bump urgency as items approach spoiling (black radish won't last long)

**Acceptance Criteria**:
- [ ] Each item has priority dropdown/select (Low, Medium, High, Urgent)
- [ ] Changing priority updates immediately (auto-save)
- [ ] Priority changes persist to database
- [ ] Visual feedback (color-coding) reflects new priority immediately
- [ ] No cycling behavior (explicit selection replaces cycling badge problem)

**From LEARNINGS.md**: Line 639-640 (Cycling badge UX problem - item disappears when clicked in sorted list)

---

## Prototype Contrast

| Aspect | Prototype | MVP | Why Change |
|--------|-----------|-----|------------|
| Delete | Only on pending imports | On saved inventory items | Can't remove spoiled/confusing items post-import |
| Quantity editing | None | Inline editable field | Need to reflect consumption outside app |
| Priority editing | None | Dropdown select per row | Need to adjust urgency as expiration approaches |
| View format | Simple read-only list | Editable table/list | Better structure for inline editing actions |
| Item visibility | All items shown | Hide quantity = 0 | Zero-quantity items are effectively deleted |
| Delete behavior | N/A (no delete) | Soft delete | Prevent FK constraint issues with IngredientClaim |

**Preserve from Prototype**:
- Priority color-coding (Urgent=error-500, High=warning-500, Medium=primary-500, Low=surface-500)
- Priority sorting (highest urgency first)
- Clean, simple UI (Skeleton components)
- Bulk import flow (works great, keep as-is)

**Fix from Prototype**:
- No editing capabilities on saved inventory
- No delete capability on saved inventory

**Change from Prototype**:
- Read-only list → Editable table/list with inline actions
- Add trash icon per row for delete
- Add inline quantity editing (minimize clicks)
- Add priority dropdown per row (explicit selection)
- Soft delete pattern for data safety

---

## Out of Scope (Deferred)

Explicitly NOT part of this feature:
- **Location field + filtering**: Deferred to separate frame (database migration + filtering not valuable until claims/locations exist)
- **Claim visibility**: Nice to have, deferred (LEARNINGS.md:99-101)
- **Sorting/filtering UI**: Deferred until filtering becomes valuable (claims/locations)
- **Portioning-aware editing UX**: Simple number input sufficient for MVP (LEARNINGS.md:17-23)
- **Bulk operations**: Single-item editing sufficient for small n (weekly CSA deliveries)
- **Location assignment**: Deferred to separate frame

**Future Features This Enables**:
- Location-based filtering (once location field added)
- Claim visibility in inventory table
- Ingredient audit workflows by location

---

## Technical Notes

**Soft Delete Pattern**:
- Add `deleted_at: datetime | None` to InventoryItem model (nullable)
- List endpoint filters `WHERE deleted_at IS NULL`
- Delete endpoint sets `deleted_at = now()`
- Preserves FK integrity with IngredientClaim table
- Migration required

**Validation**:
- Quantity > 0 enforced on PATCH (client validation + server validation)
- If user wants quantity = 0, must use DELETE action instead
- Priority must be one of: Low, Medium, High, Urgent

**API Additions Needed**:
- `DELETE /api/inventory/{id}` - Soft delete item (set deleted_at)
- `PATCH /api/inventory/{id}` - Update quantity and/or priority (partial update)

**Frontend Changes**:
- Enhanced list or table layout with inline actions
- Inline quantity input (type=number, min=0.01, auto-save on blur/enter)
- Priority dropdown/select per row (auto-save on change)
- Trash icon per row (confirm dialog optional - delete is soft, low risk)

---

## UX Decisions (Aligned)

**Layout**: Table view with columns (Ingredient | Quantity | Unit | Priority | Portion Size | Actions)
- Rationale: Avoid painful rewrite later, sets up structure for deferred features (location, claims)
- Future features naturally add as columns

**Quantity Editing**: Always-editable input field, auto-save on blur/enter
- Minimal friction (no click-to-edit step)
- Immediate feedback

**Priority Selection**: Simplest implementation (always-visible dropdown/select)
- Auto-save on change

**Delete Confirmation**: Trust soft-delete (no confirmation dialog)
- Low risk, items can be restored from database if needed
- Reduces friction

---

## Next Steps

Feature frame aligned! Ready for technical planning with `create-tip inventory-editing`.
