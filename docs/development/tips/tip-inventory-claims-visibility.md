---
date: 2025-12-13
feature: inventory-claims-visibility
status: draft
frame: .scratch/frame-inventory-claims-visibility.md
estimated_effort: M
confidence: High
tags: [inventory, claims, ui, table-enhancement]
---

# TIP: Inventory Claims Visibility

## Context

**Problem Statement**:
Users need to see which inventory ingredients are claimed by planned recipes and which remain available, to avoid waste and understand why certain ingredients aren't appearing in new pitch generation. Without this visibility, users forget about planned meals that have reserved ingredients, leading to confusion ("why no radish recipes?") and missed opportunities ("oh, beets are unclaimed - I'll roast them as a side").

**User Stories** (from feature frame):

**Essential**:
1. **See available quantities for meal planning** - Inventory table shows available column (physical - reserved) to identify spare ingredients
2. **Filter for unclaimed ingredients** - Dropdown filter to quickly find what's going unused this week
3. **Navigate to recipes claiming an ingredient** - Click ingredient to see which recipes are reserving it, with links to recipe detail page for review/abandon

**Acceptance Criteria** (TDD seeds):
- Available quantity column showing physical qty - reserved claims
- Filter dropdown with "All", "Unclaimed only", "Claimed only" options
- "Claimed By" column with clickable recipe name links (includes qty context)
- When unclaimed, shows "—" or "Unclaimed"
- When fully claimed, shows "0" or "Fully claimed"

**Scope Boundaries**:
- **In scope**: Claims visibility (available column, filter, recipe links)
- **Out of scope**: Location filtering (deferred), quick generation for unclaimed ingredients (future feature), inline recipe details (use detail page), breadcrumb navigation (browser back is fine)

**Relevant Prototype Patterns**:
- Inventory table structure: `src/frontend/src/routes/inventory/+page.svelte:214-316` - Clean table with inline editing, optimistic updates
- Claims calculation service: `src/backend/services.py:126-157` - `calculate_available_inventory()` already computes available = physical - reserved
- Claims model: `src/backend/models.py:181-192` - Links recipe_id → inventory_item_id → quantity with state tracking
- Optimistic update pattern: Inventory page lines 72-90, 103-141 - Immediate UI update with rollback on error

**Key Learnings**:
- LEARNINGS.md:533-539 - Essential use case validated: "Need to see what's claimed vs available"
- LEARNINGS.md:650-657 - Table view structure exists, needs claims integration
- LEARNINGS.md:464 - Backend already tracks claims data (recipe_id → inventory_item → quantity)
- Optimistic updates feel responsive and work well when implemented correctly

## Implementation Phases

### Phase 1: Backend Claims Aggregation Endpoint ✓

**Purpose**: Create API endpoint to return inventory items enriched with claims data, enabling frontend to display available quantities and claiming recipes. Sequenced first because frontend needs this data structure.

**Scope**: Backend API, database queries, error handling

**TDD Focus**:
- Acceptance criterion: Available quantity = physical quantity - reserved claims
- Test approach: Unit tests for endpoint, verify aggregation math, error scenarios

**Key Considerations**:
- Aggregate claims by inventory_item_id (multiple recipes can claim same ingredient)
- Include recipe name + quantity for each claim (enables "Claimed By" display)
- Return both physical and available quantities to frontend
- Filter to only RESERVED claims (exclude cooked/abandoned)
- Error handling: Database failures, malformed requests
- Performance: Add indexes on foreign keys if query is slow
- Edge case testing: No claims, deleted recipes with orphaned claims

**Dependencies**: None - first phase

**Complexity**: S

### Phase 2: Frontend Available Column ✓

**Purpose**: Add "Available" column to inventory table showing physical qty - reserved claims. Sequenced after Phase 1 because it requires aggregated data from backend.

**Scope**: Frontend UI, table structure, loading states, accessibility

**TDD Focus**:
- Acceptance criteria: Available column displays, shows correct values for unclaimed/partially/fully claimed
- Test approach: Component tests for rendering logic, edge cases, accessibility

