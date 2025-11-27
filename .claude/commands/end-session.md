# End Session Command

Synthesize the current session's work and update backlog: $ARGUMENTS

This command helps close out a work session by:
- Reviewing what was accomplished (via git diff)
- Analyzing unstructured session notes or observations
- Triaging insights into actionable next.md items
- Capturing learnings for future reference

Usage: `/end-session` or `/end-session [path-to-session-notes.md]`

---

## Process

### Step 1: Initial Message

I'll help you wrap up this session and triage insights into next.md.

Let me review what happened during this session...

Then continue immediately...

### Step 2: Gather Session Context

**Git Changes** (if in a git repository):
```bash
# Get changes made in this session
git diff HEAD --stat
git log --oneline --since="[session start time or reasonable default]"
```

Summarize:
- Files modified: [list key files]
- Tests added/modified: [count]
- New features/fixes: [brief list]

**Session Notes** (if provided as $ARGUMENTS):
- Read the session scratchpad or notes file
- Extract observations, questions, discoveries

**Current State** (read if exists):
- Check `docs/development/next.md` to understand current backlog
- Note in-progress items

### Step 3: Analyze & Categorize

Based on git changes and session notes, I've identified:

**Accomplishments**:
- [Completed work item] - [Impact]
- [Completed work item] - [Impact]

**Key Learnings**:
- [Technical discovery] - [Why it matters]
- [Design insight] - [Implications]
- [Pattern observed] - [Where it applies]

**Observations to Triage**:

#### → Domain Questions
[Design questions or tensions that need exploration]
- [Question/pain point] - [Context]

#### → Features Ready to Build
[Where domain is clear, just need implementation]
- [Feature idea] - [Domain coverage] - [Rough effort]

#### → Technical Discoveries
[Patterns, libraries, approaches learned]
- [Discovery] - [Relevance]

#### → Open Questions
[Things to investigate later]
- [Question] - [Why it matters]

#### → Future Considerations
[Ideas not ready to prioritize yet]
- [Idea] - [Why interesting]

### Step 4: Update next.md

Now I'll update `docs/development/next.md` with these insights.

**Changes to make**:
- Move [completed item] from "In Progress" to "Recently Completed"
- Add [X] domain questions to "Domain Questions to Explore"
- Add [Y] features to "Features Ready to Build"
- Add [Z] considerations to "Future Considerations"
- Update "Last updated" timestamp

[Make the specific updates to docs/development/next.md]

### Step 5: Present Summary

Session wrapped up! Here's what I captured:

**Completed This Session**:
- [Item] - now in "Recently Completed"
- [Item] - now in "Recently Completed"

**Added to Backlog**:
- **[X] Domain Questions** - ready for `explore-domain-design`
  - [Question 1]
  - [Question 2]
- **[Y] Features Ready** - ready for `create-tip`
  - [Feature 1]
  - [Feature 2]
- **[Z] Future Ideas** - in "Future Considerations"
  - [Idea 1]

**Key Learnings Captured**:
- [Learning] - [Where captured]
- [Learning] - [Where captured]

**Current Backlog State**:
- Domain questions: [count]
- Features ready: [count]
- In progress: [count]
- Future considerations: [count]

**Suggested Next Actions**:
[Based on what was accomplished and what's in the backlog]
1. [Specific next step based on momentum]
2. [Alternative if switching contexts]

Updated: `docs/development/next.md`

[If session notes were provided]:
Session notes preserved at: `[path]` (can archive if desired)

---

## Quality Guidelines

**Good Session Triaging**:
- Specific, actionable items added to next.md
- Learnings captured with enough context to be useful later
- Questions are well-framed (not just "look into X")
- Features have rough effort and domain coverage noted
- Completed items show impact, not just mechanics

**Categorization Wisdom**:
- **Domain Question**: Design tension, uncertain modeling, multiple viable approaches
- **Feature Ready**: Domain is clear, implementation is tractable, just needs planning
- **Future Consideration**: Interesting but not ready (missing dependencies, unclear priority)
- **Open Question**: Technical investigation needed before deciding

**Context Preservation**:
- Enough detail that "future you" understands the observation
- References to files, commits, or docs where relevant
- "Why it matters" captured alongside "what it is"

**Backlog Hygiene**:
- Keep "In Progress" small (1-3 items max)
- Move completed items to "Recently Completed" (keep last 5)
- Archive old items periodically
- Add effort estimates when clear

---

## Notes

**When to Use This**:
- End of a focused work session
- After implementing a feature
- When switching contexts and want to capture state
- After an exploration/spike session

**What Gets Triaged**:
- Observations from session notes
- Implications from code changes
- Questions that emerged
- Design insights
- Technical discoveries
- Follow-up ideas

**What Doesn't Need Triaging**:
- Routine commits without insights
- Minor bug fixes
- Mechanical refactoring
- Standard maintenance work

---

Remember: This command helps you stop without losing context. Good triaging means "future you" can quickly pick up the most valuable next action.
