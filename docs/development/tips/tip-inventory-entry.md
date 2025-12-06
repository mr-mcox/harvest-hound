---
date: 2025-12-06
feature: inventory-entry
status: draft
frame: .scratch/frame-inventory-entry.md
estimated_effort: M
confidence: High
tags: [mvp, steel-thread, baml, svelte, inventory]
---

# Technical Implementation Plan: Inventory Entry

## Context

**Problem Statement**:
Mental overhead of CSA delivery entry is the first friction point in the meal planning loop. Manual entry of 15-30 items (typing each ingredient, quantity, location, priority) is too slow and tedious. Users need a fast, frictionless way to get fresh produce into the system.

**User Stories** (6 essential):
1. Bulk paste CSA delivery with happy path (paste → parse → review → approve)
2. Iterate on failed parsing (delete bad items, re-paste, retry)
3. Add configuration instructions for batch context (e.g., "all frozen in 1lb portions")
4. Infer portion sizes from input or configuration
5. Automatic priority inference (LLM suggests low/medium/high/urgent)
6. Primary inventory list view (sorted by priority, link to import)

**Key Acceptance Criteria** (TDD seeds):
- Free text paste → BAML parse → client-side pending review → approve to commit
- Pending items are ephemeral (lost on page refresh, only saved on approval)
- Configuration instructions influence priority, portion hints during parsing
- Portion sizes stored with inventory items (for future claiming logic)
- LLM-suggested priorities based on perishability
- `/inventory` route shows main list, `/inventory/import` for bulk entry

**Scope Boundaries**:
- **IN**: Free text parsing, pending review, configuration context, portion inference, priority suggestions, basic list view
- **OUT**: Location field (deferred), priority editing in pending state, saved templates, table filtering, inventory editing, duplicate detection

**Relevant Prototype Patterns**:
- BAML pattern: `prototype/baml_src/inventory.baml:17-77` - ExtractIngredients function with priority inference
- Backend pattern: `prototype/app.py:313-363` - Bulk inventory POST endpoint
- Model pattern: `prototype/app.py:35-44` - InventoryItem schema
- Test pattern: `prototype/baml_src/inventory.baml:79-187` - BAML test cases for parsing

**Key Learnings**:
- Free text parsing is "soooo much easier. I love it." (LEARNINGS:251)
- LLM-suggested priorities mostly right, reduces data entry burden (LEARNINGS:318)
- Flat ingredient view with priority reduces cognitive load (LEARNINGS:309)
- Delete heavily used for cleanup during iteration (LEARNINGS:257)
- Portioning constraints discovered for claiming logic (LEARNINGS:18)

## Implementation Phases

### Phase 1: BAML Enhancements for Portions and Configuration

**Purpose**: Extend BAML parsing to infer portion sizes and apply configuration context, enabling richer inventory metadata without manual entry overhead.

**Scope**:
- BAML schema changes (Ingredient class)
- ExtractIngredients function enhancements
- BAML test coverage for new functionality

**TDD Focus**:
- Acceptance criteria: "System parses ingredients into pending items (ingredient name, quantity, unit, priority, optional portion size)"
- Acceptance criteria: "Configuration instructions influence: priority, portion hints, location"
- Test approach: Unit (BAML test cases)

**Key Considerations**:
- Portion inference from quantity/unit (e.g., "3 16oz cans" → 16oz portions)
- Portion inference from configuration instructions (e.g., "all in 1lb portions")
- Configuration context must not override explicit portion hints in text
- Portion size is optional (nullable) - only infer when confident
- **Unit standardization for counts**: Use cookbook-standard units
  - Item-specific units for countables: "roast", "chop", "can", "jar", "head", "bunch"
  - Use "whole" for whole produce when needed for clarity (vs prepared forms)
  - Avoid generic "each" or "item" - be specific to what it is
  - Examples: "2 roast" (not "2 each roast"), "3 can" (not "3 item"), "1 head lettuce"

**Dependencies**: None

**Complexity**: S

---

### Phase 2: Backend API for Pending Flow

**Purpose**: Create two-endpoint flow for pending state: parse (no save) and commit (bulk save). Enables client-side iteration on parsed results before committing to inventory.

