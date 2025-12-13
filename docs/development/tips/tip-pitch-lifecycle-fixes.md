docs/development/tips/tip-pitch-lifecycle-fixes.md---
date: 2025-12-13
feature: pitch-lifecycle-fixes
status: draft
frame: none
estimated_effort: M
confidence: High
tags: [bug-fix, pitch-generation, UX, database]
---

# TIP: Pitch Lifecycle & Generation Fixes

## Context

### Problem Statement

Pitch regeneration has three interconnected bugs causing unexpected behavior:

1. **Backend over-generates pitches**: Generates pitches for ALL criteria including those with all slots filled, and distributes more pitches than requested (routes.py:354-361)
2. **No pitch lifecycle tracking**: Pitches accumulate forever with no way to track which have been fleshed out or rejected
3. **Confusing UI counts**: Frontend shows ephemeral pitch counts that change on refresh, focusing user attention on pitches rather than meal slots

**User Impact**:
- "Generation complete" creates pitches for filled criteria (wasted LLM calls)
- Pitch counts inconsistent across page refreshes (2/3 becomes 1/3)
- Can't reject pitches they're not interested in
- Focus on wrong metric (pitch counts vs slots filled)

**From Investigation**:
- Database has 7, 13, 7, 4 pitches for criteria but UI shows "1/3 pitches"
- First criterion has 1 slot filled with planned recipe, yet got 2 new pitches
- `fleshedOutPitchIds` is client-side Set, doesn't persist

### User Stories

**Story 1: Pitches only for unfilled criteria**
- System should only generate pitches for criteria with unfilled slots
- Criteria with all slots filled should be skipped

**Story 2: Accurate pitch distribution**
- If delta = 2 pitches needed, system should generate exactly 2 total (not 4+)
- Distribution math should sum correctly across criteria

**Story 3: Track pitch lifecycle**
- Link pitches to recipes when fleshed out (via recipe_id)
- Mark pitches as rejected when user dismisses them
- Filter UI to show only available pitches (unfleshed, not rejected)

**Story 4: Focus on meal slots, not pitches**
- UI should emphasize "(X / Y slots filled)" not pitch counts
- Pitch availability is secondary information

### Key Acceptance Criteria

- [ ] Backend only generates pitches for criteria with unfilled slots
- [ ] Pitch distribution sums to requested delta (not over-generates)
- [ ] Pitches linked to recipes when fleshed out (recipe_id set)
- [ ] Pitches can be rejected (rejected = true)
- [ ] UI filters pitches: WHERE recipe_id IS NULL AND rejected = FALSE
- [ ] UI shows slot progress: "(X / Y slots filled)"
- [ ] Backend tests capture intended generation behavior

### Scope Boundaries

**In Scope:**
- Add recipe_id and rejected fields to Pitch model
- Fix generation logic (unfilled criteria only, correct distribution)
- Link pitches on flesh-out
- Soft delete pitches on rejection
- Update UI to show slot counts
- Backend tests for generation logic

**Out of Scope:**
- Auto-backfill pitches when rejected (user clicks "Generate More")
- Pitch history/audit UI (data exists, UI deferred)
- Cleanup job for old pitches (session delete cascades)

### Relevant Learnings

From LEARNINGS.md:
- "Pitches using claimed ingredients should be removed automatically" (line 289-293)
- "Pitch as projection, not entity" (line 121-127)
- "User feedback: 'I'd like them removed' - don't want to see unavailable options" (line 293)
- Multi-wave generation critical for iterative workflow (line 271-274)

From MVP-CHARTER.md:
- Pitch = "Ephemeral, session-scoped. Not a separate entity" (line 16)
- Acceptable technical debt: minimal error handling, light testing (line 136-141)

---

## Implementation Phases

### Phase 1: Add Pitch Lifecycle Schema

**Purpose**: Add database fields to track pitch lifecycle without changing behavior. This enables all subsequent phases.

