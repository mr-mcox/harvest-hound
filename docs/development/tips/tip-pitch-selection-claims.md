---
date: 2025-12-07
feature: pitch-selection-claims
status: draft
frame: .scratch/frame-pitch-selection-claims.md
estimated_effort: S
confidence: High
tags: [mvp, claiming, recipe-generation, multi-wave, session-scoped]
---

# TIP: Pitch Selection → Flesh Out → Ingredient Claiming

## Context

### Problem Statement
Users need to select promising pitches, flesh them out into complete recipes, and have ingredients automatically claimed to prevent double-booking in subsequent generation waves. The current implementation generates and displays pitches but has no selection or claiming mechanism, making iterative multi-wave generation impossible.

**From Prototype Discovery**: Two-phase recipe browsing validated (pitches → selection → flesh out). Ingredient claiming is CRITICAL for multi-wave generation - without it, second wave reuses already-claimed ingredients (LEARNINGS.md:40-44). Complete ingredient claiming required - EVERY ingredient assigned to source (LEARNINGS.md:202-208).

### User Stories (Essential)

1. **Select Multiple Pitches for Flesh Out**
   - User can click/tap pitch cards to mark them as selected (visual indicator)
   - User can deselect pitches before fleshing out
   - Selected pitches persist during page session
   - "Flesh Out Selected" button visible when 1+ pitches selected

2. **Flesh Out Selected Pitches Into Complete Recipes**
   - User clicks "Flesh Out Selected" to start batch generation
   - System generates complete recipe for each selected pitch via BAML
   - Recipes saved to database with all required fields
   - Progress indicator shown during generation
   - Fleshed-out recipes removed from pitch pool (no longer selectable)
   - Recipe state initialized as "planned"

3. **Claim Ingredients From Inventory with Quantity Tracking**
   - When recipe fleshed out, system creates IngredientClaim records for inventory items
   - Claims track: ingredient name, quantity, unit, recipe association, inventory item FK
   - Claims are "reserved" state initially (not yet consumed)
   - Only ingredients matching inventory items are claimed (grocery/pantry deferred)
   - Claim creation happens transparently and atomically

4. **Generate More Pitches Respecting Claims**
   - "Generate More" uses same button as initial pitch generation
   - System calculates decremented inventory state (original - claimed quantities)
   - Generates pitches with decremented inventory passed to BAML
   - New pitches naturally use remaining inventory (auto-pivot via quantity awareness)

### Key Acceptance Criteria (TDD Seeds)

- Pitch multi-select with visual feedback and batch action
- Complete recipe generation with structured ingredients
- Atomic IngredientClaim creation for inventory items only (all succeed or fail together)
- Multi-wave generation respects decremented inventory via quantity awareness
- Client-side pitch filtering after flesh-out (thin client approach)

### Scope Boundaries

**In Scope**:
- Recipe entity with structured ingredients (JSON storage, Pydantic validation, session-scoped)
- IngredientClaim entity with FK to InventoryItem (inventory items only)
- Claim-aware multi-wave generation via decremented inventory
- Recipe lifecycle state (planned/cooked/abandoned) - state field only, actions deferred

**Out of Scope (Deferred)**:
- Grocery/pantry ingredient source assignment and purchase likelihood (separate TIP for shopping list)
- Cook/Abandon actions (lifecycle transitions from planned state)
- Shopping list view (separate feature)
- Pitch invalidation UI (graying out/removing pitches when ingredients exhausted)
- Claims visibility UI (showing which ingredients are claimed)
- Recipe editing after planning

### Relevant Prototype Patterns

**Implementation patterns to follow**:
- SSE streaming for generation: `prototype/app.py:418-493` - GET endpoint with EventSource compatibility
- BAML sequential generation: `prototype/baml_src/recipes.baml:40-105` - GenerateRecipePitches function structure
- Inventory state management: `prototype/app.py:131-178` - load_initial_inventory() and load_available_inventory() patterns
- Claim entity structure: `prototype/app.py:63-72` - IngredientClaim model with state tracking

**Test patterns**:
- Prototype has no tests (YOLO discovery phase per `prototype/CLAUDE.md`)
- MVP needs tests on business logic and BAML generation
- Example test case: Pitch "mac and cheese" with macaroni + cheese in inventory → both claimed

