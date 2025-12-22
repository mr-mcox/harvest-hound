# Feature Frame: Session Page UX & Workflow Reorganization

**Date**: 2025-12-08
**Status**: In Progress - Phase 3 of 5 Complete
**TIP**: docs/development/tips/tip-session-page-ux-workflow.md

## Implementation Progress

- ✅ **Phase 1**: Quantity-Aware Pitch Invalidation
- ✅ **Phase 2**: Smart Manual Pitch Generation
- ✅ **Phase 3**: Recipe Detail Page with Routing (with inline recipe display)
- ⬜ **Phase 4**: Markdown Rendering in Instructions
- ⬜ **Phase 5**: Workflow-Oriented Page Sections

---

## Problem Statement

The current session page mixes three distinct jobs-to-be-done into a single view, creating UX problems: (1) pitches don't disappear when their ingredients are claimed, leading to invalid options piling up, (2) "Generate Pitches" duplicates instead of self-healing, (3) full recipes dominate the page, making pitch selection and weekly planning difficult. Users need different views for different workflow phases: planning meals, cooking tonight's recipe, and shopping.

**From Prototype Discovery**:
- LEARNINGS.md #7: "Pitches using claimed ingredients become invalid - user feedback: 'I'd like them removed' - don't want to see unavailable options"
- LEARNINGS.md #8: "Want to maintain consistent pool of available options - automatic backfill when available pitches drop below threshold"
- LEARNINGS.md #631: "Different views for different contexts: planning view, cooking view, reviewing view as distinct modes"
- MVP-CHARTER.md Phase 2 Fidelity: "Pitches: Invalidation/removal when ingredients claimed"

**Current State from Database/Screenshots**:
- Session has 2 fleshed-out recipes with 5 ingredient claims (red kuri squash, chicken, beef, black radish, acorn squash)
- 29 total pitches in system (18 quick weeknight, 6 GF/DF leftovers, 5 Saturday afternoon)
- UI shows pitches that use claimed ingredients (e.g., "Crispy Reverse-Seared Pork Chops with Kohlrabi-Apple Slaw" still visible even though kohlrabi might be claimed)
- Full recipes take up most vertical space with complete ingredient lists and instructions
- No clear separation between "planning mode" and "cooking mode"

---

## User Stories

### Story 1: Remove invalid pitches (quantity-aware)
**As a** meal planner
**I want** pitches that can't be made with remaining inventory to be removed from view
**So that** I only see options I can actually make after accounting for claims

**Acceptance Criteria**:
- [ ] After fleshing out a recipe, calculate remaining inventory: physical - claimed quantities
- [ ] Mark pitch invalid if it needs more of any ingredient than remains available
- [ ] Example valid: Have 2 lbs carrots, Recipe A claims 1 lb, Pitch B needs 0.5 lb → valid (1 lb remains)
- [ ] Example invalid: Have 1 acorn squash, Recipe A claims 1, Pitch B needs 1 → invalid (0 remains)
- [ ] Invalid pitches are removed, not grayed out (user feedback: "I'd like them removed")
- [ ] Pitch count updates to reflect removed pitches (e.g., "Quick weeknight (18 pitches)" → "Quick weeknight (13 pitches)")
- [ ] If multiple recipes flesh out concurrently, invalidation runs after all claims created
- [ ] Case-insensitive ingredient name matching (e.g., "Black Radish" matches "black radish" claim)

**From LEARNINGS.md**: Line 287-290 - "User feedback: 'I'd like them removed' - don't want to see unavailable options"

### Story 2: Smart manual pitch generation
**As a** meal planner
**I want** "Generate Pitches" to only create the pitches I need based on unfilled slots and invalid pitches
**So that** I get just enough new options without duplicates or excess