**Scope**: Backend schema changes only

**TDD Focus**:
- Schema migration creates fields correctly
- Nullable fields work (existing pitches unaffected)
- Queries work with new fields

**Key Considerations**:
- Migration must be backward compatible (nullable fields)
- Existing pitches should load correctly after migration
- Session cascade delete still works

**Dependencies**: None

**Complexity**: XS

---

### Phase 2: Fix Backend Generation Logic

**Purpose**: Fix critical bug where system generates pitches for filled criteria and over-generates total count. This is the highest-value fix.

**Scope**: Backend pitch generation logic, backend tests

**TDD Focus**:
- Write tests for intended behavior (currently failing):
  - Only generate for criteria with unfilled slots
  - Distribution sums to delta (not over-generates)
  - Skip criteria where slots == planned_recipes
- Fix routes.py generation logic
- Tests pass

**Key Considerations**:
- Current logic: `num_pitches = max(1, round(criterion_share))` forces ALL criteria to get ≥1 pitch
- Need to filter criteria BEFORE distribution loop
- Need to ensure sum of distributed pitches equals delta
- Distribution should be proportional to unfilled slots per criterion

**Dependencies**: Phase 1 (schema exists)

**Complexity**: S

---

### Phase 3: Link Pitches on Flesh-Out

**Purpose**: Update flesh-out endpoint to link pitches to recipes, creating audit trail and enabling UI filtering.

**Scope**: Backend flesh-out endpoint, database transactions

**TDD Focus**:
- Pitch.recipe_id set after successful flesh-out
- Transaction is atomic (recipe + claims + pitch update)
- Partial success handled (2/3 succeed, 1 fails)
- Failed flesh-out leaves pitch unlinked (retryable)

**Key Considerations**:
- Flesh-out request must include pitch IDs (modify request payload)
- Each pitch → recipe is its own transaction
- BAML failure = no changes to pitch
- Database failure = rollback entire transaction

**Dependencies**: Phase 1 (recipe_id field exists)

**Complexity**: S

---

### Phase 4: Update Frontend Display & Filtering

**Purpose**: Change UI to focus on meal slots rather than pitch counts, and filter pitches based on lifecycle state.

**Scope**: Frontend display logic, API queries

**TDD Focus**:
- UI shows "(X / Y slots filled)" prominently
- Pitch counts de-emphasized or removed
- Only available pitches displayed (recipe_id IS NULL AND rejected = FALSE)
- Remove ephemeral fleshedOutPitchIds logic

**Key Considerations**:
- Queries must filter: WHERE recipe_id IS NULL AND rejected = FALSE
- Slot calculation: criterionRecipes.length / criterion.slots
- Pitch display becomes optional context (not primary metric)
- Remove client-side state management for fleshed pitches

**Dependencies**: Phase 3 (pitches linked on flesh-out)

**Complexity**: S

---

### Phase 5: Add Pitch Rejection

**Purpose**: Allow users to dismiss pitches they're not interested in, preventing regeneration of similar options.

**Scope**: Backend endpoint, frontend UI action

**TDD Focus**:
- PATCH /pitches/{id}/reject endpoint
- Sets rejected = TRUE
- Rejected pitches filtered from UI
- Rejection is soft delete (reversible if needed)

**Key Considerations**:
- Simple UPDATE query (low risk)
- Frontend needs reject button/action per pitch
- Rejected pitches don't count toward "available" pool
- Future: Could use rejection signals to improve generation (deferred)

**Dependencies**: Phase 4 (UI filters by rejected field)

**Complexity**: XS

---

## Sequencing Logic

**Why this order:**

1. **Schema first** (Phase 1): Low-risk foundation, enables all subsequent work
2. **Fix generation bug** (Phase 2): Highest value, most critical issue, independent of other phases
3. **Link on flesh-out** (Phase 3): Enables cleanup, builds on schema
4. **Update UI** (Phase 4): User-facing improvements, depends on linking working
5. **Rejection feature** (Phase 5): Nice-to-have, builds on UI filtering

