---
date: 2025-12-06
feature: initial-generation
status: draft
frame: .scratch/frame-initial-generation.md
estimated_effort: M
confidence: High
tags: [mvp, steel-thread, session, baml, sse]
---

# Technical Implementation Plan: Initial Recipe Generation with Session & Criteria

## Context

### Problem Statement
Users need to plan meals with structured constraints (quick weeknights, guest meals, leftovers, etc.) rather than generating a flat pool of pitches. Real meal planning requires grouping by meal type/criteria to ensure balanced variety for the week.

### User Stories (Essential)
1. **Create Session**: Named planning session for a specific week (persisted, multiple sessions allowed)
2. **Add Meal Criteria**: Criteria with counts (min 1, max 7) that structure the week's needs
3. **Generate Grouped Pitches**: 3x pitches per criterion slot, streamed via SSE
4. **View Pitches Organized**: Pitches displayed grouped by criterion (read-only, no selection)

### Key Acceptance Criteria (TDD Seeds)
- Session persists across page refreshes
- Minimum 1 criterion, maximum 7 criteria per session
- 3x pitch generation per criterion slot
- SSE streaming with progress feedback
- Pitches saved to database and grouped by criterion in UI
- Auto-generated session name "Week of [prior Sunday]" if blank (client-side)

### Scope Boundaries
**In scope**: Session creation, criteria management, sequential pitch generation, SSE streaming, grouped display

**Out of scope** (deferred):
- Pitch selection interaction
- Ingredient claiming
- Multi-wave generation
- Pitch invalidation UI
- Criterion editing after generation
- Session archival/history view

### Relevant Prototype Patterns
- **BAML household profile pattern** (prototype/baml_src/recipes.baml:40-105): Baked-in context + dynamic inventory
- **SSE streaming pattern** (prototype/app.py:418-493): GET endpoint for EventSource compatibility
- **SQLModel schema pattern** (prototype/app.py:27-81): UUID primary keys, foreign key relationships
- **BAML test pattern** (prototype/baml_src/inventory.baml:79-187): Embedded tests for parsing validation
- **Technique diversity prompt** (LEARNINGS.md:420-428): Critical for CSA item variety

### Key Learnings
- Structured meal planning workflow validated (LEARNINGS.md:276-283)
- 3x unfilled meal slots sizing validated (LEARNINGS.md:282)
- Session persistence transforms UX to weekly hub (LEARNINGS.md:102-107)
- Sequential generation cleaner for SSE, optimize later
- Pitch persistence simpler than ephemeral state during streaming

---

## Implementation Phases

### Phase 1: Domain Models & Database Setup ✓

**Purpose**: Establish foundational data models and relationships for sessions, criteria, and pitches. TDD approach validates model constraints before building features on top.

**Scope**:
- Session, MealCriterion, Pitch SQLModel classes
- Database schema with foreign key relationships
- Model-level validations (max 7 criteria)
- Database initialization and connection setup

**TDD Focus**:
- Acceptance: Session persists across page refreshes
- Acceptance: Max 7 criteria per session
- Test approach: Unit tests for model validations and relationships

**Key Considerations**:
- Follow prototype's UUID primary key pattern (prototype/app.py:27-81)
- Session → MealCriteria (one-to-many)
- MealCriterion → Pitches (one-to-many)
- Pitch persistence decision: save pitches to DB (simpler than ephemeral during SSE streaming)
- Database file location (SQLite): consistent with prototype pattern

**Dependencies**: None (foundational)

**Complexity**: S

**Implementation notes**:
- Created PlanningSession, MealCriterion, Pitch models with UUID primary keys
- Enabled SQLite foreign key support for CASCADE deletes
- Validation for min slots deferred to API layer (SQLModel validation inconsistent)
- Renamed `key_ingredients` → `inventory_ingredients` (clearer purpose: ingredients from tracked inventory, not pantry/grocery)
- Trimmed model tests to focus on CASCADE behavior only (CRUD tested via API integration tests)
- All tests passing (2 CASCADE delete tests, 34 total)

---

### Phase 2: Session CRUD Foundation ✓

**Purpose**: Enable session creation, listing, and viewing through API and UI. Establishes navigation pattern for session-scoped workflows.

**Scope**:
- FastAPI routes for session CRUD (create, list, view by ID)
- API endpoints with JSON responses
- Main page UI with "Create Session" button
- Session list view
- Session detail route/page (empty state initially)

**TDD Focus**:
- Acceptance: User can create session with optional name
- Acceptance: Session list persists across page refreshes
- Test approach: API integration tests for CRUD operations