**Scope**:
- POST /api/inventory/parse endpoint (returns parsed items, no save)
- POST /api/inventory/bulk endpoint (saves list of items)
- Database migration to add portion_size field to InventoryItem
- Auto-create default store for simplified inventory model (hidden from user)

**TDD Focus**:
- Acceptance criteria: "System parses ingredients into pending items (not saved yet)"
- Acceptance criteria: "User can approve all pending items to commit them to inventory"
- Test approach: Integration (API endpoint testing)

**Key Considerations**:
- Parse endpoint receives free_text + optional configuration_instructions
- Parse endpoint returns array of parsed items (not saved to DB)
- Bulk endpoint receives array of items to save
- Default store created on first use (eliminates store selection from UI)
- Portion size field added to InventoryItem model (nullable string)
- Location field kept in model but not populated (deferred to post-steel-thread)

**Dependencies**: Phase 1 (BAML schema must support portions)

**Complexity**: M

---

### Phase 3: Svelte Import View with Pending State

**Purpose**: Build import UI with pending state management, enabling iterative parsing workflow (paste → review → delete bad ones → re-paste → approve).

**Scope**:
- Svelte InventoryImport component
- Client-side pending state (array of parsed items)
- Free text textarea + configuration instructions field
- Pending items review list with delete capability
- Re-parse and append workflow
- Approve all commits to backend

**TDD Focus**:
- Acceptance criteria: "User can paste free text and see pending items in review list"
- Acceptance criteria: "User can delete individual pending items from review list"
- Acceptance criteria: "User can paste additional text to re-parse more items"
- Acceptance criteria: "Final approval commits only items still in pending list"
- Test approach: E2E (user workflow testing)

