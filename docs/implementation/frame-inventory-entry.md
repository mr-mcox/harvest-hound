# Feature Frame: Inventory Entry

**Date**: 2025-12-06
**Status**: Draft - Awaiting Alignment

---

## Problem Statement

Mental overhead of CSA delivery entry is the first friction point in the meal planning loop. Users need a fast, frictionless way to get fresh produce into the system so they can start planning meals. Manual entry (typing each ingredient, quantity, location, priority) is too slow and tedious for 15-30 items at once.

**From Prototype Discovery**:
- Free text parsing is "soooo much easier. I love it." (LEARNINGS:251)
- LLM-suggested priorities mostly right, reduces data entry burden (LEARNINGS:318)
- Flat ingredient view with priority reduces cognitive load vs store-centric organization (LEARNINGS:309)

---

## User Stories

### Story 1: Bulk paste CSA delivery with happy path
**As a** meal planner
**I want** to paste my CSA delivery list and have it automatically parsed
**So that** I can get ingredients into the system in seconds, not minutes

**Acceptance Criteria**:
- [ ] User can navigate to `/inventory/import` from main inventory view
- [ ] User can paste free text (e.g., "2 lbs carrots\n3 beet bunches\n1 butternut squash")
- [ ] System parses ingredients into pending items (ingredient name, quantity, unit, priority, optional portion size)
- [ ] Pending items appear in review list (client-side only, not saved yet)
- [ ] User can approve all pending items to commit them to inventory
- [ ] After approval, pending items are cleared and user is redirected to `/inventory`
- [ ] Pending items are lost on page refresh (ephemeral until approved)

**From LEARNINGS.md**: Bulk inventory entry via free text (LEARNINGS:250), One action: paste → parse → all ingredients added (LEARNINGS:253)

### Story 2: Iterate on failed parsing (cross off and retry)
**As a** meal planner
**I want** to delete incorrectly parsed items and re-parse with adjustments
**So that** I can fix parsing mistakes without manual correction or starting over