**Key Considerations**:
- Dedicated route for session detail (not modal)
- Auto-name generation "Week of [prior Sunday]" happens client-side (user sees preview)
- Multiple sessions allowed (not just one active)
- SvelteKit routing pattern for `/sessions/:id`
- API returns created session with generated ID

**Dependencies**: Phase 1 (models must exist)

**Complexity**: S

**Implementation notes**:
- Added session CRUD endpoints in routes.py (POST /api/sessions, GET /api/sessions, GET /api/sessions/{id})
- SessionCreate/SessionResponse Pydantic models for API serialization
- Main page updated with create form + session list (Svelte 5 runes syntax)
- Auto-name generation "Week of [prior Sunday]" implemented client-side
- Session detail page at /sessions/[id] with placeholder for Phase 3
- All tests passing (41 total, 7 new session API tests)

---

### Phase 3: Meal Criteria Management ✓

**Purpose**: Enable users to define meal constraints within a session, validating the structured planning workflow.

**Scope**:
- API endpoints to add/remove criteria for a session
- Validation logic (min 1, max 7 criteria)
- UI for criterion input (description text field + slots number input)
- Display criteria list within session detail page
- Basic delete functionality per criterion

**TDD Focus**:
- Acceptance: Min 1 criterion before generation allowed
- Acceptance: Max 7 criteria validation enforced
- Test approach: API validation tests, UI state tests

**Key Considerations**:
- Simple form: text field (description) + number input (slots)
- Validation happens server-side (min 1 for generation, max 7 always)
- Client-side validation feedback (disable "Generate All" if < 1 criterion)
- Criteria display in session detail view
- Delete criterion removes from DB and updates UI

**Dependencies**: Phase 2 (need session detail page)

**Complexity**: S

**Implementation notes**:
- Added POST/GET/DELETE endpoints for criteria in routes.py
- Max 7 criteria validation enforced server-side with 400 response
- Session detail page updated with criteria form (description + slots) and list
- UI shows criteria count and disables form at max
- Placeholder for Phase 5 "Generate Pitches" button (disabled until criteria exist)
- All tests passing (48 total, 7 new criteria API tests)

---

### Phase 4: BAML Recipe Pitch Generation ✓

**Purpose**: Port and adapt prototype BAML prompts to generate pitches per criterion with household context and technique diversity.

**Scope**:
- BAML prompt for pitch generation (household profile + inventory + criterion context)
- Adapt prototype's GenerateRecipePitches for per-criterion generation
- Technique diversity prompt guidance
- Sequential generation per criterion (not batched)
- BAML tests for prompt validation

**TDD Focus**:
- Acceptance: 3x pitches generated per criterion slot
- Acceptance: Pitches reflect criterion context
- Test approach: BAML tests validating prompt structure and output

**Key Considerations**:
- Port household profile pattern from prototype/baml_src/recipes.baml:40-105
- Pass criterion description as additional context to BAML
- Generate `3 * criterion.slots` pitches per criterion
- Technique diversity critical for CSA items (LEARNINGS.md:420-428)
- Sequential calls (one BAML call per criterion) for simple implementation
- BAML function signature: `GenerateCriterionPitches(criterion_desc, num_pitches, inventory, household_profile)`

**Dependencies**: Phase 1 (need Pitch model structure)

**Complexity**: M

**Implementation notes**:
- Created recipes.baml with RecipePitch and PitchIngredient classes
- RecipePitch fields: name, blurb, why_make_this, inventory_ingredients (PitchIngredient[]), active_time_minutes
- PitchIngredient has name, quantity, unit - supports future ingredient claiming
- Updated Pitch model to store inventory_ingredients as list[dict] with {name, quantity, unit}
- GenerateRecipePitches function takes: inventory, pantry_staples, grocery_stores, household_profile, additional_context, num_pitches
- Grocery stores parameter constrains recipes to ingredients obtainable from listed stores (prevents sushi-grade tuna if only Cub available)
- Household profile passed as parameter (loaded from DB settings, not baked in)
- Simplified diversity guidance: ingredients can repeat, focus on technique variety without forcing it
- Inventory format includes source grouping for context
- Priority-based guidance instead of "spoil soon" language
- Added 3 BAML tests: basic generation, num_pitches respect, inventory ingredients with quantities validation
- Increased Anthropic max_tokens from 1024 to 4096 for multi-pitch generation
- All 48 Python tests passing, all 10 BAML tests passing

---

### Phase 5: SSE Streaming & Pitch Persistence ✓

**Purpose**: Stream pitch generation results incrementally to frontend, saving to database as they arrive. Enables progress feedback during generation.

**Scope**:
- GET endpoint for streaming pitch generation (EventSource compatible)
- Query params: session_id, criterion_id (or generate all criteria)
- Sequential BAML calls per criterion
- SSE event format with progress indicators
- Save pitches to DB as they're generated
- Frontend EventSource handling with progress UI

