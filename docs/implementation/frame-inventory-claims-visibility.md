# Feature Frame: Inventory Claims Visibility

**Date**: 2025-12-13
**Status**: Draft - Awaiting Alignment

---

## Problem Statement

Users need to see which inventory ingredients are claimed by planned recipes and which remain available, to avoid waste and understand why certain ingredients aren't appearing in new pitch generation. Without this visibility, users forget about planned meals that have reserved ingredients, leading to confusion ("why no radish recipes?") and missed opportunities ("oh, beets are unclaimed - I'll roast them as a side").

**From Prototype Discovery**:
- [x] **Ingredient claim visibility** (LEARNINGS.md:533): "Need to see what's claimed vs available" - Essential use case validated
- [x] **Inventory management table view** (LEARNINGS.md:650): Table structure exists, needs claims integration
- [x] **Claims data exists** (LEARNINGS.md:464): Backend already tracks recipe_id → inventory_item → quantity

---

## User Stories

### Story 1: See available quantities for meal planning
**As a** meal planner
**I want** to see how much of each ingredient is available vs claimed
**So that** I can identify spare ingredients to use ("1 lb spare carrots - Emily will eat those for lunch, should get more")

**Acceptance Criteria**:
- [ ] Inventory table has separate "Available" column (distinct from editable "Quantity" column)
- [ ] Available quantity = physical quantity - reserved claims
- [ ] When fully claimed, shows "0" or "Fully claimed"
- [ ] When partially claimed, shows specific available amount (e.g., "1 lb")
- [ ] When unclaimed, shows full quantity as available

**From LEARNINGS.md**: Lines 533-539 (claim visibility use cases), lines 650-657 (table view needs)

### Story 2: Filter for unclaimed ingredients
**As a** meal planner
**I want** to filter inventory to show only unclaimed ingredients
**So that** I can quickly identify what's going unused this week ("beets unclaimed - roast as side")

**Acceptance Criteria**:
- [ ] Dropdown menu above table for claim status filter
- [ ] Filter options: "All" (default), "Unclaimed only", "Claimed only"
- [ ] "Unclaimed only" hides fully claimed ingredients (shows only ingredients with available quantity > 0)
- [ ] "Claimed only" shows ingredients with ≥1 claim
- [ ] Filter state persists during session (not across page reloads)

**From LEARNINGS.md**: Lines 533-539 (UC2: "What's going unused?")

### Story 3: Navigate to recipes claiming an ingredient
**As a** meal planner
**I want** to click an ingredient and see which recipes are claiming it
**So that** I can review/abandon recipes if plans change ("used all broccoli, need to abandon that recipe")

**Acceptance Criteria**:
- [ ] New "Claimed By" column shows list of recipe names claiming this ingredient
- [ ] Each recipe name is a clickable link to that recipe's detail page
- [ ] If unclaimed, column shows "—" or "Unclaimed"
- [ ] Links include claimed quantity context (e.g., "Pot Roast (1 lb)")
- [ ] Recipe detail page has abandon action (already exists)
- [ ] No breadcrumb navigation needed (user can use browser back)

**From LEARNINGS.md**: Lines 533-539 (bidirectional lookup needed)

---

## Prototype Contrast

| Aspect | Prototype | MVP | Why Change |
|--------|-----------|-----|------------|
| Claims visibility | None - claims work invisibly | Show available qty + filter + recipe links | User confusion about why ingredients not appearing in pitches (LEARNINGS.md:533) |
| Inventory table | Basic table with quantity/priority/actions | Add "Available" column + claim status | Table structure exists, need claims integration (LEARNINGS.md:650) |
| Recipe navigation | N/A | Direct link from ingredient to recipe detail | User wants context before abandoning ("forgot I planned that") |

**Preserve from Prototype**:
- Table structure with inline editing (quantity, priority)
- Priority-based sorting
- Optimistic updates for edits

**Fix from Prototype**:
- Add claims visibility (currently invisible)
- Add filtering capability (currently shows all items)

**Change from Prototype**:
- New "Available" column showing physical qty - reserved claims
- New filter control for claim status
- Clickable claim indicator linking to recipe detail page

---

## Out of Scope (Deferred)

Explicitly NOT part of this feature:

- **Location filtering**: Deferred per user decision - audit use case ("verify chest freezer") not priority
- **Quick generation for unclaimed ingredients**: Great future feature idea - "generate side dishes from unclaimed beets" - captured for later
- **Inline recipe details**: User wants full recipe detail page for context, not modal/popover
- **Breadcrumb navigation**: User OK using browser back button
- **Claim amount breakdown per recipe**: Show aggregate available, not per-recipe detail inline (can see on recipe detail page)

**Future Features This Enables**:
- Location-based filtering for inventory audit
- Quick action: "Generate side dishes from unclaimed ingredients" button
- Shopping list adjustments based on available vs needed quantities

---

## Open Risks

**None identified** - data model exists, UI pattern established, scope is constrained.

---

## Alignment Decisions

**Resolved** - Ready for technical planning:

1. **Available quantity display**: ✅ Separate column - keeps "Quantity" column editable for actuals
2. **Multiple recipes claiming same ingredient**: ✅ List recipe names with links to each recipe detail page (adjust later if becomes cumbersome with 5+ recipes)
3. **Filter placement**: ✅ Dropdown menu above table
4. **Fully claimed ingredients**: ✅ Hidden when "Unclaimed only" filter active
