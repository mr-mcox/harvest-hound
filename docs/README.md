# Harvest Hound Documentation

Navigation guide for project documentation.

**Workflow**: This project uses the pi-platform coding workflow (`coding-workflow` skill:
problem-space → solution-space → implement → compact), with agent briefs as the central
artifact (`agent-brief` skill for format).

## For Agents: Finding "Why"

**Answering "Why this feature?"**
→ `roadmap/pain-[feature].md` - Pain point context, user examples, impact
→ `roadmap/phase-recipe-memory.md` - Current phase: insights and named concepts
→ `learnings/domain.md` or `workflows.md` - Validated discoveries

**Answering "Why this approach?"**
→ `PROJECT.md` - Standing constraints, stack, core architectural principles
→ `decisions/decision-[topic].md` - Design rationale, alternatives, trade-offs
→ `learnings/technical.md` - Validated patterns and approaches

**Answering "What's our strategy?"**
→ `roadmap/phase-recipe-memory.md` - **Current phase**: insights, concepts, tensions,
  approach commitments
→ `roadmap/PRIORITIES.md` - Current focus and order

**Answering "What have we learned?"**
→ `learnings/` - All validated discoveries
  - `domain.md` - Domain model, entities, boundaries, modeling decisions
  - `workflows.md` - User behavior patterns, what works/doesn't work
  - `technical.md` - BAML prompts, API shapes, performance learnings
  - `ux.md` - UI/UX patterns, interaction design
  - `architectural.md` - Architecture decisions and patterns

**Answering "What's unresolved?"**
→ `roadmap/pain-*.md` (status: Later) - Deferred pain points
→ `roadmap/phase-recipe-memory.md` - Open questions section
→ `features/` - Active agent briefs (work in progress)

---

## Document Lifecycle

**Strategic** (long-lived, rarely deleted):
- `PROJECT.md` - Standing constraints and validated bets, phase-independent
- `learnings/*.md` - Append-only validated discoveries (annotate superseded entries in
  place, don't delete)
- `decisions/*.md` - Permanent design rationale

**Tactical** (medium-lived, archived when addressed):
- `roadmap/phase-*.md` - Current-phase insight handoff; superseded when the phase completes
- `roadmap/pain-*.md` - Until addressed, then moved to archive/
- `roadmap/PRIORITIES.md` - Living document, frequently updated

**Ephemeral** (deleted after compaction):
- `features/[feature-name]/brief.md` - Agent brief governing one feature (see `agent-brief`
  skill for format and phases)
- `features/[feature-name]/decisions.md` - Running decision log during implementation

---

## Compaction (end of a feature)

When a feature's implementation completes (compact phase of the coding workflow):

1. **Extract significant decisions** → `decisions/decision-[topic].md`
   (why A over B, alternatives, accepted trade-offs)
2. **Extract validated learnings** → append to `learnings/[category].md`
   (what worked/surprised, patterns; use the existing entry format with discovery context
   and date)
3. **Delete the feature directory** — briefs are scaffolding; decisions and learnings are
   the permanent record.
4. **Update** `roadmap/PRIORITIES.md` and move the addressed `pain-*.md` to archive.

**The goal**: Preserve high-value context, remove scaffolding, avoid information loss.
