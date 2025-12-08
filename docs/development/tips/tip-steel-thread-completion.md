---
date: 2025-12-08
feature: steel-thread-completion
status: draft
frame: .scratch/frame-steel-thread-completion.md
estimated_effort: M
confidence: High
tags: [mvp, shopping-list, recipe-lifecycle, steel-thread]
---

# Technical Implementation Plan: Shopping List & Recipe Lifecycle

## Context

**Problem Statement**: Complete the steel thread (planning → shopping → cooking) by implementing shopping list generation and recipe lifecycle transitions. Users need to see what groceries to buy (planned recipes minus claimed inventory) and mark recipes as cooked or abandoned to complete the weekly meal planning loop.

**User Stories**:

1. **Generate Force-Ranked Shopping List** (Essential)
   - As a meal planner, I want to see what groceries I need to buy for planned recipes, ordered by confidence
   - So that I can efficiently shop for ingredients not already in inventory

2. **Mark Recipe as Cooked** (Essential)
   - As a meal planner, I want to mark a recipe as cooked when I make it
   - So that the system consumes ingredient claims and tracks completion

3. **Mark Recipe as Abandoned** (Essential)
   - As a meal planner, I want to abandon recipes I no longer plan to cook
   - So that claimed ingredients are released back to inventory

**Key Acceptance Criteria** (TDD Seeds):
- Shopping list aggregates planned recipe ingredients minus claimed inventory items
- Purchase likelihood (0.0-1.0) groups Grocery items (≥0.3) vs Pantry Staples (<0.3)
- Grocery items sorted by likelihood descending (high confidence first)
- Cook action: delete claims + decrement inventory (atomic transaction)
- Abandon action: delete claims only (releases inventory, no consumption)
- Both actions idempotent (safe to call multiple times)
- Shopping list computed on-demand (not stored), aggregates by ingredient name

**Scope Boundaries**:
- ✅ In scope: All three stories, likelihood-based grouping, idempotent actions
- ❌ Out of scope: Copy-to-clipboard (UI fidelity pass), bulk lifecycle actions, recipe editing, history view

**Relevant Prototype Patterns**:
- Recipe lifecycle states validated (LEARNINGS.md:88-93): planned → cooked/abandoned
- Shopping list workflow validated (LEARNINGS.md:324-331): aggregation fills gap
- Claims are temporary (LEARNINGS.md:95-100): delete on cook/abandon, not consumed state
- Likelihood-based sourcing (LEARNINGS.md:233-240): force-ranked shopping list

## Implementation Phases

### Phase 1: Domain Model Foundation (Recipe + Claims) ✓

**Purpose**: Establish Recipe and IngredientClaim models with lifecycle state support. Foundation for all subsequent work.

**Scope**: Backend domain models, database schema

**TDD Focus**:
- **Validation behavior**: Recipe.state only accepts valid enum values (reject invalid states)
- **Constraint behavior**: IngredientClaim.quantity must be positive (reject zero/negative)
- **Relationship behavior**: Deleting Recipe cascades to IngredientClaims (verify claims deleted)
- Test approach: Behavior tests only - don't test "does field exist", test "what happens when I do X"
- **Note**: Skip tests that just verify schema (field types, defaults) - these are tautologies

**Key Considerations**:
- Recipe.state enum: planned, cooked, abandoned (no "consumed" state for claims)
- Recipe.ingredients stored as JSON (list of RecipeIngredient dicts with purchase_likelihood)
- IngredientClaim.state: only "reserved" (claims deleted on cook/abandon, not transitioned)
- Timestamps: Recipe.cooked_at set on cook action
- Foreign key CASCADE: deleting recipe deletes claims automatically
- **Testing philosophy**: Only test if there's validation logic or business rules. Simple field declarations don't need tests.

**Dependencies**: None (foundational phase)

**Complexity**: S

---

### Phase 2: Recipe Lifecycle Endpoints ✓

**Purpose**: Enable cook and abandon actions via REST API. Users can complete or cancel planned recipes.

**Scope**: Backend API endpoints for recipe lifecycle transitions

**TDD Focus**:
- POST /recipes/{id}/cook: transitions state, deletes claims, decrements inventory (atomic)
- POST /recipes/{id}/abandon: transitions state, deletes claims only (releases inventory)
- Idempotency: calling multiple times produces same result (no-op if already in target state)
- Error handling: 404 if recipe not found, 400 if invalid state transition
- Test approach: Integration tests with test database, verify inventory updates

**Key Considerations**:
- Atomic transactions: inventory updates and claim deletion must succeed/fail together
- Idempotency check: query Recipe.state first, return early if already cooked/abandoned
- Inventory decrement: query IngredientClaim → decrement InventoryItem.quantity → delete claims
- Response includes: recipe_id, new_state, claims_deleted count, inventory_items_decremented count
- Staleness: what if InventoryItem was deleted between planning and cooking? (handle gracefully)