**Acceptance Criteria**:
- [ ] Calculate unfilled slots: total slots - fleshed-out recipes (e.g., 3 slots, 2 fleshed → 1 unfilled)
- [ ] Calculate valid pitches: existing pitches - invalid pitches (not enough inventory remaining)
- [ ] Generate target: 3x unfilled slots (e.g., 1 unfilled → 3 pitches needed)
- [ ] Only generate delta: target - valid pitches (e.g., need 3, have 2 valid → generate 1)
- [ ] Example: 3 slots, 9 original pitches, selected 2, 5 invalidated → 2 valid for 1 slot → generate 1 pitch
- [ ] Show calculation in UI: "1 meal remaining, 2 valid pitches (7 removed) — generating 1 more pitch"
- [ ] If all slots filled, button shows "All meals planned" and is disabled
- [ ] New pitches use decremented inventory (don't reuse claimed ingredients)

**From LEARNINGS.md**: Line 292-297 - "Want to maintain consistent pool of available options" (user-triggered, not automatic)

### Story 3: Compact recipe view with expandable detail
**As a** meal planner
**I want** fleshed-out recipes to show compactly with option to view full details
**So that** the session page focuses on pitch selection without being dominated by recipe details

**Acceptance Criteria**:
- [x] Fleshed-out recipes show in compact card: name, time, claimed ingredients summary
- [x] Click recipe card to navigate to full recipe detail page (new route: `/recipes/{id}`)
- [x] Full recipe page shows: ingredients, instructions, cook/abandon buttons
- [x] "Back to Session" button returns to session page
- [x] Recipe cards show cooking status with visual distinction: planned (soft green + checkmark), cooked (badge + muted)
- [x] **Implementation decision**: Recipes appear in TWO places for different contexts:
  - **Inline in criterion groups** (planning context): Shows what's committed for each criterion, helps make contrasting choices
  - **"Planned Recipes" section** (cooking context): Focused list for execution, with cook/abandon actions
- [x] Visual distinction: Recipes use soft green tint + checkmark icon vs neutral pitch cards

**Implementation Rationale**: Dual display reinforces selections during planning ("I already have 2 rice dishes for weeknight meals, let me pick something different") while maintaining a focused cooking view. Recipes spatially replace their source pitches in criterion groups.

**From LEARNINGS.md**: Line 625-630 - "Different views for different contexts...compact recipe representation works for weekly hub, more detailed view needed for cooking"

### Story 4: Workflow-oriented page sections
**As a** meal planner
**I want** the session page organized by job-to-be-done (planning, cooking tonight, shopping)
**So that** I can focus on the current task without distraction

**Acceptance Criteria**:
- [ ] Session page has clear sections: (1) Meal Criteria & Pitches, (2) Planned Recipes, (3) Shopping List
- [ ] Sections can collapse/expand independently
- [ ] Default state: Pitches expanded (planning mode), Recipes compact, Shopping minimized
- [ ] Visual hierarchy: Active section prominent, inactive sections compact
- [ ] URL anchors for deep linking (e.g., `/sessions/{id}#shopping`)
- [ ] Mobile consideration: One section visible at a time with tab navigation

**From LEARNINGS.md**: Line 104 - "Now feeling like a central hub to keep coming back to over the course of a week"

### Story 5: Render markdown in recipe instructions
**As a** meal planner
**I want** recipe instruction formatting (bold, italics, lists) to display properly
**So that** important steps and techniques are visually emphasized

**Acceptance Criteria**:
- [ ] Recipe instructions render markdown: bold (**text**), italics (*text*), inline code (`text`)
- [ ] Example: "**Cook chicken:** Nestle the marinated chicken..." renders with bold "Cook chicken:"
- [ ] Preserves line breaks and paragraph structure
- [ ] No full markdown parser needed (just inline formatting, not headers/tables/etc)
- [ ] Applies to both recipe detail page and any instruction previews
- [ ] Library consideration: Use lightweight markdown-to-HTML (e.g., `marked` or similar)

**From user feedback**: "recipe generation is generating markdown formatting eg '**Cook chicken:** Nestle'. It would be nice if that were rendered appropriately."

---

## Prototype Contrast

| Aspect | Current | Target | Why Change |
|--------|---------|--------|------------|
| Pitch invalidation | No removal, all pitches visible | Auto-remove when ingredients claimed | LEARNINGS.md #287: User explicitly requested removal vs graying out |
| Pitch regeneration | Manual "Generate Pitches" duplicates | Auto-backfill when pool drops below threshold | LEARNINGS.md #292: Self-healing pool reduces friction |
| Recipe display | Full ingredients+instructions inline | Compact cards with expandable detail | LEARNINGS.md #625: Different views for different contexts |
| Page organization | Single flat list | Workflow sections (plan/cook/shop) | User's job-to-be-done varies by day (planning Monday, cooking Tuesday) |

**Preserve from Prototype**:
- Criterion-grouped pitch organization (Quick weeknight meal, GF/DF leftovers, etc.)
- Checkbox selection for pitches before flesh-out
- Shopping list aggregation by purchase likelihood
- Cook/Abandon recipe lifecycle

**Fix from Prototype**:
- Pitches don't respect claimed ingredients (blocking issue)
- "Generate Pitches" creates duplicates instead of self-healing
- Recipe details dominate vertical space

**Change from Prototype**:
- Move from single-page to shallow navigation (session → recipe detail → back to session)
- Progressive disclosure for recipe details

---

## Out of Scope (Deferred)

Explicitly NOT part of this feature:
- **Bulk recipe operations**: Week-by-week n is small (5-7 recipes), individual management sufficient (LEARNINGS.md #582)
- **Recipe editing after planning**: Abandon+regenerate is acceptable workaround for MVP (LEARNINGS.md #523-527)
- **Pitch prioritization by uncommon ingredients**: Auto-pivot works well enough (LEARNINGS.md #569-572)
- **Mobile responsiveness**: Desktop-first MVP (MVP-CHARTER.md #140)
- **Recipe library/canonical recipes**: Post-MVP (LEARNINGS.md #654-658)

**Future Features This Enables**:
- Recipe detail page infrastructure enables future cookbook/library view
- Workflow sections pattern extends to other multi-step flows
- Pitch invalidation logic enables smarter backfill strategies

---

## Open Risks

**Risk: Quantity-aware invalidation complexity**
- Need to aggregate claims by ingredient across all recipes, subtract from physical inventory
- Unit conversion complexity: pitch needs "1 lb" but inventory has "2 each acorn squash" (apples to oranges)
- **MVP approach (aggressive)**: Invalidate if ingredient name matches but units don't match
- **Rationale**: False negatives (removing valid pitches) are better than false positives (showing invalid pitches)
- **Example cases**:
  - Case 1: Same units (1 lb vs 2 lb) → straightforward subtraction, invalidate if insufficient
  - Case 2: Different units (1 cup onion vs 2 onions) → invalidate pitch (aggressive approach)
- **Post-MVP**: Smarter unit normalization or LLM-based feasibility check to reduce false negatives

**Risk: Pitch regeneration using decremented inventory**
- Backend currently passes inventory to BAML, needs to pass decremented state (physical - claims)
- Already implemented in `load_available_inventory()` but may need verification
- **Validation**: Test that new pitches don't reuse claimed ingredients (e.g., after claiming black radish, new pitches shouldn't include it)

---

## Alignment Decisions

**Unit mismatch handling**: ✅ Aggressive
- Invalidate if ingredient name matches but units don't match
- Rationale: False negatives (removing valid pitches) better than false positives (showing invalid pitches)

**MVP scope**: ✅ All 5 stories in scope
- Story #1 (Quantity-aware pitch invalidation): Essential
- Story #2 (Smart manual generation): Essential
- Story #3 (Compact recipes + detail page): Essential
- Story #4 (Workflow sections): Essential
- Story #5 (Markdown rendering): Essential (droppable if complex during implementation)

**Implementation order**: ✅ Approved
- #1 (Invalidation) → #2 (Smart generation) → #3 (Compact recipes) → #5 (Markdown) → #4 (Workflow sections)
- Fixes bugs first, then UX improvements

**Scope boundaries**: ✅ Stories are well-scoped as written

**Recipe display strategy** (decided during Phase 3 implementation): ✅ Dual display
- Recipes appear BOTH inline in criterion groups AND in "Planned Recipes" section
- Rationale: Different contexts serve different needs
  - Inline (planning context): See what's committed per criterion, make contrasting choices
  - Section (cooking context): Focused execution view with actions
- Visual distinction: Soft green tint + checkmark icon (recipes) vs neutral (pitches)
- Cook behavior: Recipes stay visible with "Cooked ✓" badge (not removed)
- Alternative considered: Recipes only in separate section (rejected - loses planning context)
