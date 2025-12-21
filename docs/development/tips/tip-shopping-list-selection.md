---
date: 2025-12-20
feature: shopping-list-selection
status: draft
frame: .scratch/frame-shopping-list-selection.md
estimated_effort: M-L
confidence: Medium-High
tags: [shopping-list, feedback-loop, bayesian-learning, pantry-accuracy]
---

# TIP: Shopping List Selection & Pantry Learning

## Context

### Problem Statement

The shopping list currently shows what to buy but doesn't support the actual shopping workflow: checking off what you need, filtering to just those items, and copying only what's relevant. More critically, we're missing an opportunity to learn from these selections - every shopping trip reveals which "pantry staples" assumptions were wrong, but we're not capturing that feedback to improve future grocery lists and recipe generation.

**From Production Use**:
- Shopping list view works great for planning → shopping workflow (LEARNINGS.md:342)
- **Pantry guesses NOT as accurate as expected** - affects both grocery list ranking AND recipe generation (LEARNINGS.md:232)
- Feedback loop opportunity identified: grocery selections could inform pantry definitions (LEARNINGS.md:233)
- Current workflow: copy-paste to shopping apps works, but manual filtering is tedious

### User Stories

#### Story 1: Interactive Shopping List Selection (Essential)
**As a** meal planner
**I want** to check off the grocery items I actually need to buy
**So that** I can focus on what's missing from my pantry and ignore what I already have

**Acceptance Criteria** (TDD seeds):
- Each grocery item and pantry staple has a checkbox
- Checked items are visually distinct from unchecked items
- Filter toggle shows "Items to Buy" (checked only) vs "All Items" (default)
- Item check state persists during the session (survives page refresh)
- Unchecking an item removes it from the filtered view

#### Story 2: Copy Checked Items Only (Essential)
**As a** meal planner
**I want** to copy only the items I've checked off
**So that** I can paste a clean list into my shopping app (Mealboard, Out of Milk, etc.)