**Dependencies**: Phase 1 complete (Recipe and IngredientClaim models exist)

**Complexity**: M

---

### Phase 3: Shopping List Data Layer

**Purpose**: Extend RecipeIngredient schema with purchase_likelihood and implement shopping list computation algorithm.

**Scope**: Backend domain logic for shopping list aggregation

**TDD Focus**:
- RecipeIngredient includes ingredient_source ("inventory" | "pantry" | "grocery") and purchase_likelihood
- Shopping list computation: aggregate planned recipes → subtract claimed inventory → group by threshold
- Quantity aggregation: simple string concatenation ("2 cups + 1 whole")
- Staleness mitigation: re-check current InventoryItems during aggregation (handles race condition)
- Test approach: Unit tests for aggregation logic, integration tests with recipe + inventory fixtures

**Key Considerations**:
- Purchase likelihood cached during flesh-out (assigned by LLM, stored in Recipe.ingredients JSON)
- Staleness mitigation: edge case where user adds inventory between flesh-out and shopping list (rare, but handled)
- Grouping threshold: Pantry Staples (<0.3) vs Grocery (≥0.3)
- Grocery items sorted descending by purchase_likelihood (high confidence first)
- Track which recipes use each ingredient (for "used in: Recipe A, Recipe B" display)

**Dependencies**: Phase 1 complete (Recipe model exists with ingredients JSON field)

**Complexity**: M

---

### Phase 4: Shopping List API Endpoint

**Purpose**: Expose shopping list via REST API with force-ranked grocery items and pantry verification.

**Scope**: Backend API endpoint returning computed shopping list

**TDD Focus**:
- GET /sessions/{session_id}/shopping-list: returns force-ranked shopping list
- Response schema: ShoppingListResponse with grocery_items and pantry_staples arrays
- Each item includes: ingredient_name, total_quantity, purchase_likelihood, used_in_recipes
- Empty response if no planned recipes in session
- Test approach: Integration tests with planned recipes + inventory + claims fixtures

**Key Considerations**:
- Computed on-demand (not stored) from Recipe.ingredients JSON + current InventoryItems
- Session-scoped: only planned recipes for this session
- No caching (always fresh, handles inventory changes between generations)
- Performance: aggregation is O(recipes × ingredients × inventory) but n is small (5-7 recipes, 30-50 ingredients)
- Response format enables UI to display single list with visual separator at 0.3 threshold

**Dependencies**: Phase 3 complete (shopping list computation logic exists)

**Complexity**: S

---

### Phase 5: BAML Prompt Enhancement (FleshOutRecipe)

**Purpose**: Update FleshOutRecipe BAML prompt to assign ingredient_source and purchase_likelihood for every ingredient.

**Scope**: BAML prompt engineering, prompt testing with real inventory

**TDD Focus**:
- LLM assigns ingredient_source for ALL ingredients (inventory, pantry, grocery)
- LLM assigns purchase_likelihood (0.0-1.0) for pantry and grocery ingredients
- Inventory ingredients matched by name (case-insensitive)
- Pantry staples judgment: LLM decides based on household context and quantity
- Test approach: Manual testing with diverse recipes, review LLM assignments for accuracy

**Key Considerations**:
- LLM has full context: recipe, household profile, current inventory state
- Better judgments than scoring ingredients in isolation later
- Likelihood guidance: high (>0.7) = definitely buy, medium (0.3-0.7) = grey area, low (<0.3) = probably have
- Example: "8 oz goat cheese" = high likelihood (0.9), "2 tsp salt" = low likelihood (0.1)
- Prompt iteration: test with edge cases (bulk quantities, unusual spices, fresh herbs)

**Dependencies**: Phase 3 complete (RecipeIngredient schema extended)

**Complexity**: M

---

### Phase 6: Frontend Integration

**Purpose**: Wire frontend to new endpoints, display shopping list and recipe lifecycle actions.

**Scope**: Frontend UI for shopping list view and cook/abandon buttons

**TDD Focus**:
- Shopping list view displays force-ranked items with visual separator at threshold
- Cook button sends POST request, updates UI on success
- Abandon button sends POST request, updates UI on success
- Error handling: display user-friendly messages on failure
- Test approach: Manual testing with browser, E2E tests if time permits

**Key Considerations**:
- Single list with horizontal rule separator at 0.3 threshold (Pantry Staples below, Grocery above)
- Progressive disclosure: "used in: Recipe A, Recipe B" visible but not overwhelming
- Optimistic UI updates: mark recipe as cooked immediately, rollback on error
- Cook/abandon button placement: on each planned recipe card
- No bulk actions (out of scope): individual recipes only