**TDD Focus**:
- Acceptance: SSE streaming provides progress feedback
- Acceptance: Pitches saved to database linked to session + criterion
- Test approach: Integration tests for streaming endpoint, manual testing for SSE events

**Key Considerations**:
- GET endpoint pattern from prototype/app.py:418-493 (EventSource requires GET)
- Query params for session_id (EventSource can't use POST body)
- Stream format: `data: {criterion_id, pitch_index, total, pitch_data}\n\n`
- Completion event: `data: {complete: true}\n\n`
- Error handling: stream error events
- Save pitch to DB immediately upon generation (enables refresh during generation)
- Load current inventory from DB for generation context

**Dependencies**: Phase 3 (need criteria), Phase 4 (need BAML function)

**Complexity**: M

**Implementation notes**:
- Created GET `/api/sessions/{session_id}/generate-pitches` endpoint with SSE streaming
- Loads household profile, pantry, grocery stores, and inventory from DB
- Formats inventory grouped by store with priority labels
- Sequential BAML calls per criterion (one call generating 3*slots pitches)
- Streams progress events (criterion start) and pitch events (each pitch saved)
- Saves pitches to DB immediately with inventory_ingredients JSON field
- Frontend EventSource handling with real-time progress display
- Error handling for connection loss and backend errors
- Extracted `_format_inventory_text` helper to meet complexity limits
- All 48 Python tests passing, all 10 BAML tests passing
- Manual browser testing confirms streaming works end-to-end

---

### Phase 6: Pitch Display & Grouping UI

**Purpose**: Display generated pitches grouped by criterion, completing the read-only browsing experience.

**Scope**:
- Load pitches for session from database
- Group pitches by criterion
- Display pitch cards (name, blurb, why_make_this, key ingredients, active time)
- Integrate pitch display into session detail view
- Empty states for criteria with no pitches

**TDD Focus**:
- Acceptance: Pitches displayed grouped by criterion
- Acceptance: Pitch shows required fields (name, blurb, etc.)
- Test approach: Component tests for pitch display, integration test for grouping logic

**Key Considerations**:
- Load all pitches for session (query: `WHERE session_id = ? ORDER BY criterion_id, created_at`)
- Group by criterion_id in backend or frontend (frontend grouping simpler for now)
- Pitch card displays: name, emotional blurb, why_make_this, key ingredients list, active time
- Simple functional UI (cards or list, no fancy styling per MVP charter)
- Empty state: "No pitches yet" for criteria without generation
- "Generate All" button triggers Phase 5 endpoint

**Dependencies**: Phase 5 (need pitches in database)

**Complexity**: S

---

## Sequencing Logic

**Why this order minimizes risk**:
1. **Database first** (Phase 1): Foundation for all features, cheapest to change early
2. **Session CRUD** (Phase 2): Establishes navigation before adding complexity
3. **Criteria management** (Phase 3): Validates structured input before generation
4. **BAML adaptation** (Phase 4): Isolated prompt work, can test independently
5. **Streaming integration** (Phase 5): Combines BAML + API + persistence, most complex
6. **Display UI** (Phase 6): Consumes generated data, easiest to iterate on

**Where parallel work is possible**:
- Phase 4 (BAML) can start after Phase 1 completes (doesn't need session UI)
- Phase 2 and 3 must be sequential (criteria needs session detail page)

**Where dependencies constrain sequencing**:
- Phase 5 requires Phase 3 + 4 (needs criteria and BAML function)
- Phase 6 requires Phase 5 (needs pitches in database)

**How phases build on each other**:
- Each phase enables the next without rework
- Early phases validate database schema before complex features
- BAML work isolated from API work until integration (Phase 5)

---

## High-Level Test Strategy

**TDD throughout all phases** with red-green-refactor cycle:

**Phase 1**: Model validation tests (max criteria, relationships)
**Phase 2**: API integration tests (session CRUD endpoints)
**Phase 3**: Validation tests (min/max criteria enforcement)
**Phase 4**: BAML prompt tests (embedded in .baml files following prototype pattern)
**Phase 5**: Streaming endpoint integration tests, manual SSE testing
**Phase 6**: Component tests for pitch cards, grouping logic tests

**Key scenarios to validate** (from acceptance criteria):
- Session persists across page refreshes (Phase 2)
- Auto-name generation client-side (Phase 2)
- Min 1, max 7 criteria validation (Phase 3)
- 3x pitch generation per criterion (Phase 4, 5)
- SSE progress feedback (Phase 5)
- Pitches grouped by criterion (Phase 6)

**Testing approach per phase**:
- Domain models: Unit tests
- API endpoints: Integration tests (request → response)
- BAML prompts: Embedded tests in .baml files
- SSE streaming: Manual testing with browser EventSource
- UI components: Svelte component tests (if breakage emerges)

---

## Integration Points

**Backend**:
- Models: Session, MealCriterion, Pitch with relationships
- Routes: Session CRUD, criteria management, SSE streaming generation
- BAML: GenerateCriterionPitches function adapted from prototype
- Database: SQLite with SQLModel ORM

**Frontend**:
- Routes: Main page, session list, session detail (`/sessions/:id`)
- Components: Session creation form, criteria input, pitch cards
- State: EventSource handling for streaming, pitch grouping logic
- UI Framework: Svelte + Skeleton v3

**BAML**:
- Port GenerateRecipePitches from prototype
- Adapt for per-criterion context
- Household profile baked into prompt
- Dynamic inventory loading

**Database Relationships**:
- Session (1) → MealCriteria (N)
- MealCriterion (1) → Pitches (N)
- All use UUID foreign keys

---

## Risk Assessment

**High Risks**:

1. **SSE streaming complexity during pitch persistence**
   - Risk: State management during incremental SSE + DB writes could have race conditions
   - Mitigation: Sequential BAML calls (not parallel), simple save-per-pitch pattern
   - Contingency: Start with synchronous generation (all pitches then return), add streaming later

2. **BAML prompt adaptation for per-criterion context**
   - Risk: Prototype generates flat pool; per-criterion generation may need prompt restructuring
   - Mitigation: Start with criterion description as additional_context (minimal change)
   - Contingency: If quality suffers, batch generate with post-processing to group by criterion

**Medium Risks**:

3. **Pitch persistence vs ephemeral tradeoff**
   - Risk: Persistent pitches add DB complexity, ephemeral pitches complicate SSE state
   - Mitigation: Choose persistence (simpler for SSE, aligns with session-as-hub)
   - Watch: If DB queries slow, add indexes or reconsider

4. **Sequential vs batched BAML generation performance**
   - Risk: Sequential BAML calls (3 criteria = 3 calls) may feel slow
   - Mitigation: Acceptable for MVP (optimize later), SSE provides progress feedback
   - Watch: If > 10 seconds total, consider batching

**Steering likelihood**:
- Phase 4 (BAML adaptation) may need prompt iteration to match quality
- Phase 5 (SSE integration) may need UX adjustments for progress feedback

---

## Implementation Notes

**TDD**: Test-Driven Development throughout all phases with red-green-refactor

**Prototype patterns to follow**:
- BAML household profile baking (prototype/baml_src/recipes.baml:40-105)
- GET-based SSE endpoint pattern (prototype/app.py:418-493)
- SQLModel UUID schema (prototype/app.py:27-81)
- BAML embedded tests (prototype/baml_src/inventory.baml:79-187)

**Prototype patterns to change**:
- Single `app.py` → separate `models.py`, `routes.py`, `baml_functions.py`
- Flat pitch generation → grouped by criterion
- Vanilla JS → Svelte + Skeleton v3
- Sync BAML → Async throughout

**Quality gates**:
- Each phase: tests pass before moving to next phase
- Phase 5: Manual SSE testing with browser confirms streaming works
- Phase 6: End-to-end walkthrough (create session → add criteria → generate → view pitches)

**General guidance**:
- Steel thread focus: OK to be ugly (basic cards, no filtering)
- Acceptable debt: minimal error handling, happy-path focus
- Fast iteration priority: changes in < 30 min
- Stop if adding abstraction "for later"

---

## Overall Complexity Estimate

**Complexity**: M (Moderate)

**Confidence**: High

**Justification**:
- **Pattern novelty**: LOW - Following clear prototype patterns for BAML, SSE, SQLModel
- **Decision density**: MEDIUM - BAML prompt adaptation, SSE state management need decisions
- **Context coordination**: MEDIUM - Session → Criteria → Pitches relationships across 6 phases
- **Integration points**: MEDIUM - BAML + API + DB + SSE + Frontend, but well-scoped
- **Steering likelihood**: MEDIUM - BAML prompts may need iteration (Phase 4), SSE UX may need adjustment (Phase 5)

**What drives complexity**:
- BAML prompt adaptation from flat to per-criterion generation (novel context)
- SSE streaming with incremental DB persistence (integration density)
- Sequential BAML calls coordination (state management)

**Why confidence is high**:
- Clear prototype patterns to follow for all major components
- Well-defined acceptance criteria from feature frame
- Incremental phases with clear dependencies
- MVP scope boundaries prevent feature creep