**Acceptance Criteria**:
- [ ] User can delete individual pending items from review list
- [ ] User can paste additional text to re-parse more items
- [ ] Re-parsed items append to pending list (don't replace)
- [ ] User can iterate (paste → review → delete bad ones → paste again) until satisfied
- [ ] Final approval commits only the items still in pending list

**From LEARNINGS.md**: Delete works great, heavily used for cleanup (LEARNINGS:257), Parsing notes useful for problematic items (LEARNINGS:367)

### Story 3: Add configuration instructions for batch context
**As a** meal planner
**I want** to provide parsing context that applies to all items in my list
**So that** I don't have to repeat "these are all frozen" or "all in 1lb portions" for each item

**Acceptance Criteria**:
- [ ] User can enter optional configuration instructions in a separate field
- [ ] Configuration instructions are passed to LLM during parsing
- [ ] Configuration instructions influence: priority ("on their last legs"), portion hints ("all in 1lb portions"), location ("all frozen")
- [ ] Configuration instructions are session-only (not saved between page loads)
- [ ] Configuration instructions apply to each parse call in the session

**From LEARNINGS.md**: Store definitions dual-purpose: what belongs + parsing context (LEARNINGS:25)

**Example instructions**:
- "These are all frozen and in 1lb portions"
- "All are dried beans in 3lb bags, loose"
- "All are in 16oz cans"
- "All of these veggies are on their last legs"

### Story 4: Infer portion sizes from input or configuration
**As a** meal planner
**I want** the system to understand discrete portions vs infinitely divisible quantities
**So that** recipe generation respects portioning constraints (can't use 1.5 lbs if frozen in 1lb packs)

**Acceptance Criteria**:
- [ ] System infers portion sizes from quantity/unit (e.g., "3 16oz cans of tomatoes" → 16oz portions)
- [ ] System infers portion sizes from configuration instructions (e.g., "all in 1lb portions")
- [ ] Portion size is optional metadata (nullable, assumes infinitely divisible if not specified)
- [ ] Portion sizes appear in pending items review (read-only in Phase 1)
- [ ] Portion sizes are stored with inventory items for future claiming logic

**From LEARNINGS.md**: Portioning constraints discovered (LEARNINGS:18), Item-based units for meats (LEARNINGS:371)

### Story 5: Automatic priority inference
**As a** meal planner
**I want** the system to suggest priority levels based on perishability
**So that** I can quickly triage what needs to be used soon vs what can wait

**Acceptance Criteria**:
- [ ] LLM suggests priority during parsing: low (frozen), medium (normal), high (use soon), urgent (spoiling)
- [ ] Priority appears in pending items review (read-only in Phase 1)
- [ ] Configuration instructions can influence priority ("on their last legs" → high/urgent)
- [ ] Priority editing in pending state deferred to Phase 2 (polish pass)

**From LEARNINGS.md**: LLM-suggested priorities mostly right (LEARNINGS:318), Priority drives recipe importance (LEARNINGS:185)

### Story 6: Primary inventory list view
**As a** meal planner
**I want** to see all my current inventory as the main view
**So that** I can verify what's in the system and access import functionality

**Acceptance Criteria**:
- [ ] `/inventory` route shows main inventory list (primary view)
- [ ] Inventory list shows: ingredient name, quantity + unit, priority, portion size (if present)
- [ ] Inventory list is sorted by priority (urgent → high → medium → low)
- [ ] "Import Ingredients" button navigates to `/inventory/import`
- [ ] After approval in import view, user is redirected to `/inventory` to see new items
- [ ] No filtering or advanced features in Phase 1 (simple list only)
- [ ] Location field deferred to post-steel-thread (not in model, not in UI)

**From LEARNINGS.md**: Flat ingredient view with priority reduces cognitive load (LEARNINGS:309)

---

## Prototype Contrast

| Aspect | Prototype | MVP | Why Change |
|--------|-----------|-----|------------|
| Inventory entry | `/stores/{id}/inventory/bulk` POST endpoint | Dedicated `/inventory/import` page | Clearer user mental model (importing vs managing) |
| Pending review | Immediate save, inline delete | Client-side pending state with approve step | Safer iteration (no accidental commits), matches user's "cross off and retry" workflow |
| Configuration instructions | Store definitions (saved) | Session-only free text field | Defer saved templates complexity, validate pattern first |
| Portion sizes | Not explicitly modeled | Optional metadata on inventory items | Enable future claiming logic without blocking MVP |
| Priority | Editable after save | Read-only in pending (Phase 1), editable after save | Simplest path for steel thread, editing deferred to Phase 2 |
| Location | Store metadata, editable | Deferred entirely (not in model or UI) | Not essential for steel thread, batch update post-steel-thread |
| Navigation | Stores page primary | `/inventory` list primary, import secondary | List view is more frequently accessed than import |

**Preserve from Prototype**:
- Free text → BAML parse → bulk insert flow (single round-trip per parse)
- LLM-suggested priorities (manual adjustment deferred to Phase 2)
- Flat list sorted by priority

**Fix from Prototype**:
- No separate "stores" concept in MVP (just inventory with location metadata)
- Pending state before commit (safer iteration)

**Change from Prototype**:
- Dedicated import view (separate route) vs embedded in store management
- Configuration instructions as session context vs saved store definitions

---

## Out of Scope (Deferred)

Explicitly NOT part of this feature:
- **Location field**: Not in model or UI for Phase 1. Deferred to post-steel-thread batch update. Not essential for proving the meal planning loop.
- **Priority editing in pending state**: Phase 2 fidelity pass. Deferred because LLM suggestions are accurate enough (80%+) and editing can happen after save.
- **Saved configuration templates**: Session-only instructions for now. Deferred because we don't know if patterns emerge that are worth saving.
- **Table view with filtering**: Phase 2 fidelity pass. Deferred because simple list is sufficient for proving the loop.
- **Editing inventory items**: Separate feature (CRUD on existing items vs import). Deferred because import is the steel thread bottleneck.
- **Portioning UI refinement**: Read-only display in Phase 1. Deferred because manual editing isn't validated yet.
- **Duplicate detection**: No smart merging of "carrots" variants. Deferred because user can delete duplicates manually.

**Future Features This Enables**:
- Saved configuration templates (if usage patterns emerge)
- Advanced table view with filtering and bulk operations
- Inventory editing and quantity adjustments
- Portion-aware claiming logic in recipe generation

---

## Open Risks

**Parsing accuracy for configuration instructions**:
- Risk: LLM might not correctly apply batch context ("all frozen") to every item
- Impact: User has to manually fix priority/location for each item (defeats purpose)
- Suggest: Test with real examples during implementation. If accuracy < 80%, consider explicit prompt engineering or structured input.

**Client-side pending state complexity**:
- Risk: Managing pending items in Svelte state might get messy with iteration
- Impact: Bugs in review flow (deleted items reappearing, duplicates)
- Suggest: Use simple array state, append-only pattern for re-parses

---

## Alignment Decisions

✅ **Portion sizes in review**: Show if inferred (helps user understand what was parsed)

✅ **Priority editing UX**: Deferred to Phase 2 polish pass (simplest for steel thread)

✅ **Navigation**: `/inventory` is primary list view, `/inventory/import` is secondary import page

✅ **Location inference**: Deferred entirely - not in BAML, not in model, batch update post-steel-thread

✅ **Multiple imports lifecycle**: After approval, pending items are committed and cleared (reset to empty)