**Dependencies**: Phases 2, 4, 5 complete (endpoints exist, BAML assigns likelihood)

**Complexity**: M

---

## Sequencing Logic

**Why this order minimizes risk**:
1. Domain model first (Phase 1): foundation for all work, no dependencies
2. Lifecycle endpoints next (Phase 2): enables early testing of cook/abandon logic independently
3. Shopping list data layer (Phase 3): core algorithm, testable without API or BAML changes
4. Shopping list API (Phase 4): thin layer over Phase 3 logic, low complexity
5. BAML enhancement (Phase 5): prompt iteration needs domain model + API to test against
6. Frontend last (Phase 6): integrates all prior work, depends on working backend

**Where parallel work is possible**:
- Phase 3 (shopping list algorithm) can start while Phase 2 (lifecycle endpoints) is in progress
- Phase 5 (BAML prompt) can iterate in parallel with Phase 4 (API endpoint) if domain model is stable

**Where dependencies constrain sequencing**:
- Phase 2 depends on Phase 1 (needs Recipe/IngredientClaim models)
- Phase 4 depends on Phase 3 (needs computation logic)
- Phase 6 depends on Phases 2, 4, 5 (needs all backend pieces working)

**How phases build on each other**:
- Phase 1 → Phase 2: state machine enables lifecycle actions
- Phase 1 → Phase 3 → Phase 4: domain model → computation → API exposure
- Phase 5 enhances Phase 3: LLM assigns data that computation logic uses
- Phase 6 integrates everything: UI consumes APIs and displays data

## High-Level Test Strategy (TDD Throughout)

**Test-Driven Development approach**:
- Red-Green-Refactor cycle per phase
- Write failing test first (acceptance criteria → test case)
- Implement minimum code to pass
- Refactor with confidence

**Unit tests**:
- Model validation (Recipe state transitions, IngredientClaim relationships)
- Shopping list aggregation logic (quantity concat, grouping, sorting)
- Edge cases (empty inventory, no claims, invalid states)

**Integration tests**:
- API endpoints with test database fixtures
- Atomic transactions (cook action: verify inventory + claims updated together)
- Idempotency (calling cook twice produces same result)
- Shopping list computation with real Recipe + InventoryItem data

**Manual testing**:
- BAML prompt quality (LLM assignments feel right?)
- Frontend UX (shopping list readable? buttons work?)
- E2E flow (plan → shop → cook → verify inventory)

**Key scenarios to validate** (from acceptance criteria):
1. Shopping list excludes claimed inventory items (not already have it)
2. Shopping list groups by threshold (Grocery ≥0.3, Pantry <0.3)
3. Cook action decrements inventory correctly (atomic, idempotent)
4. Abandon action releases claims without consuming inventory
5. Staleness mitigation (inventory added between flesh-out and shopping list still excluded)

## Integration Points

**Backend**:
- Models: Recipe, IngredientClaim, InventoryItem (new/modified)
- API: New endpoints for cook, abandon, shopping list (3 endpoints)
- BAML: FleshOutRecipe prompt enhancement (assign ingredient_source + purchase_likelihood)
- Database: Schema changes (Recipe.state, Recipe.ingredients JSON structure)

**Frontend**:
- Components: Shopping list view, recipe lifecycle buttons (cook/abandon)
- State management: Update planned recipes on cook/abandon
- API calls: POST /recipes/{id}/cook, POST /recipes/{id}/abandon, GET /sessions/{session_id}/shopping-list

**BAML**:
- Prompt changes: FleshOutRecipe assigns ingredient_source and purchase_likelihood for every ingredient
- Schema changes: RecipeIngredient extends with new fields (ingredient_source, purchase_likelihood)

## Risk Assessment

**High Risks**:
1. **Atomic transaction failure** (cook action)
   - Risk: Inventory decremented but claims not deleted (or vice versa)
   - Mitigation: Use database transactions, test rollback scenarios
   - Contingency: Add transaction logging, manual cleanup tools if needed

2. **LLM likelihood judgment quality** (shopping list accuracy)
   - Risk: LLM assigns wrong likelihood (high for pantry staples, low for specialty items)
   - Mitigation: Prompt iteration with diverse examples, user feedback loop
   - Contingency: Manual likelihood override UI (deferred to post-MVP)
   - **Steering likelihood**: High - prompt quality requires human review and iteration

3. **Idempotency edge cases** (calling cook twice with concurrent requests)
   - Risk: Race condition if two clients call cook simultaneously
   - Mitigation: Database-level locking or check-then-update in transaction
   - Contingency: Accept rare double-decrement bug for MVP (fixable post-launch)

