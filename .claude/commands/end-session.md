# End Session Command

Wrap up the current session and triage insights: $ARGUMENTS

## Purpose

Close out a work session by capturing learnings and preparing for the next session. Balances:
- **What's obvious** (from git, completed work) - Claude synthesizes
- **What needs reflection** (surprises, friction, insights) - User provides context

**Key Principle**: Learnings inform the MVP workflow. Session insights feed into `frame-feature` decisions and `docs/MVP-CHARTER.md` evolution.

---

## Path Reference Note

**IMPORTANT**: All file paths are relative to **project root** (`/Users/mcox/dev/harvest-hound/`), NOT current working directory.

---

## Target Files

**Updates**:
- `docs/MVP-CHARTER.md` - Scope, priorities, architectural bets (if learnings warrant)
- `docs/LEARNINGS.md` - Validated discoveries

**Cleanup candidates**:
- `.scratch/frame-*.md` - Completed feature frames
- `docs/development/tips/tip-*.md` - Completed TIPs

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
- Any `.scratch/frame-*.md` files that were implemented?
- Any `docs/development/tips/tip-*.md` that were completed?

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

### Step 3: Categorize Insights

Based on git changes AND user reflections, categorize:

**Charter-Relevant** (affects `docs/MVP-CHARTER.md`):
- Scope changes: Features that should move in/out of MVP
- Architectural learnings: Patterns better/worse than expected
- Success criteria: Definition of "done" needs refinement

**LEARNINGS.md-Relevant** (validated discoveries):
- Domain insights: Concepts, workflows, boundaries
- Technical discoveries: BAML, API, performance
- Use case validation: Essential, nice-to-have, not needed

**Next Session Prep**:
- Ready for `frame-feature`: [Features clear enough to frame]
- Needs exploration: [Questions requiring investigation]
- Blocked on: [External dependencies or decisions]

### Step 4: Update MVP Charter (if applicable)

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

### Step 5: Update LEARNINGS.md (if applicable)

For validated discoveries, update `docs/LEARNINGS.md`:

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

### Step 6: Cleanup Completed Artifacts

Check for completed work to clean up:

**Feature Frames** (`.scratch/frame-*.md`):
- If feature implemented: "Frame for [feature] can be deleted - code is source of truth now"
- Don't auto-delete; note for user

**TIPs** (`docs/development/tips/tip-*.md`):
- If implementation complete: "TIP for [feature] can be deleted"
- Don't auto-delete; note for user

### Step 7: Present Summary

"Session wrapped up! Here's what I captured:

**Completed This Session**:
- [Item] - [Impact/outcome]

**Charter Updates**:
- [Section changed] - [Brief description]
- Or: "No charter changes needed"

**LEARNINGS.md Updates**:
- [Section]: [Key insight added]
- Or: "No new learnings to document"

**Cleanup Ready**:
- [Files that can be deleted]

**Suggested Next Session**:
- **If continuing current work**: [Specific next step]
- **If starting fresh**: [Most valuable `frame-feature` candidate]
- **If exploring**: [Question worth investigating]

Ready to pick up here next time!"

---

## Quality Guidelines

**Good Session Wrap-ups**:
- Capture user context that git can't show
- Connect insights to MVP workflow (charter, learnings)
- Set up clear next session starting point
- Don't over-document routine work

**When to Update Charter**:
- Scope boundary was tested and needs adjustment
- Architectural bet proved right/wrong
- Success criteria need refinement
- NOT for minor implementation details

**When to Update LEARNINGS.md**:
- Something was validated through actual use
- A discovery changes how you think about domain
- NOT for code patterns (those live in code)

**Categorization Wisdom**:
- **Charter-relevant**: Changes strategic direction
- **LEARNINGS-relevant**: Validated discovery about domain/workflow
- **Neither**: Routine implementation (no documentation needed)

---

## Integration with MVP Workflow

**This command connects**:
- FROM: Implementation work guided by TIPs
- TO: Next `frame-feature` or continued implementation

**Session insights feed**:
- `docs/MVP-CHARTER.md` - Strategic scope/architecture updates
- `docs/LEARNINGS.md` - Validated discoveries
- Next `frame-feature` - Features ready to frame

**Don't capture here** (other commands handle):
- Feature framing → `frame-feature`
- Technical planning → `create-tip`
- Domain exploration → `explore-domain-design`

---

## Remember

**Balance obvious and reflective**:
- Git tells WHAT changed
- User tells WHY it matters

**Keep it lightweight**:
- Not every session needs charter updates
- Not every session has learnings worth documenting
- Some sessions are just "made progress, moving on"

**Set up next session**:
- Clear starting point
- No lost context
- Ready to `frame-feature` or continue