**Key learnings that inform this feature**:
- Quantity-aware claiming works smoothly, no edge cases found (LEARNINGS.md:74-80)
- LLM declares, code manages state - architectural win (LEARNINGS.md:409-418)
- Auto-save on flesh-out feels natural (LEARNINGS.md:88-93)
- Session-scoped recipes with canonical migration path (LEARNINGS.md:660-666)
- IngredientClaim only for inventory items (LEARNINGS.md:668-674)
- Decremented inventory pattern for multi-wave (LEARNINGS.md:676-681)

---

## Implementation Phases

### Phase 1: Recipe Entity with Structured Ingredients ✓

**Purpose**: Establish Recipe schema with structured ingredients (preparation field) as foundation for claiming logic. Sequenced first because claiming depends on recipe structure.

**Scope**: Backend domain model, database schema, Pydantic validation

**TDD Focus**:
- Acceptance criterion: Recipe saved with structured ingredients
- Test approach: Unit tests for Recipe model validation, JSON serialization round-trip

**Key Considerations**:
- Store ingredients as JSON list (not normalized tables) for flexibility
- Pydantic schema enforces structure: quantity (str), unit (str), name (str), preparation (str|None), notes (str|None)
- Quantity as string handles ranges, "to taste", approximations
- Preparation field solves shopping list prep leak (LEARNINGS.md:335-341)
- Recipe fields: id, session_id (future), criterion_id (future), name, description, ingredients (JSON), instructions (list[str]), times, servings, state, notes, timestamps

**Dependencies**: None

**Complexity**: XS

---

### Phase 2: IngredientClaim Entity for Inventory Reservations

**Purpose**: Create IngredientClaim entity for tracking inventory item reservations. Sequenced after Recipe entity because claims reference recipes.

**Scope**: Backend domain model, database schema, InventoryItem FK

**TDD Focus**:
- Acceptance criterion: Claim creation with inventory_item_id FK to InventoryItem
- Test approach: Unit tests for IngredientClaim creation, FK constraint validation

**Key Considerations**:
- IngredientClaim fields: id, recipe_id (FK), inventory_item_id (FK to InventoryItem), ingredient_name, quantity (float), unit, state (reserved/consumed), timestamps
- Claims only for inventory items (grocery/pantry deferred to shopping list TIP)
- State field supports future cook/abandon workflow (reserved → consumed)
- Simplified schema: No source_type, source assignment, or purchase_likelihood fields

**Dependencies**: Phase 1 (Recipe entity)

**Complexity**: XS

---

### Phase 3: FleshOutRecipe BAML Function

**Purpose**: Create new BAML function to generate complete recipes from selected pitches. Sequenced here to enable claiming logic in next phase.

**Scope**: BAML prompt engineering, structured output schema

**TDD Focus**:
- Acceptance criterion: Generate complete recipe with structured ingredients from pitch
- Test approach: Integration tests with sample pitches, validate recipe structure, ingredient format

**Key Considerations**:
- FleshOutRecipe function inputs: pitch data (name, key ingredients), household context, inventory state (explicit + definition stores)
- Structured output: Recipe with ingredients (name, quantity, unit, preparation), instructions, times, servings
- Use GenerateSingleRecipe as template pattern from prototype
- Household profile + pantry staples + inventory context pattern from prototype
- NO source assignment in this function (grocery/pantry deferred to shopping list TIP)
- Focus on recipe generation quality and pitch fidelity

**Dependencies**: Phase 2 (IngredientClaim schema)

**Complexity**: S

---

### Phase 4: Flesh-Out Endpoint with Atomic Claim Creation

**Purpose**: Implement POST endpoint to flesh out selected pitches, save recipes, and create ingredient claims atomically. Critical integration point - recipe generation + persistence + claiming must succeed/fail together.

**Scope**: Backend API, database transactions, claim creation logic, error handling

**TDD Focus**:
- Acceptance criterion: All claims for a recipe succeed or fail together (atomic)
- Test approach: Integration tests with rollback scenarios, validate claim quantities match recipe ingredients, test inventory matching logic

