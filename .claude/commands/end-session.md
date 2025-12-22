# End Session Command

Wrap up the current session and triage insights: $ARGUMENTS

## Purpose

Close out a work session by capturing learnings and preparing for the next session. Balances:
- **What's obvious** (from git, completed work) - Claude synthesizes
- **What needs reflection** (surprises, friction, insights) - User provides context

**Key Principle**: Learnings inform the MVP workflow. Session insights feed into `frame-feature` decisions, roadmap priorities, and strategic direction.

---

## Path Reference Note

**IMPORTANT**: All file paths are relative to **project root** (`/Users/mcox/dev/harvest-hound/`), NOT current working directory.

---

## Target Files

**Updates**:
- `docs/MVP-CHARTER.md` - Scope, priorities, architectural bets (if learnings warrant)
- `docs/learnings/*.md` - Validated discoveries (categorized by domain/workflow/technical/ux/architectural)
- `docs/roadmap/PRIORITIES.md` - Current priorities and strategic focus
- `docs/roadmap/pain-*.md` - New pain points discovered

**Creates** (distillation from ephemeral docs):
- `docs/decisions/decision-*.md` - Significant design decisions (distilled from TIPs)

**Cleanup candidates**:
- `docs/implementation/frame-*.md` - Completed feature frames (delete after distillation)
- `docs/implementation/tip-*.md` - Completed TIPs (delete after distillation)

---

## Process

### Step 1: Gather Session Context

"Let me review what happened this session..."

**Git Changes** (run automatically):
```bash
git diff HEAD --stat
git log --oneline -10
```

Summarize:
- Files modified: [key files]
- Features/fixes: [brief list]
- Tests added: [if any]

**Check for completed work**:
- Any `docs/implementation/frame-*.md` files that were implemented?
- Any `docs/implementation/tip-*.md` that were completed?

Present: "Based on git, it looks like you worked on [summary]. Let me ask a few questions to capture insights."

### Step 2: Gather User Reflections

Ask targeted questions, then WAIT for responses:

**About What Worked:**
- What felt smooth or natural during this session?
- Any "oh, that's nice" moments?
- Patterns that paid off?

**About Friction:**
- Where did you get stuck or slow down?
- Anything surprisingly hard?
- Workarounds you had to use?

**About Discoveries:**
- Did you learn anything that changes how you think about the MVP?
- Any scope creep you had to resist (or gave into)?
- Technical approaches that worked better/worse than expected?

**About Next Session:**
- What's the most valuable next step?
- Anything you want to make sure doesn't get lost?

Then WAIT for user responses before proceeding.

### Step 3: Distill Ephemeral Documents

**For completed TIPs** (`docs/implementation/tip-*.md`):

"I see you completed `tip-[name].md`. Let me check if there are decisions or learnings worth preserving..."

Ask user:

**1. Significant design decisions made?**
- "During implementation, did you choose between meaningful alternatives?"
- "Was there a 'why approach A over B' decision worth documenting?"
- Examples: "Why BAML streaming vs batch?", "Why claims model over direct updates?"

**2. Validated learnings discovered?**
- "What worked better/worse than expected?"
- "Any surprises during implementation that others should know?"
- Examples: "LLM/code separation reduced cognitive load", "Sequential claiming prevents conflicts"

**If YES to significant decisions**:

Create `docs/decisions/decision-[topic].md`:

```markdown
# Decision: [Topic]

**Date**: [YYYY-MM-DD]
**Context**: [Feature/TIP that drove this decision]
**Status**: Accepted

## Decision

[What we decided to do]

## Rationale

[Why we chose this approach]

## Alternatives Considered

- **[Alternative A]**: [Why we didn't choose this]
- **[Alternative B]**: [Why we didn't choose this]

## Trade-offs Accepted

- [What we gave up for this approach]
- [Technical debt or limitations]

## Consequences

- **Enables**: [What this makes possible]
- **Constrains**: [What this limits]

## References

- Implemented in: [PR/commit if applicable]
- Original TIP: `docs/implementation/tip-[name].md` (deleted [date])
- Related pain point: `docs/roadmap/pain-[name].md` (if applicable)
```

**If YES to validated learnings**:

Categorize and add to appropriate `docs/learnings/[category].md`:
- **Domain insights** → `learnings/domain.md`
- **Workflow patterns** → `learnings/workflows.md`
- **Technical discoveries** → `learnings/technical.md`
- **UX insights** → `learnings/ux.md`
- **Architectural patterns** → `learnings/architectural.md`

Format:
```markdown
- [x] **[Learning]**: [Specific insight]
  - [Supporting detail from implementation]
  - [User reaction if applicable]
  - (discovered: [feature] implementation, [date])
```

**For completed frames** (`docs/implementation/frame-*.md`):
- Pain point context already in `docs/roadmap/pain-*.md` ✓
- User stories served their purpose for TDD ✓
- Mark frame for deletion (no distillation needed)

**Present distillation summary**:

"From completed implementation:

**Decisions worth preserving**:
- Created `docs/decisions/decision-[topic].md` ([brief description])
- Or: "No significant decisions to preserve"

**Learnings added**:
- `learnings/[category].md`: [Brief description]
- Or: "No new learnings to document"

**Ready to delete** (context preserved):
- `implementation/tip-[name].md`
- `implementation/frame-[name].md`

Shall I delete these now or leave for you to review?"

### Step 4: Categorize Insights

Based on git changes AND user reflections, categorize:

**Charter-Relevant** (affects `docs/MVP-CHARTER.md`):
- Scope changes: Features that should move in/out of MVP
- Architectural learnings: Patterns better/worse than expected
- Success criteria: Definition of "done" needs refinement

**Learnings-Relevant** (validated discoveries):
- Domain insights → `learnings/domain.md`
- Workflow patterns → `learnings/workflows.md`
- Technical discoveries → `learnings/technical.md`
- UX insights → `learnings/ux.md`
- Architectural patterns → `learnings/architectural.md`

**Roadmap-Relevant** (pain points and priorities):
- New pain points → Create `roadmap/pain-[name].md`
- Priority changes → Update `roadmap/PRIORITIES.md`

**Next Session Prep**:
- Ready for `frame-feature`: [Check `roadmap/PRIORITIES.md` for Next items]
- Needs exploration: [Questions requiring investigation]
- Blocked on: [External dependencies or decisions]

### Step 5: Update MVP Charter (if applicable)

Only update charter for significant learnings:

**Scope changes**:
- Features essential that weren't listed
- Features that should be deferred
- New out-of-scope items

**Architectural learnings**:
- Patterns that worked better/worse
- Technical debt decisions to update
- New constraints discovered

**Success criteria**:
- Steel thread complete criteria changed
- Definition of "done" refined

If changes needed, update `docs/MVP-CHARTER.md`:
- Update relevant section
- Update "Last Updated" date
- Note: "Changed: [Section] - [What] - [Why]"

### Step 6: Update Learnings (if applicable)

For validated discoveries not already captured in distillation, update appropriate `docs/learnings/[category].md`:

**Format**:
```markdown
- [x] **[Discovery]**: [Specific insight]
  - [Supporting detail]
  - (discovered: [context], [date])
```

**DO Document**:
- Actual user reactions
- Surprise discoveries
- Workflow preferences
- Complexity assessments
- Domain boundaries

**DON'T Document**:
- Code structure details
- Implementation specifics
- Speculative improvements
- Things not validated by use

**Categorization Guide**:
- **domain.md**: Entity relationships, boundaries, modeling decisions
- **workflows.md**: User behavior patterns, what works/doesn't
- **technical.md**: BAML prompts, API shapes, performance
- **ux.md**: UI/UX patterns, interaction design
- **architectural.md**: Architecture decisions, patterns to keep/change

### Step 7: Update Roadmap (if applicable)

**For new pain points**, create `docs/roadmap/pain-[name].md`:

```markdown
# [Pain Point Title]

**Status**: Next | Later | On Hold
**Impact**: Critical | High | Medium | Low
**Discovered**: [YYYY-MM-DD] ([context])
**Related**: [Charter/learnings references if applicable]

## The Pain

[Description of the problem from user perspective]

### User Examples

> [Quote or specific example from user]

## Why It Matters

1. [Impact on workflow/experience]
2. [Consequence if not addressed]

## Solution Direction

[Potential approaches to solve this]

## Potential Breakdown

[If complex, how might this be tackled piece by piece]

## Notes

[Additional context, user preferences, related work]
```

