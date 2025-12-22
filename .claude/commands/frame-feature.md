# Frame Feature Command

Translate pain points and learnings into problem framing for: $ARGUMENTS

## Purpose

Bridge discovered pain points to implementation-ready user stories. This command extracts validated learnings and frames them as problems to solve, with clear acceptance criteria that seed TDD.

**Key Principle**: Align on the nature of the problem before the nature of the solution. User stories capture WHAT users need; technical planning (create-tip) determines HOW.

---

## Path Reference Note

**IMPORTANT**: All file paths are relative to **project root** (`/Users/mcox/dev/harvest-hound/`), NOT current working directory.

---

## Context Sources

**Primary**:
- `docs/roadmap/pain-[feature].md` - Pain point context, user examples, solution direction
- `docs/roadmap/PRIORITIES.md` - Current priorities and strategic focus
- `docs/MVP-CHARTER.md` - Scope, priorities, and architectural bets
- `docs/learnings/` - Validated discoveries (domain, workflows, technical, ux, architectural)
- `src/` - Current implementation to understand existing patterns

**Secondary** (if relevant):
- `docs/decisions/` - Design decisions that may affect this feature

**Available Agents**:
- `docs-locator` - Find relevant docs (use first for discovery)
- `docs-synthesizer` - Extract insights from docs (use after locator identifies files)

---

## Process

### Step 1: Acknowledge and Gather Context

"I'll help frame the feature: [topic from $ARGUMENTS]

Let me gather context from roadmap, learnings, and current implementation..."

**Check roadmap first**:
- Read `docs/roadmap/pain-[feature].md` (if exists) for pain point context
- Read `docs/roadmap/PRIORITIES.md` to see where this fits (Now/Next/Later)

Read `docs/MVP-CHARTER.md` to understand:
- Is this feature in scope for MVP?
- What architectural bets apply?
- Any explicit out-of-scope items to respect?

Read relevant `docs/learnings/` files to find validated discoveries:
- `domain.md` for entity relationships and boundaries
- `workflows.md` for user behavior patterns
- `technical.md` for proven patterns
- `ux.md` for interaction patterns

**Optional**: Use `docs-locator` to find additional relevant docs, then `docs-synthesizer` to extract key insights.

Explore `src/` to understand current implementation patterns.

### Step 2: Synthesize Relevant Context

Present what you found:

**From Roadmap**:
- Pain point: [Summary from `roadmap/pain-[feature].md`]
- Priority: [Now / Next / Later from `roadmap/PRIORITIES.md`]
- User examples: [Key quotes or scenarios]

**From MVP-CHARTER.md**:
- Scope alignment: [Steel thread complete, in refinement / Future enhancement]
- Relevant architectural bets: [List any that apply]
- Constraints to respect: [Any explicit boundaries]

