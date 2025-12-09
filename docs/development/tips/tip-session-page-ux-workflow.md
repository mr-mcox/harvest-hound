---
date: 2025-12-08
feature: session-page-ux-workflow
status: draft
frame: .scratch/frame-session-page-ux-workflow.md
estimated_effort: M
confidence: High
tags: [ux, recipe-planning, pitch-invalidation, workflow-optimization]
---

# Technical Implementation Plan: Session Page UX & Workflow Reorganization

## Context

**Problem Statement**: The session page mixes three distinct jobs-to-be-done (planning meals, cooking tonight's recipe, shopping) into a single view, creating UX problems: (1) pitches using claimed ingredients remain visible, creating invalid options, (2) "Generate Pitches" creates duplicates instead of calculating needed count, (3) full recipe details dominate vertical space, making pitch selection difficult.

**User Stories**:
- **Story 1 (Essential)**: Remove pitches that can't be made with remaining inventory (quantity-aware)
- **Story 2 (Essential)**: Smart manual pitch generation (only generate delta needed)
- **Story 3 (Essential)**: Compact recipe view with expandable detail page
- **Story 4 (Essential)**: Workflow-oriented page sections (plan/cook/shop)
- **Story 5 (Essential, droppable if complex)**: Render markdown in recipe instructions

**Key Acceptance Criteria (TDD Seeds)**:
- After fleshing out recipe, invalid pitches are removed from view (not grayed out)
- Generate Pitches calculates: 3x unfilled slots - valid pitches = delta to generate
- Fleshed-out recipes show compact cards, click navigates to `/recipes/{id}` route
- Session page organized into collapsible sections with workflow focus
- Recipe instructions render markdown formatting (bold, italics, inline code)

**Scope Boundaries**:
- **In scope**: Fix pitch invalidation bug, add smart generation, create recipe detail page, reorganize session page
- **Out of scope**: Bulk recipe operations, recipe editing after planning, mobile responsiveness, recipe library

**Relevant Patterns from Prototype & MVP**:
- `load_available_inventory()` (prototype `app.py:154-178`) - decremented inventory state calculation
- EventSource SSE streaming - MVP already implements this (`sessions/[id]/+page.svelte:250`)
- SvelteKit file-based routing - just create `src/frontend/src/routes/recipes/[id]/+page.svelte`
- Svelte 5 runes (`$state`, `$derived`) - MVP uses Svelte 5 reactive state
- Skeleton UI library - MVP uses for components and styling
- Criterion-grouped pitch display (MVP `sessions/[id]/+page.svelte:730-798`)

**Current MVP State to Change**:
- **Pitch invalidation**: Prototype grays out invalid pitches; MVP doesn't check validity at all yet
- **Generate count**: Hardcoded count per criterion (slots * 3); need smart calculation based on valid pitches
- **Recipe display**: Full details shown inline (lines 509-579); need compact cards + detail route
- **Page organization**: Flat sections; need collapsible workflow-oriented hierarchy

**Key Learnings**:
- LEARNINGS.md #287-290: User explicitly requested pitch removal vs graying out
- LEARNINGS.md #292-297: Want consistent pool via manual backfill (not automatic)
- LEARNINGS.md #625-630: Different views for different contexts (planning vs cooking)
- LEARNINGS.md #409-418: LLM declares ingredients, code manages state (separation of concerns)
- LEARNINGS.md #676-681: Decremented inventory pattern enables multi-wave auto-pivot

**Open Risks**:
- **Unit mismatch handling**: Ingredient name matches but units differ (e.g., pitch needs "1 lb" but inventory has "2 acorn squash")
  - MVP approach: Aggressive invalidation (false negatives better than false positives)
  - Example: Different units (1 cup onion vs 2 onions) → invalidate pitch
- **Pitch regeneration using decremented inventory**: Already implemented in `load_available_inventory()` but needs validation

---

## Implementation Phases

### Phase 1: Quantity-Aware Pitch Invalidation ✓

**Purpose**: Remove pitches that can't be made with remaining inventory (not just gray them out). This fixes the core bug where invalid options pile up and confuse users.

**Scope**: Backend validation logic, frontend rendering changes

**TDD Focus**:
- Acceptance criterion: After fleshing out recipe, invalid pitches are removed from view
- Test approach: Unit tests for validation logic, integration test for end-to-end flow
- Key scenarios: Same units (straightforward subtraction), different units (aggressive invalidation), no inventory match

**Key Considerations**:
- Aggressive unit mismatch strategy: invalidate if ingredient name matches but units don't match
- False negatives (removing valid pitches) are acceptable, false positives (showing invalid) are not
- Case-insensitive ingredient name matching ("Black Radish" matches "black radish" claim)
- Validation must run after all concurrent flesh-outs complete to avoid race conditions

**Dependencies**: None (first phase)

**Complexity**: S

---

### Phase 2: Smart Manual Pitch Generation ✓

**Purpose**: Calculate exactly how many pitches to generate based on unfilled meal slots and currently valid pitches. Prevents duplication and maintains consistent pool size.

**Scope**: Backend calculation logic, frontend UI updates

**TDD Focus**:
- Acceptance criterion: Generate Pitches calculates delta = (3x unfilled slots) - valid pitches
- Test approach: Unit tests for calculation logic with various scenarios
- Key scenarios: All slots filled (button disabled), partial fills, first generation vs subsequent

**Key Considerations**:
- Calculation: total_slots - fleshed_recipes = unfilled_slots → target = 3x unfilled_slots → delta = target - valid_pitches
- Edge case: If all slots filled (unfilled = 0), button shows "All meals planned" and is disabled
- UI decision: Concise messaging ("Generating N pitches to fill remaining slots") per user preference
- Must use decremented inventory for new pitch generation (validate `load_available_inventory()` is called)

**Dependencies**: Phase 1 (needs valid pitch count calculation)

**Complexity**: S

---

### Phase 3: Recipe Detail Page with Routing ✓

**Purpose**: Create separate route for recipe detail view, showing compact cards on session page. This reduces visual clutter and creates focused cooking mode.

**Scope**: New route `/recipes/[id]`, session page compact cards component, inline recipe display in criterion groups

**Implementation Approach** (Revised during execution):
- **Original plan**: Recipes only in separate "Planned Recipes" section
- **Implemented**: Recipes appear in TWO places for different contexts:
  1. **Inline in criterion groups** (planning context): Recipes replace their source pitches spatially, showing what's committed per criterion
  2. **"Planned Recipes" section** (cooking context): Focused list with cook/abandon actions
- **Rationale**: User feedback during planning - "reinforces what I've already selected" and helps make contrasting choices ("I already have 2 rice dishes for weeknight meals, let me pick a pitch that contrasts")

**What Was Built**:
- GET `/api/recipes/{id}` endpoint with basic tests (happy path, 404, cooked state)
- Updated GET `/sessions/{id}/recipes` to include both PLANNED and COOKED recipes (exclude ABANDONED)
- Added `state` and `criterion_id` fields to FleshedOutRecipe schema
- Recipe detail page (`/recipes/[id]`) with full view, cook/abandon buttons, back navigation
- Compact recipe card component with visual distinction (soft green tint + checkmark icon)
- Inline recipe rendering in criterion groups (recipes shown before pitches)
- Updated "Planned Recipes" section to use compact cards with inline actions
- Cook action keeps recipe visible with "Cooked ✓" badge (instead of removing)
- Abandon action removes recipe entirely

**Tests**: 3 passing tests for GET `/api/recipes/{id}`, all existing session tests passing

**Files Modified**:
- `src/backend/routes.py` - Added GET endpoint, updated session recipes query
- `src/backend/schemas.py` - Added state and criterion_id fields
- `src/backend/tests/test_recipe_detail.py` - New test suite
- `src/frontend/src/routes/recipes/[id]/+page.svelte` - Recipe detail page
- `src/frontend/src/routes/recipes/[id]/+page.ts` - Data loader
- `src/frontend/src/routes/sessions/[id]/+page.svelte` - Inline recipes + compact cards

**Dependencies**: None (implemented independently)

**Complexity**: S (as planned)

---

### Phase 4: Markdown Rendering in Instructions

**Purpose**: Render markdown formatting in recipe instructions so emphasis and structure are visually clear.

**Scope**: Library integration (markdown-it), instruction rendering updates

**TDD Focus**:
- Acceptance criterion: Recipe instructions render bold, italics, inline code properly
- Test approach: Unit tests for markdown parsing, visual testing for output
- Key scenarios: Bold text, italic text, inline code, line breaks, mixed formatting

**Key Considerations**:
- Library choice: markdown-it (flexible, 28kb) per user preference
- Scope: Inline formatting only (bold, italics, code), not full markdown (headers, tables, lists)
- Security: markdown-it has XSS protection built-in (safe HTML output)
- Applies to both recipe detail page and any instruction previews
- Lightweight integration - just wrap instruction text with markdown renderer

**Dependencies**: None (can be done independently)

**Complexity**: XS (library integration is straightforward)

---

### Phase 5: Workflow-Oriented Page Sections

**Purpose**: Reorganize session page into job-to-be-done sections (Planning, Cooking, Shopping) with collapsible controls. This creates focus by hiding irrelevant sections.

**Scope**: Session page restructuring, section collapse/expand controls, visual hierarchy

**TDD Focus**:
- Acceptance criterion: Session page has clear sections that collapse/expand independently
- Test approach: E2E tests for section interaction, visual testing for hierarchy
- Key scenarios: Default state (pitches expanded, recipes compact, shopping minimized), toggle sections, mobile consideration

**Key Considerations**:
- Three sections: (1) Meal Criteria & Pitches, (2) Planned Recipes, (3) Shopping List
- Default state per user preference: Always reset (no localStorage), Pitches expanded, Recipes compact, Shopping minimized
- Visual hierarchy: Active section prominent, inactive sections compact with toggle controls
- Mobile consideration noted but not implemented (out of scope per MVP-CHARTER.md #140)
- URL anchors for deep linking (e.g., `/sessions/{id}#shopping`) - optional enhancement

**Dependencies**: Phase 3 (compact recipe cards need to exist first)

**Complexity**: S (reorganization of existing elements)

---

## Sequencing Logic

**Why this order minimizes risk**:
1. **Phase 1 first**: Fixes core bug (invalid pitches visible) that blocks authentic use
2. **Phase 2 next**: Builds on Phase 1's validation logic to calculate smart generation count
3. **Phase 3 independent**: Can be worked in parallel with Phase 1-2 (no dependencies)
4. **Phase 4 independent**: Lightweight library integration, can be dropped if time-constrained
5. **Phase 5 last**: Reorganizes UI after all functional pieces are in place (depends on Phase 3 compact cards)

**Where parallel work is possible**:
- Phase 3 (recipe detail page) can start while Phase 1-2 are in progress
- Phase 4 (markdown) can be done anytime, completely independent

**Where dependencies constrain sequencing**:
- Phase 2 needs Phase 1's validation logic (valid pitch count)
- Phase 5 needs Phase 3's compact recipe cards (can't reorganize what doesn't exist yet)

**How phases build on each other**:
- Phase 1 → Phase 2: Validation logic enables smart count calculation
- Phase 3 → Phase 5: Compact cards enable workflow reorganization
- All phases → Complete feature: Each phase independently valuable, together they transform UX

---

## High-Level Test Strategy

**TDD Throughout**: Red-green-refactor cycle per phase

**Phase 1 - Unit & Integration**:
- Unit tests: Pitch validation logic with various inventory states (same units, different units, missing ingredients)
- Integration test: Flesh out recipe → verify invalid pitches removed from session page
- Test in Svelte component: Use `page.test.ts` pattern from existing tests

**Phase 2 - Unit & Integration**:
- Unit tests: Generation count calculation with various scenarios (0 fleshed, 3 fleshed, all slots filled)
- Integration test: Click "Generate Pitches" → verify correct count generated, button state updated
- May need backend endpoint changes, test API responses

**Phase 3 - Integration & E2E**:
- Integration tests: Recipe detail page loads with data from `+page.ts` loader
- E2E test: Session page → click compact card → navigate to detail page → cook/abandon → back to session
- Use SvelteKit testing patterns (Testing Library, Playwright)

**Phase 4 - Unit & Visual**:
- Unit tests: Markdown rendering in Svelte component
- Visual testing: Verify rendered output matches expected formatting (use snapshots)

**Phase 5 - E2E & Visual**:
- E2E tests: Toggle sections, verify collapse/expand state persists during session
- Visual testing: Verify default state, section hierarchy, active/inactive styling
- Use Skeleton UI collapse components if available

**Overall Testing Approach**:
- Follow MVP testing patterns (see `src/frontend/src/routes/*/page.test.ts`)
- Leverage Svelte Testing Library for component tests
- Manual testing for visual validation (markdown rendering, section hierarchy)
- Pre-commit hooks catch formatting issues early

---

## Integration Points

**Backend Changes**:
- Pitch validation logic (calculate valid vs invalid based on decremented inventory)
- Generation count calculation endpoint or logic enhancement
- GET `/api/recipes/{id}` endpoint if not already exists (for recipe detail page)
- Markdown already returned by LLM, no backend changes needed

**Frontend Changes** (SvelteKit + Svelte 5):
- Pitch rendering: Filter invalid pitches from display (use `$derived` for reactive validity check)
- Generate Pitches UI: Calculate and show smart count, update button state
- Recipe compact cards component on session page
- New route: `src/frontend/src/routes/recipes/[id]/+page.svelte` and `+page.ts`
- Markdown-it library integration for instruction rendering
- Session page section reorganization: Use Skeleton UI collapse components or custom collapsible sections
- Extract reusable components (CompactRecipeCard, RecipeDetail)

**BAML Changes**:
- None (backend already passes decremented inventory, LLM already returns markdown-formatted instructions)

**Database Changes**:
- None (existing schema supports all features)

---

## Library Research

**Markdown Rendering**:
- Library: markdown-it (chosen per user preference)
- Why needed: Recipe instructions contain markdown formatting that needs visual rendering
- Decision made: Use markdown-it for flexibility (28kb, extensible, better parsing than marked.js)
- Integration: Install via npm, import in Svelte component, use `{@html markdown.render(instructions)}`
- Security: markdown-it sanitizes HTML output by default (XSS protection)
- May need TypeScript types: `@types/markdown-it`

**Skeleton UI Components**:
- Research existing collapse/accordion components from Skeleton library
- Check if Collapsible or Accordion components exist and fit workflow section needs
- Fallback: Custom Svelte component with transitions and state management

---

## Risk Assessment

**High Risks with Mitigation**:

**Risk: Unit mismatch complexity in invalidation logic**
- Problem: Ingredient name matches but units differ (pitch needs "1 lb carrots" but inventory has "3 carrots")
- Impact: Incorrect invalidation (either false positives or false negatives)
- Mitigation: Aggressive approach - invalidate if units don't match (false negatives acceptable)
- Steering likelihood: Medium - may need user feedback on specific edge cases during testing

**Medium Risks to Watch**:

**Risk: Markdown XSS vulnerability**
- Problem: User-generated markdown could inject malicious HTML
- Impact: Security vulnerability
- Mitigation: markdown-it sanitizes HTML by default, verify configuration
- Steering likelihood: Low - library handles this, just verify during implementation

**Risk: Section collapse state management**
- Problem: Managing multiple section states without localStorage (per user preference)
- Impact: State synchronization between UI and underlying data
- Mitigation: Simple default state reset, no persistence needed
- Steering likelihood: Low - straightforward implementation

**Contingency Plans**:

**If Phase 4 (markdown) becomes complex**:
- Drop markdown rendering (marked as droppable in frame)
- Display raw markdown text (acceptable for MVP)
- Revisit post-MVP when needs are clearer

---

## Implementation Notes

**TDD**: Test-Driven Development throughout all phases
- Write test first (red)
- Implement feature to pass test (green)
- Refactor for clarity (green)

**MVP Patterns to Follow**:
- SvelteKit file-based routing (`src/frontend/src/routes/`)
- Svelte 5 runes for reactive state (`$state`, `$derived`, `$effect`)
- EventSource SSE streaming (already in MVP `sessions/[id]/+page.svelte:250`)
- Skeleton UI components and styling (preset classes)
- TypeScript for type safety
- Existing test patterns (`page.test.ts` files)

**Current Implementation to Change**:
- Pitch invalidation: Add validity checking (doesn't exist in MVP yet)
- Generation count: Smart calculation instead of hardcoded `criterion.slots * 3`
- Recipe display: Extract compact card component, create detail route (current: inline full details)
- Page structure: Add collapsible workflow sections (current: flat sections)

**Quality Gates**:
- All tests pass (unit, integration, E2E)
- TypeScript type checking passes (`npm run check`)
- Manual testing confirms UX improvements
- Pre-commit hooks pass (ruff for Python, prettier + svelte-check for frontend)
- User validation on authentic data (real CSA inventory, real meal planning workflow)

**General Guidance**:
- Follow SvelteKit and Svelte 5 patterns (reactive statements, component composition)
- Keep EventSource SSE streaming for progressive loading
- Maintain separation of concerns (LLM declares, code manages state)
- Test with real inventory data throughout (not just mock data)
- Extract reusable components where appropriate (CompactRecipeCard, RecipeDetail)

---

## Overall Complexity Estimate

**Complexity**: M (Medium)

**Confidence**: High

**Justification**:

**What drives complexity**:
1. **Integration points**: 5 phases touching backend, frontend, and page structure coordination
2. **Decision density**: Unit mismatch handling strategy, section state management
3. **Scope breadth**: 5 user stories with distinct acceptance criteria, multiple systems affected
4. **SvelteKit familiarity**: MVP already uses SvelteKit patterns, reducing novelty

**Complexity per phase**:
- Phase 1 (Invalidation): S - Clear logic, add validity checking to existing pitch display
- Phase 2 (Smart generation): S - Straightforward calculation
- Phase 3 (Detail page): S - SvelteKit routing is file-based, trivial to add new route
- Phase 4 (Markdown): XS - Library integration is straightforward
- Phase 5 (Sections): S - Reorganization of existing elements, may leverage Skeleton UI

**Overall estimate considers**:
- SvelteKit routing is trivial (file-based), no research spike needed
- MVP already has most patterns in place (EventSource, state management, API calls)
- 5 phases are well-scoped with clear acceptance criteria
- Familiar tech stack (SvelteKit, Svelte 5, TypeScript) reduces unknowns

**Estimate is Medium (not Large) because**:
- No novel patterns needed - SvelteKit routing is built-in
- MVP provides strong foundation (existing session page, API endpoints, components)
- Each phase is straightforward with existing patterns to follow
- High confidence from clear tech stack and existing implementation

**Estimate is not Small because**:
- 5 distinct phases require coordination
- Multiple integration points (backend validation, frontend rendering, routing)
- Expected steering on unit mismatch edge cases
- Breadth of changes across multiple systems
