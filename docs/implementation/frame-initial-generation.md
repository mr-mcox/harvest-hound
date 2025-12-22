# Feature Frame: Initial Recipe Generation with Session & Criteria

**Date**: 2025-12-06
**Status**: Aligned - Ready for Technical Planning

---

## Problem Statement

Users need to plan meals with structured constraints (quick weeknights, guest meals, leftovers, etc.) rather than generating a flat pool of pitches. The current prototype generates N pitches without organization, but real meal planning requires grouping by meal type/criteria to ensure balanced variety for the week.

**From Prototype Discovery**:
- Structured meal planning workflow validated: specs upfront (criteria), systematic filling, 3x unfilled slots (LEARNINGS.md:276-283)
- Flat generation works but doesn't match real planning needs (MVP-CHARTER.md:58 - "generate grouped pitches")
- Week-level planning criteria is essential for balanced variety (LEARNINGS.md:169-173)

---

## User Stories

### Story 1: Create Planning Session
**As a** meal planner
**I want** to create a named planning session for a specific week
**So that** I can organize my meal planning work in a persistent container

**Acceptance Criteria**:
- [ ] User sees "Create Session" button on main page
- [ ] User can create a session with optional name (auto-generates "Week of [prior Sunday]" if blank)
- [ ] Session is saved to database and persists across page refreshes
- [ ] User can view their active session
- [ ] Only one active session exists at a time (keep simple for MVP)
- [ ] Empty state shows "No active session" message with creation button

**From LEARNINGS.md**: Recipe persistence transforms system feel from session tool to weekly hub (line 102-107)

### Story 2: Add Meal Criteria to Session
**As a** meal planner
**I want** to add meal criteria with counts to my session
**So that** the system generates the right variety of pitches for my week

**Acceptance Criteria**:
- [ ] User can add a criterion with description field (e.g., "Quick weeknight dinner")
- [ ] Each criterion has a slots/count field (number input, e.g., 2 meals needed)
- [ ] User can add multiple criteria to one session (up to 7 max)
- [ ] Criteria are saved and displayed in the session
- [ ] User can remove criteria before generation (basic delete)
- [ ] System validates max 7 criteria per session

**From LEARNINGS.md**: Different from ad-hoc context, helps generate balanced week (line 171-173)

### Story 3: Generate Grouped Pitches
**As a** meal planner
**I want** to generate recipe pitches grouped by my criteria
**So that** I get organized options that match each meal type I need

**Acceptance Criteria**:
- [ ] User clicks single "Generate All" button to start generation
- [ ] System generates 3x pitches per criterion (e.g., 2 slots → 6 pitches)
- [ ] Generation uses current inventory + household profile + criterion context
- [ ] Pitches are grouped/associated with their originating criterion
- [ ] Progress feedback during generation (streaming or status indicator)
- [ ] Generated pitches are saved to database linked to session + criterion

**From LEARNINGS.md**:
- 3x unfilled meal slots sizing validated (line 282)
- Batch generation then stream to frontend works well (line 381)
- Technique diversity prompt critical for CSA items (line 420-428)

### Story 4: View Generated Pitches Organized by Criterion
**As a** meal planner
**I want** to see my generated pitches grouped by meal criteria
**So that** I can browse options for each specific meal type

**Acceptance Criteria**:
- [ ] Pitches are displayed grouped under their criterion heading
- [ ] Each pitch shows: name, blurb, why_make_this, key ingredients, active time
- [ ] Pitch display is read-only (no selection interaction yet)
- [ ] UI is simple/functional (cards or list, no fancy styling needed)
- [ ] Empty criteria show "No pitches yet" or similar

**From LEARNINGS.md**: Pitch quality ~80% ready for decision-making (line 377-382)

---

## Prototype Contrast

| Aspect | Prototype | MVP | Why Change |
|--------|-----------|-----|------------|
| **Organization** | Flat list of N pitches | Grouped by meal criteria | Real planning needs structure (LEARNINGS.md:276-283) |
| **Container** | No session concept | Named session entity | Persistence transforms UX (LEARNINGS.md:102-107) |
| **Criteria** | Optional context field | Explicit meal criteria with counts | Enables balanced variety (LEARNINGS.md:169-173) |
| **Generation sizing** | Fixed N pitches | 3x per criterion slot | Validated sizing (LEARNINGS.md:282) |
| **UI mode** | Single page | Session-focused page | Better information architecture as features grow |

**Preserve from Prototype**:
- BAML prompt structure (household profile, technique diversity, ingredient sources)
- SSE streaming architecture for generation feedback
- Three-tier ingredient source model (explicit stores, definition stores, grocery)
- LLM/code separation (LLM declares, code manages state)
- Batch BAML generation pattern (all pitches at once, stream results)

**Fix from Prototype**:
- Add Session and MealCriterion entities (missing domain concepts)
- Group pitches by criterion (currently flat)
- Support structured planning workflow (currently ad-hoc)

**Change from Prototype**:
- Introduce session-scoped UI (from single global page)
- Move from "Generate N" to "Generate All (for criteria)"
- Associate pitches with criteria for grouping

---

## Out of Scope (Deferred)

Explicitly NOT part of this feature:

- **Pitch selection interaction**: Deferred per user request - build through display only
- **Ingredient claiming**: Assume clean slate (no prior claims to respect)
- **Multi-wave generation**: Comes later with selection ("Generate More")
- **Pitch invalidation UI**: Deferred to fidelity pass (MVP-CHARTER.md:68)
- **Criterion editing after generation**: Can delete/recreate session for now
- **Multiple active sessions**: Single session for MVP simplicity
- **Session history**: No archive/review of past weeks yet
- **Essential vs optional grocery split**: Deferred to fidelity pass (MVP-CHARTER.md:68)

**Future Features This Enables**:
- Pitch selection (next iteration)
- Flesh-out with ingredient claiming
- Multi-wave generation with claim-aware pivoting
- Shopping list generation from claims

---

## Design Decisions (Aligned)

**Criterion specification UX**:
- ✅ Simple form: Text field (description) + number input (slots)
- Minimal friction, keeps LLM focused on recipe generation not parsing

**Session creation flow**:
- ✅ "Create Session" button on main page as job-to-be-done entrypoint
- One of small handful of primary actions on main page

**Session naming**:
- ✅ Optional field with auto-generation
- Auto-generated format: "Week of [prior Sunday date]"
- User can override with custom name

**Criterion limit**:
- ✅ Maximum 7 criteria per session
- Arbitrary but reasonable constraint for MVP

**Empty state**:
- ✅ Show main page with "Create Session" button
- Display simple message: "No active session" when none exists
- Avoid auto-creation or complex routing

**Session lifecycle**:
- ✅ Deferred - no end state for MVP
- Focus on creation + use, not archival/completion