**Acceptance Criteria** (TDD seeds):
- "Copy Checked Items" button appears when at least one item is checked
- Button copies checked items in paste-friendly format (ingredient + quantity, one per line)
- Copied format excludes confidence %, recipe context (clean for external apps)
- Visual feedback confirms successful copy (toast/checkmark)
- Works alongside existing "Copy All" functionality (don't break current workflow)

#### Story 3: Global Ingredient Purchase Statistics (Essential)
**As a** system
**I want** to track which ingredients are purchased vs skipped across sessions
**So that** I can learn each household's actual pantry staples over time

**Acceptance Criteria** (TDD seeds):
- When user checks items in shopping list, selection state is recorded
- Stats derived at query time from reviewed selections: sessions_observed, times_purchased, times_skipped
- Only reviewed selections contribute to stats (positive engagement signal)
- Stats computed globally across all sessions (not session-scoped)
- Stats are ingredient-name based (not recipe-specific)

#### Story 4: Engagement Tracking for Valid Feedback (Essential)
**As a** system
**I want** to distinguish "user had everything in stock" from "user didn't review the list"
**So that** absence of purchases doesn't incorrectly signal "everything is a pantry staple"

**Acceptance Criteria** (TDD seeds):
- "Mark as Reviewed" action explicitly signals user engaged with list
- Reviewing with NO items checked = valid signal (had everything)
- Reviewing with SOME items checked = valid signal (purchased those, skipped rest)
- Not reviewing = no stats recorded (ambiguous data rejected)
- Review status persists with session (can see "Reviewed on Dec 20")

#### Story 5: Bayesian Likelihood Refinement (Essential)
**As a** meal planner
**I want** the system to learn from my past shopping selections
**So that** grocery lists get smarter over time and pantry guesses improve

**Acceptance Criteria** (TDD seeds):
- When generating shopping list, use historical stats to refine purchase_likelihood
- Bayesian update: LLM prior (current likelihood) + historical data → posterior likelihood
- Example: Onions had 0.8 prior, but skipped 10/11 times → posterior drops to ~0.2
- Example: Goat cheese had 0.3 prior, but purchased 8/8 times → posterior rises to ~0.9
- Updated likelihoods affect grocery/pantry split (threshold still 0.3)
- Updated likelihoods affect sort order (high confidence items first)

### Scope Boundaries

**In Scope**:
- Session-scoped checkbox state (database-backed)
- Filter toggle (checked only vs all)
- Copy checked items (paste-friendly format)
- Global ingredient purchase statistics (derived from reviewed selections)
- Explicit "Mark as Reviewed" engagement tracking
- Bayesian likelihood refinement using historical data

**Out of Scope (Deferred)**:
- External app integrations (Mealboard, Out of Milk direct export)
- WHY tracking (reasons for skipping)
- Automatic pantry updates (just collect data, don't auto-update pantry config)
- Multi-store selection tracking
- Ingredient substitution preferences
- Stats visibility UI (invisible for MVP)

### Current MVP Implementation Patterns

**Backend Patterns** (from `src/backend/`):
- `shopping_list.py:149` - `compute_shopping_list()` aggregates ingredients, returns ShoppingListResponse
- `models.py:82-88` - PlanningSession model for session-scoped data
- `models.py:160-183` - Recipe model with JSON columns for structured data
- `models.py:185-196` - IngredientClaim model for foreign key relationships, CASCADE deletes
- `routes.py:846-866` - GET endpoint pattern for on-demand computation
- `test_shopping_list.py` - Domain-first TDD with helper functions

**Frontend Patterns** (from `src/frontend/src/`):
- `lib/components/ShoppingList.svelte:1-108` - Component receives props, displays grocery/pantry sections
- `routes/sessions/[id]/+page.svelte:106-224` - Svelte 5 runes ($state, $derived) for reactive data
- `routes/sessions/[id]/+page.svelte:201` - Async data loading pattern with loading/error states
- `routes/sessions/[id]/+page.svelte:827-830` - Component composition pattern

**Key Learnings**:
- Likelihood-based ingredient sourcing (≥0.3 = grocery, <0.3 = pantry) - LEARNINGS.md:251-258
- Shopping list fills planning → shop → cook workflow - LEARNINGS.md:342-349
- Pantry accuracy gap identified in production - LEARNINGS.md:226-234

---

## Implementation Phases

### Phase 1: Database Schema & Stats Foundation ✓

**Purpose**: Establish data model for selection state. Stats are derived from selections at query time (no separate stats table to avoid data drift).

**Scope**: Database schema additions, migrations

**TDD Focus**:
- Acceptance criteria: Selection state persisted per session
- Test approach: Database constraint tests, model validation tests

**Key Considerations**:
- `ShoppingListSelection` table: session-scoped checkbox state
  - Foreign key to PlanningSession with CASCADE delete
  - Composite uniqueness constraint: (session_id, ingredient_name)
  - `reviewed_at` timestamp for engagement tracking (NULL = not reviewed)
  - `checked` boolean for selection state
- Stats derived at query time from reviewed selections (no separate table)
- Alembic migration for schema changes

**Dependencies**: None (foundation phase)

**Complexity**: S

---

### Phase 2: Backend - Selection State Management ✓

**Purpose**: Enable reading and updating checkbox state per session. This allows frontend to persist user selections across page refreshes.

**Scope**: Backend API endpoints, database persistence

**TDD Focus**:
- Acceptance criteria: Item check state persists (survives refresh)
- Test approach: Integration tests for API endpoints, unit tests for selection logic

**Key Considerations**:
- API endpoint: `PATCH /api/sessions/{session_id}/shopping-list/selections`
  - Request body: `{ingredient_name: str, checked: bool}`
  - Upsert pattern: update if exists, insert if not
  - Return updated selections list
- API endpoint: `GET /api/sessions/{session_id}/shopping-list/selections`
  - Return all selections for session as `{ingredient_name: checked}` dict
  - Used on page load to restore checkbox state
- Modify `compute_shopping_list()` to include selection state
  - Join ShoppingListSelection on (session_id, ingredient_name)
  - Add `checked` field to ShoppingListItem response
- Handle edge case: ingredient no longer in shopping list (recipe abandoned) but selection exists

**Dependencies**: Phase 1 (schema must exist)

**Complexity**: M

---

### Phase 3: Backend - Review Endpoint ✓

**Purpose**: Capture user engagement signal by marking selections as reviewed. Stats are derived from reviewed selections at query time (Phase 4).

**Scope**: Backend API endpoint

**TDD Focus**:
- Acceptance criteria: "Mark as Reviewed" sets timestamp, engagement tracking works
- Test approach: Integration tests for review endpoint

**Key Considerations**:
- API endpoint: `POST /api/sessions/{session_id}/shopping-list/review`
  - Mark `ShoppingListSelection.reviewed_at = now()` for all selections in session
  - Return success response with review timestamp
- Handle edge case: User reviews multiple times
  - Allow re-reviewing (updates timestamp) - user might check off more items while shopping
- No stats table to update - stats derived at query time from reviewed selections

**Dependencies**: Phase 1 (schema), Phase 2 (selection state)

**Complexity**: S

---

### Phase 4: Backend - Bayesian Likelihood Refinement

**Purpose**: Use historical purchase statistics to refine LLM-generated purchase likelihoods. This improves grocery/pantry split accuracy over time.

**Scope**: Backend computation logic, Bayesian formula implementation

**TDD Focus**:
- Acceptance criteria: Bayesian update produces correct posteriors, affects grocery/pantry split
- Test approach: Unit tests for Bayesian formula with known inputs/outputs

**Key Considerations**:
- Modify `compute_shopping_list()` to derive stats from reviewed selections:
  ```sql
  SELECT 
    ingredient_name,
    COUNT(*) as sessions_observed,
    SUM(CASE WHEN checked THEN 1 ELSE 0 END) as times_purchased,
    SUM(CASE WHEN NOT checked THEN 1 ELSE 0 END) as times_skipped
  FROM shoppinglistselection
  WHERE reviewed_at IS NOT NULL
  GROUP BY ingredient_name
  ```
- Bayesian update formula:
  - Prior: `purchase_likelihood` from recipe ingredient (LLM-generated)
  - Evidence: `times_purchased / sessions_observed` (empirical rate)
  - Weights: `w_prior` and `w_evidence` based on `sessions_observed`
    - Early sessions (n < 5): favor prior heavily (LLM knows more)
    - Later sessions (n ≥ 10): favor evidence (user data is reliable)
    - Example weights: `w_prior = max(5, 10 - sessions_observed)`, `w_evidence = sessions_observed`
  - Posterior: `(prior * w_prior + empirical * w_evidence) / (w_prior + w_evidence)`
- Apply posterior to `purchase_likelihood` field before grocery/pantry split
- Preserve original LLM likelihood in tests for comparison
- Handle edge cases:
  - No historical data: use prior as-is
  - Zero sessions observed: use prior as-is

**Dependencies**: Phase 3 (reviewed selections must exist)

**Complexity**: M

---

### Phase 5: Frontend - Interactive Selection UI

**Purpose**: Enable users to check off items they need to buy. This is the primary UX improvement for the shopping workflow.

**Scope**: Frontend component updates, state management, API integration

**TDD Focus**:
- Acceptance criteria: Checkboxes work, visual distinction, persist on refresh
- Test approach: Component tests for checkbox behavior (light coverage)

**Key Considerations**:
- Update `ShoppingList.svelte`:
  - Add checkbox input for each item (grocery and pantry)
  - Use Svelte 5 `$state` for checkbox state: `let selections = $state(new Map<string, boolean>())`
  - Load selections on mount: `fetch('/api/sessions/{id}/shopping-list/selections')`
  - On checkbox change: `PATCH /api/sessions/{id}/shopping-list/selections`
  - Visual distinction: checked items have different opacity/strikethrough/background
- Handle loading state while fetching selections (avoid flash of unchecked boxes)
- Handle optimistic updates (update UI immediately, rollback on API failure)
- Checkbox component: Use Skeleton UI checkbox or custom styled input
- Consider accessibility: keyboard navigation, screen reader labels

**Dependencies**: Phase 2 (API endpoints for selection state)

**Complexity**: M

---

### Phase 6: Frontend - Filter & Copy Features

**Purpose**: Allow filtering to checked items and copying only what's needed. This completes the shopping workflow UX.

**Scope**: Frontend UI additions, clipboard integration

**TDD Focus**:
- Acceptance criteria: Filter toggle works, copy button appears, paste format is clean
- Test approach: Component tests for filter logic, manual testing for clipboard (light coverage)

**Key Considerations**:
- Filter toggle button:
  - States: "All Items" (default) vs "Items to Buy" (checked only)
  - Use `$derived` to compute filtered lists: `let visibleGroceryItems = $derived(filterChecked ? groceryItems.filter(i => selections.get(i.ingredient_name)) : groceryItems)`
  - Apply same filter to pantry staples section
- "Copy Checked Items" button:
  - Only show when at least one item is checked
  - Format: `${ingredient_name} ${total_quantity}` (one per line)
  - Exclude confidence %, recipe context (clean for paste)
  - Use Clipboard API: `navigator.clipboard.writeText(text)`
  - Visual feedback: toast notification or temporary checkmark icon
- Preserve existing "Copy All" functionality (don't break current workflow)
- Button placement: near filter toggle, clear hierarchy

**Dependencies**: Phase 5 (checkbox state must exist)

**Complexity**: S

---

### Phase 7: Frontend - Review Action

**Purpose**: Allow user to signal they've reviewed the list. This triggers stats recording and provides engagement tracking.

**Scope**: Frontend UI addition, API integration

**TDD Focus**:
- Acceptance criteria: Review button works, success feedback shown
- Test approach: Integration test for API call (light coverage)

**Key Considerations**:
- "Mark as Reviewed" button:
  - Placement: Bottom of shopping list, or near filter/copy buttons
  - Action: `POST /api/sessions/{id}/shopping-list/review`
  - Success feedback: Toast notification "Shopping list reviewed on [date]"
  - Update UI to show review status (e.g., "Last reviewed: Dec 20, 2:30pm")
- Behavior after review:
  - Allow re-reviewing? (Yes - user might check off more items while shopping)
  - Disable checkboxes? (No - let user continue marking items)
- Consider loading state during API call
- Error handling: Display error message if review fails

**Dependencies**: Phase 3 (review API endpoint)

**Complexity**: S

---

## Sequencing Logic

**Foundation-first approach**: Phase 1 establishes data models, all subsequent phases depend on it.

**Backend-then-frontend pattern**: Phases 2-4 build backend capabilities (state management, review endpoint, Bayesian refinement), then Phases 5-7 build frontend UX on top.

**Progressive enhancement**: Each phase delivers independently valuable capability:
- Phase 2: Selection persistence (no UI yet, but foundation)
- Phase 3: Review endpoint (marks selections as reviewed for stats derivation)
- Phase 4: Bayesian refinement (improves shopping list quality)
- Phase 5: Interactive UI (immediate UX value)
- Phase 6: Filter & copy (workflow completion)
- Phase 7: Review action (engagement tracking, stats flow)

**Parallel work possible**:
- Phase 4 (Bayesian) can be built in parallel with Phase 5 (Frontend UI) - both depend on Phase 3 but not each other
- Phase 6 (Filter/copy) and Phase 7 (Review) could be combined if desired - both are small frontend additions

**Risk sequencing**: Bayesian logic (Phase 4) is most mathematically complex, placed after foundational phases but before full frontend rollout. Can validate with unit tests before UI integration.

---

## High-Level Test Strategy

**TDD throughout all phases** - Red-Green-Refactor cycle for each feature.

### Backend Testing (Comprehensive)

**Phase 1: Database Schema**
- Model validation tests (constraints, foreign keys)
- Migration tests (schema created correctly)

**Phase 2: Selection State**
- Unit tests: Selection persistence logic (upsert behavior)
- Integration tests: API endpoints (PATCH/GET selections)
- Edge case tests: Ingredient no longer in shopping list

**Phase 3: Review Endpoint**
- Integration tests: Review endpoint sets reviewed_at timestamp
- Edge case tests: Review multiple times, empty shopping list

**Phase 4: Bayesian Refinement**
- Unit tests: Bayesian formula (known inputs → expected outputs)
- Unit tests: Stats derivation query (aggregates reviewed selections correctly)
- Integration tests: compute_shopping_list() with historical data
- Edge case tests: No historical data, zero sessions

**Test Scenarios from Acceptance Criteria**:
- Onions skipped 10/11 times: prior 0.8 → posterior ~0.2 (verify grocery/pantry split changes)
- Goat cheese purchased 8/8 times: prior 0.3 → posterior ~0.9 (verify sort order changes)
- First session: no historical data → use LLM prior as-is
- Review with no items checked: valid signal (all items skipped)

### Frontend Testing (Light)

**Phase 5: Interactive UI**
- Component tests: Checkbox state updates on click
- Integration tests: API called on checkbox change (manual or light)

**Phase 6: Filter & Copy**
- Component tests: Filter logic (checked-only view)
- Manual testing: Clipboard copy (paste into external app)

**Phase 7: Review Action**
- Integration tests: Review API called on button click (manual or light)

**Manual Testing Focus**:
- End-to-end workflow: Check items → filter → copy → paste into Mealboard
- Cross-session persistence: Check items → refresh page → checkboxes restored
- Bayesian learning: Mark reviewed → next session → likelihoods improved

---

## Integration Points

### Backend
- **Models**: Add ShoppingListSelection table (stats derived at query time)
- **Routes**: Add PATCH/GET selections, POST review endpoints
- **Services**: Modify `compute_shopping_list()` for Bayesian refinement (derives stats from reviewed selections)
- **Migrations**: Alembic migrations for schema changes

### Frontend
- **Components**: Update ShoppingList.svelte with checkboxes, filter, buttons
- **State**: Session-scoped selection state with Svelte 5 runes
- **API Integration**: PATCH/GET selections, POST review
- **Page**: +page.svelte integration (load selections, handle review)

### BAML
- No prompt changes needed (purchase_likelihood already in RecipeIngredient)

---

## Risk Assessment

### High Risks

**Risk: Bayesian formula edge cases**
- Impact: Incorrect posteriors could make shopping list worse, not better
- Mitigation:
  - Comprehensive unit tests with known inputs/outputs
  - Guard against division by zero, null sessions
  - Progressive weighting (favor LLM prior when data is sparse)
  - Manual validation in first few sessions after deployment
- Contingency: If formula produces bad results, can disable Bayesian refinement and fall back to LLM-only

**Risk: Ingredient name exact match fragmentation**
- Impact: "Yellow Onion" vs "yellow onion" vs "Onion" tracked separately, Bayesian learning less effective
- Mitigation:
  - Accept for MVP (user clarified: use exact match as-is)
  - Monitor in production: if fragmentation becomes painful, add normalization in future iteration
- Contingency: Could add ingredient grouping/merging feature later if needed

### Medium Risks

**Risk: Review workflow unclear to user**
- Impact: User doesn't "Mark as Reviewed", no stats collected, feature doesn't learn
- Mitigation:
  - Clear button label: "Mark as Reviewed" with tooltip explaining purpose
  - Success feedback: "Shopping list reviewed on [date]" confirmation
  - Consider onboarding hint on first use (deferred for MVP)
- Contingency: Monitor review rate in logs, add UI hints if adoption is low

**Risk: Session-scoped state synchronization**
- Impact: Checkbox state out of sync between frontend and backend (API failures, race conditions)
- Mitigation:
  - Optimistic updates with rollback on API failure
  - Load selections on mount (authoritative backend state)
  - Clear error messages if sync fails
- Contingency: "Reload shopping list" button to force re-sync

### Low Risks

**Risk: Clipboard API browser compatibility**
- Impact: Copy button doesn't work in some browsers
- Mitigation: Clipboard API widely supported in modern browsers
- Contingency: Fallback to manual copy (select text, Ctrl+C) if needed

---

## Implementation Notes

### TDD Approach
- **Test-Driven Development throughout all phases**
- Write tests first (red), implement to pass (green), refactor (refactor)
- Backend: Comprehensive domain logic and integration tests
- Frontend: Light component tests, rely on manual testing for UX

### Current Implementation Patterns to Follow
- Database models with CASCADE deletes (Phase 1) - see `models.py:185-196` (IngredientClaim)
- Upsert pattern for selection state (Phase 2) - new pattern, but follows SQLModel conventions
- On-demand computation in `compute_shopping_list()` (Phase 4) - see `shopping_list.py:149`
- Svelte 5 runes for reactive state (Phase 5) - see `routes/sessions/[id]/+page.svelte:106-224`
- Component composition pattern - see `ShoppingList.svelte` as prop-driven component

### Extensions to Current Implementation
- Shopping list computation: Add Bayesian refinement step (Phase 4) - extends `compute_shopping_list()`
- ShoppingListItem schema: Add `checked` field (Phase 2) - extends existing ShoppingListItem response
- Frontend: Add interactive selection UI (Phase 5-7) - enhances existing ShoppingList.svelte component

### Quality Gates
- All tests pass before moving to next phase
- Migration runs cleanly on dev.db
- Pre-commit hooks pass (formatting, linting)
- Manual end-to-end test: Check items → filter → copy → review → next session sees improved likelihoods

### Bayesian Formula Details
```python
# Pseudocode for Bayesian update
def bayesian_update(prior: float, sessions_observed: int, times_purchased: int) -> float:
    if sessions_observed == 0:
        return prior  # No data, use LLM prior

    empirical = times_purchased / sessions_observed

    # Weight function: favor evidence as sessions accumulate
    w_prior = max(5, 10 - sessions_observed)  # Starts at 10, drops to 5
    w_evidence = sessions_observed  # Grows linearly

    posterior = (prior * w_prior + empirical * w_evidence) / (w_prior + w_evidence)
    return posterior
```

---

## Overall Complexity Estimate

**Overall: M-L (Moderate-Large)**

**Confidence: Medium-High**

**Justification**:
- **Scope**: 7 phases, mix of backend and frontend work
- **Novelty**: Bayesian formula is new pattern (not in prototype), but mathematically straightforward
- **Integration**: Multiple systems (database, API, frontend), but established patterns exist
- **Decision density**: Most decisions resolved by feature frame and user clarification
- **Steering likelihood**: Low - clear requirements, proven patterns, unit tests validate Bayesian logic

**Complexity breakdown**:
- Phase 1 (Schema): S - Straightforward database additions
- Phase 2 (Selection State): M - New state management pattern
- Phase 3 (Stats Recording): M - Stats computation logic, upsert pattern
- Phase 4 (Bayesian): M - Mathematical formula, edge case handling
- Phase 5 (Frontend UI): M - State management, API integration
- Phase 6 (Filter/Copy): S - UI logic, clipboard
- Phase 7 (Review): S - Simple button + API call

**Cumulative scope is substantial, but individual phases are manageable.** Established patterns (database models, API endpoints, Svelte components) reduce implementation complexity. Bayesian refinement is the most novel aspect, but comprehensive unit tests will validate correctness.
