# Frame Feature Command

Translate prototype learnings into problem framing for: $ARGUMENTS

## Purpose

Bridge discovered pain points to implementation-ready user stories. This command extracts validated learnings from prototype discovery and frames them as problems to solve, with clear acceptance criteria that seed TDD.

**Key Principle**: Align on the nature of the problem before the nature of the solution. User stories capture WHAT users need; technical planning (create-tip) determines HOW.

---

## Path Reference Note

**IMPORTANT**: All file paths are relative to **project root** (`/Users/mcox/dev/harvest-hound/`), NOT current working directory.

From `prototype/`, use `../` to reach project root files.

---

## Context Sources

**Primary**:
- `docs/LEARNINGS.md` - Validated discoveries from prototype phase
- `prototype/` - Current implementation to contrast against

**Secondary** (if relevant):
- `docs/open-questions/` - Unresolved design questions
- `.scratch/pain-*.md` - Recent pain analyses (if any remain)

---

## Process

### Step 1: Acknowledge and Gather Context

"I'll help frame the feature: [topic from $ARGUMENTS]

Let me gather context from our prototype learnings and current implementation..."

Read `docs/LEARNINGS.md` to find relevant validated discoveries.

Explore `prototype/` to understand current implementation state.

### Step 2: Synthesize Relevant Learnings

Present what you found:

**From LEARNINGS.md** (discoveries that inform this feature):
- [Specific learning with checkbox status]
- [Specific learning]
- [Specific learning]

**Current Prototype State**:
- What exists: [current implementation]
- What's missing/broken: [gaps or regressions]
- What works well: [to preserve]

**Related Open Questions** (if any):
- [Question that affects this feature]

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

After user input, create the frame document at `.scratch/frame-[feature-name].md`:

```markdown
# Feature Frame: [Feature Name]

**Date**: [YYYY-MM-DD]
**Status**: Draft - Awaiting Alignment

---

## Problem Statement

[2-3 sentences: What user need does this address? Why does it matter?]

**From Prototype Discovery**:
- [Key learning that validates this need]
- [Key learning]

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

**From LEARNINGS.md**: [Reference to validated discovery]

### Story 2: [Secondary user need]
**As a** [role]
**I want** [capability]
**So that** [benefit/outcome]

**Acceptance Criteria**:
- [ ] [Testable criterion]
- [ ] [Testable criterion]

**From LEARNINGS.md**: [Reference]

[Add more stories as needed - typically 2-4 per feature]

---

## Prototype Contrast

| Aspect | Prototype | MVP | Why Change |
|--------|-----------|-----|------------|
| [Aspect] | [Current state] | [Target state] | [Rationale from learnings] |
| [Aspect] | [Current state] | [Target state] | [Rationale] |

**Preserve from Prototype**:
- [What works well and should be kept]

**Fix from Prototype**:
- [What's broken or missing]

**Change from Prototype**:
- [Deliberate improvements based on learnings]

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

"I've created a feature frame at `.scratch/frame-[feature-name].md`

**Problem**: [One sentence summary]

**Stories**:
1. [Story 1 title] - [Essential/Nice-to-have]
2. [Story 2 title] - [Essential/Nice-to-have]

**Key Contrasts with Prototype**:
- [Main change 1]
- [Main change 2]

**Out of Scope**:
- [Deferred item]

Please review and let me know:
- Are these the right stories for MVP?
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

Update `.scratch/frame-[feature-name].md` with changes.

### Step 7: After Alignment

"Feature frame aligned and saved at `.scratch/frame-[feature-name].md`

**Next step**: Use `create-tip [feature-name]` to plan the technical implementation.

The TIP will use this frame for:
- User stories → Test case inspiration
- Acceptance criteria → TDD seeds
- Scope boundaries → Implementation constraints
- Prototype contrast → Migration/evolution approach"

---

## Quality Guidelines

**Good Feature Frames**:
- Stories grounded in validated learnings (not assumptions)
- Acceptance criteria are testable (seed TDD)
- Scope is constrained (out-of-scope section used)
- Prototype contrast is specific (not vague "improvements")
- Risks identified with resolution paths

**Anti-patterns**:
- Inventing requirements not from learnings
- Vague acceptance criteria ("it should work well")
- Scope creep (trying to solve everything)
- Technical solutions in user stories (HOW not WHAT)
- Ignoring prototype - it has valuable learnings

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

**This command produces**: `.scratch/frame-[feature-name].md`

**Next command**: `create-tip [feature-name]` reads the frame and produces technical plan

**If risks need exploration**: `explore-domain-design [topic]` for architectural decisions

**After implementation**: Delete `.scratch/frame-[feature-name].md` (ephemeral)

---

## Remember

**Frame-feature is about WHAT, not HOW**:
- WHAT problem are we solving?
- WHAT does success look like for users?
- WHAT scope constraints do we have?

Technical decisions (HOW) come in `create-tip`.

**Learnings are your source of truth**:
- LEARNINGS.md contains validated discoveries
- Prototype code shows current reality
- User input resolves ambiguity and priorities

**Acceptance criteria seed TDD**:
- Each criterion should be testable
- These become test case inspiration
- "User can X" → `test_user_can_X()`