**Key Considerations**:
- Endpoint: POST /flesh-out-pitches (batch operation for selected pitches)
- For each pitch: call FleshOutRecipe BAML → save Recipe → create IngredientClaims
- Atomic transaction: Use SQLModel session commit for all claims per recipe
- Ingredient matching: Try exact match against inventory items by name
- Create IngredientClaim only for matched inventory items (skip non-inventory ingredients)
- InventoryItem lookup: Query by ingredient name, cache in dict for batch efficiency
- Return: Saved recipes with claim summaries for frontend display

**Dependencies**: Phase 3 (FleshOutRecipe BAML)

**Complexity**: S

---

### Phase 5: Claim-Aware Multi-Wave Generation

**Purpose**: Ensure GenerateRecipePitches respects claimed ingredients by passing decremented inventory state. Enables iterative "pick some → generate more" workflow.

**Scope**: Backend inventory calculation validation

**TDD Focus**:
- Acceptance criterion: Second wave pitches use decremented quantities, naturally avoid exhausted ingredients
- Test approach: Integration test with multi-wave scenario (generate → select → flesh out → generate more), validate decremented inventory state

**Key Considerations**:
- Calculate decremented inventory: Query reserved claims, sum by ingredient name, subtract from physical inventory
- Pass decremented inventory state to BAML in explicit_stores (quantities reduced)
- NO "DO NOT use" constraint needed - LLM pivots naturally via quantity awareness (LEARNINGS.md:676-681)
- API: Reuse existing GET /generate-pitches endpoint, already uses load_available_inventory() per `prototype/app.py:442`
- Prototype already implements this correctly - verify behavior in tests
- Auto-pivot validated in prototype (LEARNINGS.md:390-396)

**Dependencies**: Phase 4 (Claim creation)

**Complexity**: XS

---

### Phase 6: Frontend Multi-Select UI

**Purpose**: Add client-side multi-select interaction for pitch cards with visual feedback and batch action trigger. Sequenced after backend ready to minimize rework.

**Scope**: Frontend JavaScript, UI state management, visual indicators

**TDD Focus**:
- Acceptance criterion: User can select/deselect pitches, see count, trigger batch action
- Test approach: Manual testing (minimal frontend tests per user guidance)

**Key Considerations**:
- Click pitch card to toggle selected state (visual indicator: border/background change)
- Maintain selected pitch array in client state (pitch names or indices)
- Show/hide "Flesh Out Selected" button based on selection count > 0
- Button disabled state when count = 0
- Client-side filtering: Remove fleshed-out pitches from display after successful flesh-out (thin client approach)
- Session persistence: Selected state persists during page session (not across refresh)

**Dependencies**: Phase 5 (Backend complete)

**Complexity**: S

---

### Phase 7: Batch Flesh-Out Frontend Integration

**Purpose**: Connect frontend multi-select UI to flesh-out endpoint with progress indication during batch generation. Final integration point completing the full workflow.

**Scope**: Frontend API integration, progress UI, error handling, state updates

**TDD Focus**:
- Acceptance criterion: Selected pitches generate recipes with progress feedback
- Test approach: Manual testing with real multi-pitch selection

**Key Considerations**:
- On "Flesh Out Selected" click: Send selected pitch data to POST /flesh-out-pitches
- Progress indicator: Show during API call (spinner or status text)
- Success handling: Display generated recipes, update inventory state awareness, remove fleshed-out pitches from pool
- Error handling: Show error message, preserve selection state for retry
- Recipe display: Add to "My Planned Recipes" section at top of page
- Update client inventory tracking: Decrement quantities based on claims (for next "Generate More")
- Clear selection state after successful flesh-out

**Dependencies**: Phase 6 (Frontend multi-select)

**Complexity**: S

---

## Sequencing Logic

**Why this order minimizes risk**:
1. Phases 1-2 establish data model foundation (Recipe + IngredientClaim) before generation logic
2. Phase 3 (BAML) developed after schema finalized to avoid rework from schema changes
3. Phase 4 implements claiming logic with atomic guarantees before multi-wave
4. Phase 5 validates multi-wave behavior (mostly already implemented in prototype)
5. Phases 6-7 implement frontend after backend complete to minimize coordination churn

**Where parallel work is possible**:
- Phase 3 (BAML) could start in parallel with Phase 2 (IngredientClaim entity) if BAML schema assumptions hold
- Phase 6 (Frontend multi-select UI) could start early as static prototype, integrated in Phase 7