**Medium Risks**:
1. **Quantity aggregation ambiguity** (mixed units)
   - Risk: "2 cups + 1 whole onion" is clear, but "200g + 1 cup flour" is confusing
   - Mitigation: Simple string concat for MVP, accept imperfection
   - Contingency: Unit normalization library if users complain (post-MVP)

2. **Staleness mitigation complexity** (inventory race condition)
   - Risk: User adds inventory between flesh-out and shopping list, but LLM already assigned "grocery"
   - Mitigation: Re-check current inventory by name during aggregation (handles most cases)
   - Contingency: Accept rare false positive (shows on list even though you have it)

3. **Performance with large inventories** (shopping list computation)
   - Risk: O(recipes × ingredients × inventory) becomes slow with 100+ inventory items
   - Mitigation: Current scope (5-7 recipes, ~50 inventory items) is fast enough
   - Contingency: Add caching or indexing if performance degrades (unlikely for MVP)

**Contingency Plans**:
- If atomic transactions prove too complex: Accept eventual consistency, add manual reconciliation tools
- If LLM likelihood quality is poor: Prompt iteration with user, manual threshold override in UI
- If idempotency fails: Add request deduplication with client-generated idempotency keys

**Steering Likelihood**:
- **High steering**: BAML prompt iteration (Phase 5) - human judgment needed for likelihood quality
- **Medium steering**: Shopping list computation edge cases (Phase 3) - quantity aggregation decisions
- **Low steering**: Lifecycle endpoints (Phase 2) - clear acceptance criteria, straightforward implementation

## Implementation Notes

**TDD**: Test-Driven Development throughout all phases
- Write test first (acceptance criteria → failing test)
- Implement minimum code to pass
- Refactor with green tests
- Quality gate: all tests pass before moving to next phase

**Prototype patterns to follow**:
- Recipe model structure (prototype/app.py:47-61): state field, JSON ingredients, timestamps
- IngredientClaim pattern (prototype/app.py:63-72): recipe_id FK, ingredient_name, quantity, state
- SSE streaming pattern (src/backend/routes.py:260-394): for future recipe generation enhancements

**Prototype patterns to change**:
- Claims use "reserved" state only (no "consumed" state) - delete on cook/abandon
- Recipe.state uses enum validation (not free-text string)
- RecipeIngredient extends with ingredient_source and purchase_likelihood (new fields)

**Quality gates**:
- Phase completion criteria: all tests pass, acceptance criteria met
- Code review: peer review on PR before merge (if team exists)
- Manual testing: smoke test happy path after each phase
- Pre-commit hooks: ruff (Python) + prettier (frontend) pass

**General guidance**:
- Keep endpoints RESTful: POST for mutations, GET for queries
- Use Pydantic for request/response validation (FastAPI pattern)
- Database migrations: Use SQLModel metadata.create_all() for schema changes (prototype simplicity)
- Error handling: Return 4xx for client errors, 5xx for server errors with user-friendly messages
- Logging: Log lifecycle transitions and shopping list computations for debugging

## Overall Complexity Estimate

**Overall**: M (Medium)

**Confidence**: High

**Justification**:
- **Decision density**: Moderate - BAML prompt iteration requires judgment (Phase 5), but most phases have clear acceptance criteria
- **Novel patterns**: Low - lifecycle state machine is straightforward, shopping list is aggregation logic (no new architectural patterns)
- **Integration points**: Moderate - 3 systems affected (backend, frontend, BAML) but changes are localized
- **Context coordination**: Moderate - recipe lifecycle and shopping list share IngredientClaim concept, but phases are mostly independent
- **Steering likelihood**: Medium - BAML prompt quality needs human oversight, but endpoints and algorithm are spec-driven

**Breakdown by phase**:
- Phase 1 (Domain Model): S - clear schema, established patterns
- Phase 2 (Lifecycle Endpoints): M - atomic transactions require care, idempotency testing
- Phase 3 (Shopping List Logic): M - aggregation algorithm, staleness mitigation edge cases
- Phase 4 (Shopping List API): S - thin layer over Phase 3
- Phase 5 (BAML Prompt): M - iterative prompt engineering, human review needed
- Phase 6 (Frontend): M - multiple UI changes, error handling, integration testing

**Complexity drivers**:
1. Atomic transactions in Phase 2 (ensure consistency)
2. BAML likelihood judgment quality in Phase 5 (prompt iteration)
3. Integration across 3 systems in Phase 6 (coordination overhead)
4. Idempotency and error handling across lifecycle actions

Overall: Moderate complexity, high confidence in success. Most phases follow established patterns (CRUD endpoints, JSON aggregation). Main uncertainty is BAML prompt quality for likelihood assignments (requires human review and iteration).