**Key Considerations**:
- Keep existing "Quantity" column for editing physical inventory
- Display "0" or "Fully claimed" when available = 0
- Display specific amount when partially claimed (e.g., "1 lb")
- Display full quantity when unclaimed
- Visual polish: Column width, formatting/styling to distinguish from physical quantity
- Loading states: Show skeleton/spinner while fetching claims data
- Error handling: Backend failures, stale data (show error message, retry option)
- Responsive behavior: Column wrapping on mobile
- Accessibility: Screen reader announces available quantity, keyboard navigation
- Edge case testing: Zero inventory, no claims, all items fully claimed

**Dependencies**: Phase 1 (needs backend endpoint)

**Complexity**: S

### Phase 3: Claims Detail Column ✓

**Purpose**: Add "Claimed By" column showing which recipes are claiming each ingredient, with clickable links to recipe detail page. Enables user workflow of reviewing/abandoning recipes when plans change.

**Scope**: Frontend UI, routing, accessibility

**TDD Focus**:
- Acceptance criterion: Recipe names are clickable links, include claimed quantity context
- Test approach: Component tests for link rendering, E2E for navigation, accessibility

**Key Considerations**:
- Display recipe name + claimed quantity (e.g., "Pot Roast (1 lb)")
- Multiple recipes claiming same ingredient → list all with quantities
- Links navigate to existing `/recipes/{id}` detail page
- Show "—" or "Unclaimed" when no claims
- Visual polish: Handle long recipe names or many claims gracefully (truncate, collapse, or scroll)
- Responsive behavior: Column stacking on mobile
- Accessibility: Links have proper aria-labels, keyboard navigation works
- Edge case testing: 5+ recipes claiming same ingredient, recipe deleted but claims remain

**Dependencies**: Phase 2 (builds on table structure)

**Complexity**: S

### Phase 4: Claim Status Filter & E2E Validation ✓

**Purpose**: Add dropdown filter above table to show all/unclaimed/claimed ingredients. Enables quick discovery of unused ingredients. Validate complete workflow across all features. Sequenced last after all display features are working.

**Scope**: Frontend UI, state management, E2E workflow testing

**TDD Focus**:
- Acceptance criterion: Filter options work correctly, state persists during session
- Test approach: Component tests for filtering logic, E2E tests for complete workflows

**Key Considerations**:
- Filter options: "All" (default), "Unclaimed only", "Claimed only"
- "Unclaimed only" = ingredients with available quantity > 0
- "Claimed only" = ingredients with ≥1 claim
- Session persistence (not across page reloads)
- Filter interacts with existing priority sorting
- Filter placement above table (consistent with UI patterns)
- Visual polish: Dropdown styling, clear labels
- Accessibility: Keyboard navigation, screen reader announces filter changes
- E2E workflow validation: View available → filter unclaimed → click recipe link → abandon → verify availability updates and filter reflects change
- Performance testing: 50+ inventory items with multiple claims per item
- Final manual QA: Complete walkthrough with real CSA data

**Dependencies**: Phase 3 (all display features must be complete)

**Complexity**: S


## Sequencing Logic

**Why this order minimizes risk**:
1. Backend first establishes stable data contract for frontend
2. Display columns before filtering reduces complexity (see data working before adding filters)
3. Available column before "Claimed By" column enables iterative testing (math first, then links)
4. Filter last because it operates on completed display structure (includes E2E validation once all features are working)

**Parallel work opportunities**:
- Phase 2 & 3 could potentially overlap (both are frontend table columns), but sequential is cleaner for focused testing

**Dependencies**:
- Phase 1 → Phase 2 (backend data needed for display)
- Phase 2 → Phase 3 (table structure evolves incrementally)
- Phase 3 → Phase 4 (filter operates on display, E2E validates complete feature)

## High-Level Test Strategy

**TDD throughout with red-green-refactor cycle per phase**:

**Phase 1** (Backend):
- Unit tests for claims aggregation endpoint
- Verify correct calculation: available = physical - reserved
- Test multiple recipes claiming same ingredient
- Test edge cases: no claims, deleted recipes with orphaned claims
- Test error handling: database failures, malformed requests

**Phase 2** (Frontend - Available Column):
- Component tests for available quantity rendering
- Test display logic for unclaimed/partial/fully claimed states
- Verify correct data binding from backend response
- Test loading states and error handling
- Test responsive behavior on mobile
- Test accessibility (screen readers, keyboard navigation)
- Test edge cases: zero inventory, all items fully claimed