**From learnings/** (discoveries that inform this feature):
- Domain: [Relevant entity/boundary learnings]
- Workflows: [Relevant user behavior patterns]
- Technical: [Relevant proven patterns]
- UX: [Relevant interaction patterns]

**Current Implementation**:
- What exists: [relevant current code/patterns]
- What's missing: [gaps this feature will fill]
- What works well: [to preserve/build on]

**Related Decisions** (if any from `decisions/`):
- [Decision that affects this feature]

### Step 3: Ask Clarifying Questions

Questions to sharpen the problem framing:

**Scope & Priority**:
- Which aspects are essential vs nice-to-have for MVP?
- Are there parts we should explicitly defer?

**User Experience**:
- What's the ideal workflow for this feature?
- What would make you say "oh, that's nice!"?

**Constraints**:
- Any must-preserve behaviors from prototype?
- Any anti-patterns to avoid?

Then WAIT for user responses.

### Step 4: Generate Feature Frame

After user input, create the frame document at `docs/implementation/frame-[feature-name].md`:

```markdown
# Feature Frame: [Feature Name]

**Date**: [YYYY-MM-DD]
**Status**: Draft - Awaiting Alignment

---

## Problem Statement

[2-3 sentences: What user need does this address? Why does it matter?]

**From Pain Point** (`roadmap/pain-[feature].md`):
- [Key user quote or example]
- [Impact on workflow]

**From Learnings** (`learnings/`):
- [Domain/workflow/technical learning that validates this need]
- [Supporting learning]

---

## User Stories

### Story 1: [Primary user need]
**As a** [role - usually "meal planner"]
**I want** [capability]
**So that** [benefit/outcome]

**Acceptance Criteria**:
- [ ] [Testable criterion - becomes TDD seed]
- [ ] [Testable criterion]
- [ ] [Testable criterion]

**From learnings/**: [Reference to validated discovery with file]

### Story 2: [Secondary user need]
**As a** [role]
**I want** [capability]
**So that** [benefit/outcome]

**Acceptance Criteria**:
- [ ] [Testable criterion]
- [ ] [Testable criterion]

**From learnings/**: [Reference]

[Add more stories as needed - typically 2-4 per feature]

---

## Current State vs Target

| Aspect | Current | Target | Why Change |
|--------|---------|--------|------------|
| [Aspect] | [Current state] | [Target state] | [Rationale from learnings/pain point] |
| [Aspect] | [Current state] | [Target state] | [Rationale] |

**Build On**:
- [What works well in current implementation]

**Add**:
- [New capabilities needed]

**Change**:
- [Deliberate improvements based on learnings/pain point]

---

## Out of Scope (Deferred)

Explicitly NOT part of this feature:
- [Capability]: Deferred because [reason]
- [Capability]: Deferred because [reason]

**Future Features This Enables**:
- [Feature that builds on this]

---

## Open Risks

[Only if there are unresolved questions that could affect approach]

- **[Risk]**: [Description and impact]
  - Options: [A vs B]
  - Suggest: [Resolution path - explore-domain-design? User decision?]

---

## Questions for Alignment

Before proceeding to technical planning:

1. [Question about scope or priority]
2. [Question about user experience detail]
3. [Question needing user judgment]
```

### Step 5: Present for Alignment

"I've created a feature frame at `docs/implementation/frame-[feature-name].md`

**Problem**: [One sentence summary]

**Stories**:
1. [Story 1 title] - [Essential/Nice-to-have]
2. [Story 2 title] - [Essential/Nice-to-have]

**Key Changes from Current**:
- [Main change 1]
- [Main change 2]

**Out of Scope**:
- [Deferred item]

Please review and let me know:
- Are these the right stories?
- Is the scope appropriately constrained?
- Any acceptance criteria missing or wrong?
- Ready to proceed to technical planning?"

Then WAIT for user feedback.

### Step 6: Iterate on Feedback

Incorporate user feedback:
- Adjust story priorities (essential vs nice-to-have)
- Refine acceptance criteria
- Adjust scope boundaries
- Add/remove stories as directed

Update `docs/implementation/frame-[feature-name].md` with changes.

### Step 7: After Alignment

"Feature frame aligned and saved at `docs/implementation/frame-[feature-name].md`

**Next step**: Use `create-tip [feature-name]` to plan the technical implementation.

The TIP will use this frame for:
- User stories → Test case inspiration
- Acceptance criteria → TDD seeds
- Scope boundaries → Implementation constraints
- Current state contrast → Build/change/add approach"

---

## Quality Guidelines

**Good Feature Frames**:
- Stories grounded in pain points and validated learnings (not assumptions)
- Acceptance criteria are testable (seed TDD)
- Scope is constrained (out-of-scope section used)
- Current state contrast is specific (not vague "improvements")
- Builds on existing patterns where appropriate
- Risks identified with resolution paths

**Anti-patterns**:
- Inventing requirements not from pain points/learnings
- Vague acceptance criteria ("it should work well")
- Scope creep (trying to solve everything)
- Technical solutions in user stories (HOW not WHAT)
- Ignoring current implementation - it has valuable patterns

**Story Sizing**:
- Each story should be independently valuable
- If a story has 8+ acceptance criteria, consider splitting
- Essential stories vs nice-to-have should be explicit

---

## Feature Batching (Optional)

If framing multiple related features:

"These features share context and could be batched:
- [Feature A]: [Brief description]
- [Feature B]: [Brief description]

Would you like to frame them together? This can:
- Surface shared acceptance criteria
- Identify natural implementation sequence
- Reduce planning overhead"

---

## Integration with Other Commands

**This command produces**: `docs/implementation/frame-[feature-name].md`

**Input from**:
- `roadmap/pain-[feature].md` (pain point context)
- `roadmap/PRIORITIES.md` (priority/timing)

**Next command**: `create-tip [feature-name]` reads the frame and produces technical plan

**After implementation**: `end-session` may distill learnings, then delete frame (ephemeral)

---

## Remember

**Frame-feature is about WHAT, not HOW**:
- WHAT problem are we solving? (from pain point)
- WHAT does success look like for users? (acceptance criteria)
- WHAT scope constraints do we have? (in/out of scope)

Technical decisions (HOW) come in `create-tip`.

**Pain points + learnings are your source of truth**:
- `roadmap/pain-*.md` contains user context and examples
- `learnings/*.md` contains validated discoveries
- Current `src/` code shows working patterns
- User input resolves ambiguity and priorities

**Acceptance criteria seed TDD**:
- Each criterion should be testable
- These become test case inspiration
- "User can X" → `test_user_can_X()`