**Key Considerations**:
- Pending state managed in Svelte component (reactive array)
- Parse button calls /api/inventory/parse, appends results to pending state
- Delete removes item from pending array (client-side only)
- Re-parse appends to existing pending items (doesn't replace)
- Configuration instructions apply to each parse call in session
- Approve all sends pending items to /api/inventory/bulk, clears state
- Pending items lost on page refresh (session-only, not persisted)

**Dependencies**: Phase 2 (backend endpoints must exist)

**Complexity**: M

---

### Phase 4: Inventory List View

**Purpose**: Create main inventory view sorted by priority, providing visibility into current inventory and navigation to import functionality.

**Scope**:
- Svelte InventoryList component
- GET /api/inventory endpoint
- Priority-sorted display (urgent → high → medium → low)
- Display fields: ingredient name, quantity + unit, priority, portion size (if present)
- "Import Ingredients" button navigates to import view

**TDD Focus**:
- Acceptance criteria: "/inventory route shows main inventory list"
- Acceptance criteria: "Inventory list sorted by priority"
- Acceptance criteria: "Inventory list shows: ingredient name, quantity + unit, priority, portion size"
- Test approach: Integration (component + API)

**Key Considerations**:
- Priority sorting: urgent (4) → high (3) → medium (2) → low (1)
- Portion size displayed when present (e.g., "3 lbs (1lb portions)")
- No filtering or advanced features in Phase 1 (simple sorted list)
- Navigation button to /inventory/import route

**Dependencies**: Phase 2 (backend must return inventory items)

**Complexity**: S

---

### Phase 5: Integration and Navigation

**Purpose**: Wire up routing, navigation, and post-approval redirect to complete the end-to-end import-to-list workflow.

**Scope**:
- SvelteKit routing configuration (/inventory, /inventory/import)
- Navigation between list and import views
- Post-approval redirect to /inventory
- Clear pending state after successful commit
- End-to-end flow testing

**TDD Focus**:
- Acceptance criteria: "User can navigate to /inventory/import from main inventory view"
- Acceptance criteria: "After approval, user is redirected to /inventory"
- Acceptance criteria: "Pending items are cleared after approval"
- Test approach: E2E (full workflow)

**Key Considerations**:
- SvelteKit routing setup for /inventory and /inventory/import
- Import view redirects to /inventory after successful approval
- Pending state cleared in Svelte component after redirect
- "Import Ingredients" button in list view navigates to import
- Browser back button behavior (pending state lost)

**Dependencies**: Phases 3 and 4 (both views must exist)

**Complexity**: S

---

## Sequencing Logic

**Why this order**:
- BAML first (foundation for all parsing) → Backend API (data layer) → Import UI (user-facing) → List UI (destination) → Integration (wiring)
- BAML changes are isolated and low-risk, establish contract for backend
- Backend provides stable API for frontend to consume
- Import view depends on parse/bulk endpoints existing
- List view can be built in parallel with import view (both depend on Phase 2)
- Integration phase wires everything together once pieces exist

**Parallel work opportunities**:
- Phases 3 and 4 can proceed in parallel after Phase 2 completes (both depend on backend, not on each other)

**Dependencies that constrain sequencing**:
- Phase 2 must follow Phase 1 (backend calls BAML)
- Phase 3 must follow Phase 2 (UI calls backend API)
- Phase 5 must follow Phases 3 and 4 (integrates both views)

**How phases build on each other**:
- Phase 1 establishes portion/config support in BAML
- Phase 2 exposes BAML functionality via API + adds pending flow
- Phase 3 builds on API to create import workflow
- Phase 4 builds on API to create list view
- Phase 5 connects import → list flow

---

## High-Level Test Strategy

**TDD Throughout** (Red-Green-Refactor):
- Phase 1: BAML unit tests (extend existing test suite)
- Phase 2: API integration tests (parse endpoint returns expected shape, bulk endpoint saves correctly)
- Phase 3: E2E tests for import workflow (paste → parse → delete → re-parse → approve flow)
- Phase 4: Integration tests for list view (fetch, sort, display)
- Phase 5: E2E tests for navigation and redirect flow

**Key Scenarios to Validate** (from acceptance criteria):
- Happy path: Paste CSA delivery → parse → approve → see in list
- Iteration: Paste → delete bad items → re-paste → approve
- Configuration context: "all frozen in 1lb portions" influences parsing
- Portion inference: "3 16oz cans" → 16oz portions captured
- Priority inference: LLM suggests appropriate urgency levels
- Page refresh: Pending items lost (ephemeral state)

**Testing Approach Per Phase**:
- BAML: Test cases in .baml files (portion inference, config context)
- Backend: API integration tests (pytest + httpx)
- Frontend: Svelte component tests + E2E (Playwright or similar)

---

## Integration Points

**Backend**:
- BAML client integration (ExtractIngredients function)
- New API endpoints (/api/inventory/parse, /api/inventory/bulk)
- Database schema migration (add portion_size field)
- Default store auto-creation logic

**Frontend**:
- SvelteKit routing setup
- New Svelte components (InventoryImport, InventoryList)
- Client-side state management (pending items array)
- API integration (fetch to backend endpoints)

**BAML**:
- Ingredient class extension (portion_size field)
- ExtractIngredients prompt updates (portion inference, config context)
- Test suite expansion (new test cases)

---

## Risk Assessment

**High Risks**:

1. **BAML portion inference accuracy**
   - Risk: LLM might not correctly parse "all in 1lb portions" from configuration instructions
   - Impact: User has to manually fix portions (defeats convenience purpose)
   - Mitigation:
     - Start with largest OpenAI model (gpt-4o) for parsing
     - Extensive BAML testing with real examples
     - **Targeted retry testing**: When test fails, re-run 4 more times. If fails 2+ out of 5 total runs, decide remediation.
     - Once all tests pass, try smaller/faster models (gpt-4o-mini) and verify tests still pass
   - Contingency:
     - If consistent failures: Upgrade model OR decompose into multiple BAML calls (basic parsing + portion inference)
     - If accuracy insufficient: Simplify to explicit-only portion hints (remove config inference)

2. **Configuration instructions ignored or misapplied**
   - Risk: LLM applies batch context incorrectly (e.g., "all frozen" → assigns wrong priorities)
   - Impact: Wrong priorities assigned, user has to manually fix each item
   - Mitigation:
     - Clear prompt engineering with explicit examples in prompt
     - Test with diverse configuration examples
     - Use targeted retry testing (5-run validation on failures)
   - Contingency:
     - Make configuration optional, provide examples in UI for clarity
     - If persistent issues: Upgrade model OR split configuration application into separate BAML call

**Medium Risks**:

1. **Client-side pending state complexity**
   - Risk: Managing pending items array in Svelte (appending, deleting) gets messy
   - Impact: Bugs in review flow (deleted items reappearing, duplicates on re-parse)
   - Mitigation: Simple array operations, clear state management pattern
   - Contingency: Use Svelte stores if component state becomes unwieldy

2. **Default store assumption**
   - Risk: Auto-creating default store might conflict with future multi-location support
   - Impact: Migration complexity when adding location-based inventory
   - Mitigation: Design migration path upfront; keep store_id for now
   - Contingency: Accept technical debt, plan refactor for post-steel-thread

**Steering Likelihood**:
- Medium - Novel pending state workflow may need UX adjustments during implementation
- Configuration instructions prompt engineering may require iteration
- Portion inference accuracy will need validation with real data

---

## Implementation Notes

**TDD**: Test-Driven Development throughout all phases (red-green-refactor cycle)

**Prototype Patterns to Follow**:
- BAML ExtractIngredients structure (`prototype/baml_src/inventory.baml:17-77`)
- Bulk POST endpoint pattern (`prototype/app.py:313-363`)
- InventoryItem model fields (`prototype/app.py:35-44`)
- BAML test case structure (`prototype/baml_src/inventory.baml:79-187`)

**Prototype Patterns to Change**:
- Prototype saves immediately; MVP uses pending state before commit
- Prototype has store selection UI; MVP auto-creates default store (hidden)
- Prototype lacks portion_size and configuration_instructions

**Model Selection Strategy**:
- **Parsing (BAML ExtractIngredients)**: Use OpenAI family (cheaper for parsing tasks)
  - Start with largest: gpt-4o (establishes quality baseline)
  - Once all tests pass: Try smaller/faster models (gpt-4o-mini, gpt-3.5-turbo)
  - Verify tests still pass with smaller model before accepting downgrade
- **Recipe generation**: Continue using Anthropic (not changed by this feature)

**Testing Strategy for Model Validation**:
- **Initial development**: Use gpt-4o, write BAML tests until all pass
- **Test failure protocol**: When test fails, don't immediately fix prompt
  1. Re-run failing test 4 more times (5 total runs)
  2. If fails 2+ times out of 5: Decide remediation (prompt fix, model upgrade, or decompose task)
  3. If fails only 1 out of 5: Accept as acceptable variance, move on
- **Model optimization**: After all tests pass with gpt-4o, try gpt-4o-mini
  - Run full test suite with smaller model
  - If all tests pass: Accept smaller model (cost savings)
  - If tests fail: Decide between keeping gpt-4o OR decomposing complex tasks into multiple calls

**Quality Gates**:
- All BAML tests pass (5-run validation for any failures) before moving to Phase 2
- Model optimization attempted (try smaller model) before considering Phase 1 complete
- API endpoints tested with real BAML calls before frontend work
- Import workflow fully functional before building list view
- End-to-end flow tested with real CSA delivery list before completion

**General Guidance**:
- Keep Svelte components focused (single responsibility)
- Use TypeScript for frontend type safety
- Follow existing BAML test patterns for new test cases
- Minimize database schema changes (keep store_id, add portion_size only)
- Configuration instructions are session-scoped (in-memory, not persisted)
- Location field remains in model but unpopulated (fewest code changes)

---

## Overall Complexity Estimate

**T-shirt size**: M (Moderate)

**Confidence level**: High

**Justification**:
- **Pattern novelty**: Some novel patterns (pending state workflow, configuration context), but clear prototype examples for BAML and backend
- **Decision density**: Moderate - BAML prompt engineering for portions/config requires judgment, but acceptance criteria are clear
- **Context coordination**: Multiple systems coordinated (BAML, backend API, Svelte components, database), but integration points are well-defined
- **Integration points**: BAML, FastAPI, SQLModel, SvelteKit all touch this feature, requires careful sequencing
- **Steering likelihood**: Medium - Portion inference and config instructions may need prompt iteration based on real data

**Effort breakdown**:
- Phase 1 (BAML): S - Extending existing patterns
- Phase 2 (Backend): M - New endpoint patterns, schema migration
- Phase 3 (Svelte import): M - New component with state management
- Phase 4 (Svelte list): S - Simple display component
- Phase 5 (Integration): S - Routing and navigation

**Overall**: Moderate complexity driven by multi-system integration and novel pending state pattern, but high confidence due to clear acceptance criteria and prototype patterns to follow.