**Phase 3** (Frontend - Claimed By Column):
- Component tests for recipe link rendering
- Test multiple claiming recipes display
- E2E test for link navigation to recipe detail page
- Test responsive behavior (long names, many claims)
- Test accessibility (link labels, keyboard navigation)
- Test edge case: 5+ recipes claiming same ingredient

**Phase 4** (Frontend - Filter & E2E):
- Component tests for filter logic
- Test filter state persistence during session
- Verify filter interaction with sorting
- Test accessibility (keyboard navigation, screen reader announcements)
- E2E workflow tests: view available → filter unclaimed → click recipe link → abandon → verify updates
- Performance testing: 50+ inventory items with multiple claims
- Final manual QA with real CSA data

## Integration Points

**Backend**:
- New API endpoint: GET `/api/inventory/with-claims` (or enhance existing `/api/inventory`)
- Database queries: Join InventoryItem with IngredientClaim and Recipe tables
- Services: Leverage existing `calculate_available_inventory()` or similar aggregation logic

**Frontend**:
- Inventory page: `src/frontend/src/routes/inventory/+page.svelte`
- Enhance existing table structure (add columns)
- Add filter dropdown component above table
- Update TypeScript interfaces for enhanced InventoryItem response
- Routing: Link to existing `/recipes/[id]` route

**BAML**: Not applicable - no prompt changes needed

## Risk Assessment

**Low overall risk** - data model exists, UI pattern established, scope is constrained.

**Medium risks to watch**:
1. **Performance with many claims**: If user has 50+ inventory items each claimed by multiple recipes, aggregation query and UI rendering could slow down
   - Mitigation: Monitor query performance, add indexes if needed, consider pagination if inventory grows large

2. **Stale data after recipe state changes**: If recipe is cooked/abandoned, claims are deleted - UI must refresh to reflect availability change
   - Mitigation: Use optimistic updates or polling, consider WebSocket updates for real-time sync (post-MVP)

**Contingency plans**:
- If aggregation query is slow: Add database indexes on `inventory_item_id` and `recipe_id` foreign keys
- If many claims make UI cluttered: Collapse claims list by default, expand on click
- If filter logic becomes complex: Extract to separate Svelte component for testability

**Steering likelihood**: Low - straightforward CRUD enhancement with clear requirements and existing patterns to follow. Uncertainty areas:
- Filter UI placement/styling (user preference during review)
- "Claimed By" column formatting when 5+ recipes claim same ingredient (adjust if becomes issue)

## Implementation Notes

**TDD**: Test-Driven Development throughout all phases - write tests first, implement to pass, refactor for quality.

**Prototype patterns to follow**:
- Inventory table structure: `src/frontend/src/routes/inventory/+page.svelte:214-316`
- Optimistic update pattern: Lines 72-90, 103-141 (immediate UI update with rollback)
- Claims calculation: `src/backend/services.py:126-157` (`calculate_available_inventory()`)

**Prototype patterns to change**:
- Enhance inventory table with new columns (Available, Claimed By)
- Add filtering capability (currently shows all items without filters)

**Quality gates**:
- All tests passing (unit, component, E2E)
- Pre-commit hooks passing (linting, formatting)
- Manual QA: Complete workflow walkthrough with real data
- Accessibility audit: Keyboard navigation, screen reader compatibility

## Overall Complexity Estimate

**Overall**: M (Moderate)
**Confidence**: High

**Justification**:
- **Not XS/S** because it requires both backend (aggregation query) and frontend (table enhancement, filtering) changes across multiple phases
- **Not L/XL** because it leverages existing patterns extensively (table structure exists, claims calculation exists, routing exists)
- **Moderate complexity drivers**:
  - Backend aggregation logic (join multiple tables, calculate available quantities)
  - Frontend state management (filter state, claims data binding)
  - Integration points (backend ↔ frontend data contract)
  - Multiple user stories with distinct acceptance criteria
- **Low steering needs**: Requirements are clear from feature frame, existing patterns provide templates, architectural approach is straightforward
- **5 phases** reflect iterative delivery strategy, not inherent complexity - each phase is simple when isolated