**Update `docs/roadmap/PRIORITIES.md`** if priorities changed:
- Move items between Now/Next/Later
- Update strategy notes
- Update "Last Updated" date

### Step 8: Cleanup Completed Artifacts

Check for completed work to clean up:

**Feature Frames** (`docs/implementation/frame-*.md`):
- If feature implemented: "Frame for [feature] can be deleted - code is source of truth now"
- Don't auto-delete; note for user

**TIPs** (`docs/implementation/tip-*.md`):
- If implementation complete AND distilled: "TIP for [feature] can be deleted - decisions/learnings preserved"
- Don't auto-delete; note for user

### Step 9: Present Summary

"Session wrapped up! Here's what I captured:

**Completed This Session**:
- [Item] - [Impact/outcome]

**Charter Updates**:
- [Section changed] - [Brief description]
- Or: "No charter changes needed"

**Learnings Updates**:
- `learnings/[category].md`: [Key insight added]
- Or: "No new learnings to document"

**Decisions Preserved**:
- `decisions/decision-[topic].md`: [Brief description]
- Or: "No significant decisions to preserve"

**Roadmap Updates**:
- Created `roadmap/pain-[name].md`
- Updated `roadmap/PRIORITIES.md`: [change]
- Or: "No roadmap changes needed"

**Cleanup Ready**:
- [Files that can be deleted]

**Suggested Next Session**:
- **If continuing current work**: [Specific next step]
- **If starting fresh**: [Most valuable item from `roadmap/PRIORITIES.md` Next section]
- **If exploring**: [Question worth investigating]

Ready to pick up here next time!"

---

## Quality Guidelines

**Good Session Wrap-ups**:
- Capture user context that git can't show
- Distill decisions/learnings from TIPs before deleting
- Connect insights to roadmap priorities
- Set up clear next session starting point
- Don't over-document routine work

**When to Update Charter**:
- Scope boundary was tested and needs adjustment
- Architectural bet proved right/wrong
- Success criteria need refinement
- NOT for minor implementation details

**When to Update Learnings**:
- Something was validated through actual use
- A discovery changes how you think about domain/workflow/technical approach
- NOT for code patterns (those live in code)

**When to Create Decision Doc**:
- Meaningful choice between alternatives was made
- Trade-offs were considered and accepted
- Future implementers need to understand "why this way"
- NOT for obvious or trivial choices

**When to Create Pain Point**:
- User friction discovered through real use
- Gap in current system identified
- Feature need surfaced
- NOT for minor polish or nice-to-haves (unless part of pattern)

**Categorization Wisdom**:
- **Charter-relevant**: Changes strategic direction
- **Learnings-relevant**: Validated discovery about domain/workflow/technical
- **Decisions**: Why we chose approach A over B
- **Roadmap**: Pain points to address, priority changes
- **Neither**: Routine implementation (no documentation needed)

---

## Integration with MVP Workflow

**This command connects**:
- FROM: Implementation work guided by TIPs
- TO: Next `frame-feature` or continued implementation

**Session insights feed**:
- `docs/MVP-CHARTER.md` - Strategic scope/architecture updates
- `docs/learnings/*.md` - Validated discoveries (categorized)
- `docs/decisions/*.md` - Design decisions (distilled from TIPs)
- `docs/roadmap/` - Pain points and priorities
- Next `frame-feature` - Features ready to frame from roadmap

**Don't capture here** (other commands handle):
- Feature framing → `frame-feature` (creates frames in implementation/)
- Technical planning → `create-tip` (creates TIPs in implementation/)
- Domain exploration → `explore-domain-design` (if we use this)

---

## Remember

**Balance obvious and reflective**:
- Git tells WHAT changed
- User tells WHY it matters
- Distillation preserves high-value context

**Keep it lightweight**:
- Not every session needs charter updates
- Not every session has learnings worth documenting
- Not every TIP needs a decision doc
- Some sessions are just "made progress, moving on"

**Preserve before deleting**:
- Distill decisions from TIPs → `decisions/`
- Extract learnings from implementation → `learnings/`
- Capture new pain points → `roadmap/`
- THEN delete ephemeral docs

**Set up next session**:
- Clear starting point from `roadmap/PRIORITIES.md`
- No lost context (distilled to permanent docs)
- Ready to `frame-feature` or continue