**Where dependencies constrain sequencing**:
- Phases 1→2→4 are sequential (Recipe → Claim entity → Claim creation logic)
- Phase 3 must complete before Phase 4 (BAML function needed for flesh-out endpoint)
- Phase 5 depends on Phase 4 (multi-wave needs claim creation working)
- Phase 7 depends on Phases 4-6 (integration needs backend + frontend pieces)

**How phases build on each other**:
- Domain model (Phases 1-2) → Generation logic (Phase 3) → Persistence + claiming (Phase 4) → Multi-wave validation (Phase 5) → User interaction (Phases 6-7)

---

## High-Level Test Strategy

**TDD throughout with red-green-refactor cycle per phase**:
- Write failing test first
- Implement minimal code to pass
- Refactor for clarity
- Commit

**Test categories by phase**:

**Phase 1-2 (Domain Model)**:
- Unit tests: Model validation, JSON serialization, FK constraints
- Focus: Schema correctness, data integrity

**Phase 3 (BAML)**:
- Integration tests: Sample pitch inputs → validate structured recipe outputs
- Scenarios: Recipe structure correctness, ingredient format (name, quantity, unit, preparation), different inventory states
- Example: "Mac and cheese" pitch → validate complete recipe with structured ingredients

**Phase 4 (Claiming Logic)**:
- Integration tests: End-to-end flesh-out flow with claim creation
- Scenarios: Atomic transaction (rollback on partial failure), inventory matching, InventoryItem FK resolution
- Example: "Mac and cheese" recipe with macaroni + cheese in inventory → both ingredients get IngredientClaims with correct FKs

**Phase 5 (Multi-Wave)**:
- Integration tests: Multi-wave generation flow
- Scenarios: Generate → select → flesh out → generate more → validate no claimed ingredient reuse, decremented quantities accurate
- Example: Use 2 lbs carrots in wave 1 → wave 2 receives 0 lbs carrots in inventory state

**Phase 6-7 (Frontend)**:
- Minimal automated tests (per user guidance)
- Manual testing: Multi-select interaction, batch action, progress indication, error states
- Integration test: E2E workflow from pitch selection to recipe display

**Key test scenarios (from acceptance criteria)**:
1. Multi-select pitches → flesh out → recipes saved with structured ingredients
2. Ingredient claiming → inventory items matched and claimed with correct FK references
3. Atomic claim creation → all succeed or rollback on failure
4. Multi-wave generation → decremented inventory passed to BAML, natural pivot to remaining ingredients
5. Client filtering → fleshed-out pitches removed from display

---

## Integration Points

**Backend**:
- Recipe model: New entity, fields, JSON ingredient storage, session-scoped
- IngredientClaim model: New entity with FK to InventoryItem, Recipe
- InventoryItem model: Existing, queried for ingredient matching
- Inventory calculation: Validate load_available_inventory() for decremented state (already implemented in prototype)
- API endpoints: New POST /flesh-out-pitches, validate GET /generate-pitches behavior
- Database migrations: New tables for Recipe, IngredientClaim

**Frontend**:
- Pitch display: Add selection UI to existing pitch cards
- Recipe display: New "My Planned Recipes" section
- State management: Track selected pitches, fleshed-out recipes
- API integration: Flesh-out endpoint, batch operations

**BAML**:
- New FleshOutRecipe function: Structured output for complete recipe generation
- GenerateRecipePitches: No changes needed (already receives decremented inventory from load_available_inventory)

---

## Risk Assessment

**High Risks**:

1. **Atomic claim creation complexity**
   - Risk: Partial claim creation on error, data inconsistency
   - Mitigation: Single transaction per recipe with rollback, comprehensive error handling
   - Contingency: Add claim validation endpoint to detect/repair orphaned claims

2. **Ingredient name matching accuracy**
   - Risk: Ingredient names from recipe don't match inventory item names (e.g., "macaroni" vs "elbow pasta")
   - Mitigation: Start with exact string matching, monitor match rate in tests
   - Contingency: Add fuzzy matching or normalization if exact matching insufficient (<70% match rate)

**Medium Risks**:

1. **Multi-wave inventory state synchronization**
   - Risk: Frontend and backend inventory state diverge, double-booking ingredients
   - Mitigation: Backend always authoritative (load_available_inventory), frontend awareness of decremented state
   - Contingency: Add inventory state refresh endpoint for frontend reconciliation