**Parallel work possible:**
- Phase 2 can happen in parallel with Phase 3 (independent changes)

**Risk minimization:**
- Schema changes deployed first without behavior changes
- Critical bug fixed early (high value)
- Each phase is independently valuable
- Rollback is straightforward (each phase is isolated)

---

## High-Level Test Strategy

**TDD throughout**: Write failing tests, implement fixes, tests pass

**Backend Focus:**
- Unit tests for pitch generation logic (Phase 2)
- Integration tests for flesh-out with linking (Phase 3)
- Endpoint tests for rejection (Phase 5)

**Test Scenarios:**
- Generation skips fully-filled criteria
- Distribution math sums correctly
- Pitches linked atomically on flesh-out
- Failed flesh-out leaves pitch unlinked
- Rejected pitches filtered from queries

**Acceptable Gaps** (per MVP-CHARTER):
- Light integration test coverage
- Manual testing for UI changes
- Minimal error handling tests

---

## Integration Points

**Backend:**
- models.py: Add recipe_id, rejected fields to Pitch
- routes.py: Fix generation logic, update flesh-out endpoint, add reject endpoint
- services.py: Modify calculate_pitch_generation_delta to filter criteria
- tests/: Add generation logic tests

**Frontend:**
- +page.svelte: Update slot display, remove fleshedOutPitchIds logic, add rejection UI
- API calls: Modify flesh-out request, add reject request

**Database:**
- Alembic migration: Add columns to pitch table

**No BAML changes needed** (generation prompts unchanged)

---

## Risk Assessment

**High Risks:**
- **Migration breaks existing pitches**: Mitigation: Nullable fields, test migration on copy of harvest.db
- **Generation logic still incorrect**: Mitigation: TDD approach, write tests first

**Medium Risks:**
- **Partial flesh-out failures**: Mitigation: Per-pitch transactions, each is atomic
- **UI shows stale data after changes**: Mitigation: Refetch pitches after mutations

**Low Risks:**
- **Data accumulation**: Mitigation: Session cascade delete handles cleanup
- **Query performance**: Mitigation: Small data volume, indexes exist

**Contingency Plans:**
- If migration fails: Rollback, debug on dev.db
- If generation logic complex: Break into smaller tests, iterate
- If UI filtering broken: Fall back to client-side filter temporarily

---

## Implementation Notes

**TDD**: Test-Driven Development throughout all phases
- Write failing test first
- Implement minimal fix
- Refactor if needed
- Commit when green

**Migration Safety**:
- Test on dev.db first
- Backup harvest.db before production migration
- Nullable fields ensure backward compatibility

**Query Patterns**:
- Consistent filtering: `WHERE recipe_id IS NULL AND rejected = FALSE`
- Use SQLModel select() for type safety
- Avoid N+1 queries (prefetch if needed)

**Quality Gates**:
- All tests pass
- Pre-commit hooks pass
- Manual smoke test on dev.db

---

## Overall Complexity Estimate

**Overall**: M (Medium)
**Confidence**: High

**Justification**:
- **5 phases**: Each is XS-S individually, but coordination adds up
- **Schema migration**: Low-risk but requires care (backup, testing)
- **Generation logic**: Well-understood bug, clear fix, but needs careful testing
- **Integration points**: Backend + Frontend + Database, but changes are localized
- **Novel patterns**: None - all standard CRUD and filtering
- **Decision density**: Low - clear fixes for clear bugs
- **Steering needs**: Minimal - straightforward implementation

**Effort breakdown**:
- Phase 1 (Schema): XS (~30 min)
- Phase 2 (Generation fix): S (~1-2 hours with tests)
- Phase 3 (Linking): S (~1-2 hours)
- Phase 4 (UI update): S (~1 hour)
- Phase 5 (Rejection): XS (~30 min)

**Total estimated**: 4-6 hours