2. **Client-side filtering complexity**
   - Risk: Filtering logic fragile, pitches reappear incorrectly
   - Mitigation: Simple index/name-based filtering, comprehensive manual testing
   - Contingency: Move to server-side pitch state tracking if client-side proves buggy

**Steering Likelihood**:

- **BAML prompt engineering** (Phase 3): May need iteration on recipe generation quality, pitch fidelity. Human judgment needed for prompt refinement.
- **Ingredient matching logic** (Phase 4): Name matching strategy may need adjustment based on real data (exact vs fuzzy).
- **Frontend UX** (Phases 6-7): Visual design for selection state, progress indication may need course correction based on feel.

---

## Implementation Notes

**TDD**: Test-Driven Development throughout all phases
- Write tests first (red)
- Implement minimal code (green)
- Refactor for clarity
- Commit and move to next test

**Prototype patterns to follow**:
- SSE streaming: `prototype/app.py:418-493` - EventSource-compatible GET endpoint
- BAML sequential generation: `prototype/baml_src/recipes.baml:40-105` - Household context + inventory structure
- Inventory state calculation: `prototype/app.py:154-178` - Decremented state from reserved claims
- Claim entity: `prototype/app.py:63-72` - State tracking (reserved/consumed)

**Prototype patterns to change**:
- Recipe ingredients: Change from JSON string blob (`ingredients_json`) to structured JSON list with preparation field
- IngredientClaim: Add inventory_item_id FK field (prototype uses store_name string)
- Recipe entity: Add session_id field (enables future canonical split)

**Quality gates**:
- All tests passing before phase completion
- BAML generation quality: Validate recipe structure and ingredient format correctness
- Atomic claim creation: Zero orphaned claims in error scenarios
- Multi-wave generation: Zero double-booked ingredients in integration tests
- Ingredient matching: Monitor match rate, adjust strategy if <70%

**General guidance**:
- Use thin client approach (client-side filtering) unless bugs force server-side state
- InventoryItem lookup: Cache ingredient name→ID dict for batch operations efficiency
- Error handling: Graceful degradation (save recipe even if claim creation fails, log for manual review)
- Start with exact name matching for ingredients, add fuzzy matching only if needed

---

## Overall Complexity Estimate

**Overall**: S (Simple)

**Confidence**: High

**Justification**:

**What drives complexity**:
- **Integration points**: Recipe + IngredientClaim + InventoryItem + BAML + Frontend coordination (5 systems)
- **Atomic transaction requirements**: Claim creation must be bulletproof, no partial failures
- **Ingredient name matching**: Exact matching may need fuzzy fallback

**Why confidence is high**:
- Prototype validated claiming works smoothly (LEARNINGS.md:74-80)
- Clear patterns to follow from prototype (SSE, inventory state, claim entity)
- LLM/code separation proven successful (LEARNINGS.md:409-418)
- User confirmed simplified architecture (inventory claims only, descoped grocery/pantry)
- Well-defined acceptance criteria from feature frame
- Decremented inventory pattern already implemented in prototype

**Why not higher complexity**:
- Grocery/pantry source assignment descoped (significant simplification)
- Multi-wave generation already mostly implemented in prototype
- No novel BAML functions (FleshOutRecipe similar to GenerateSingleRecipe)
- Established patterns for most components (SSE streaming, BAML generation, SQLModel ORM)
- Thin client approach minimizes frontend complexity

**Why not lower complexity**:
- Atomic transaction guarantees require implementation care
- Ingredient name matching may need iteration
- Test coverage on business logic and BAML generation adds thoroughness
- Multiple integration points require coordination

**Complexity by phase**:
- Phases 1-2: XS (straightforward data modeling)
- Phase 3: S (BAML function similar to prototype pattern)
- Phase 4: S (claim creation logic simplified by inventory-only scope)
- Phase 5: XS (validate existing prototype behavior)
- Phases 6-7: S (thin client, minimal frontend tests)

**Decision density**: Low - Most patterns established in prototype. Main decision point is ingredient matching strategy (exact vs fuzzy).

**Steering needs**: Light oversight for BAML prompt refinement (Phase 3), ingredient matching edge cases (Phase 4). Expect 1-2 minor course corrections during implementation.
