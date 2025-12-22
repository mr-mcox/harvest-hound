# Harvest Hound Documentation

Navigation guide for project documentation.

## For Agents: Finding "Why"

**Answering "Why this feature?"**
→ `roadmap/pain-[feature].md` - Pain point context, user examples, impact
→ `learnings/domain.md` or `workflows.md` - Validated discoveries

**Answering "Why this approach?"**
→ `decisions/decision-[topic].md` - Design rationale, alternatives, trade-offs
→ `learnings/technical.md` - Validated patterns and approaches
→ `MVP-CHARTER.md` - Architectural bets and constraints

**Answering "What's our strategy?"**
→ `MVP-CHARTER.md` - Scope, priorities, success criteria
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
→ `implementation/` - Active work in progress

---

## Document Lifecycle

**Strategic** (long-lived, rarely deleted):
- `MVP-CHARTER.md` - Updated as strategy evolves
- `learnings/*.md` - Append-only validated discoveries
- `decisions/*.md` - Permanent design rationale

**Tactical** (medium-lived, archived when addressed):
- `roadmap/pain-*.md` - Until addressed, then moved to archive/
- `roadmap/PRIORITIES.md` - Living document, frequently updated

**Ephemeral** (deleted after use):
- `implementation/frame-*.md` - Deleted after feature implemented (context distilled to decisions/learnings)
- `implementation/tip-*.md` - Deleted after implementation complete (context distilled to decisions/learnings)

---

## By Purpose

| Purpose | Location | Lifespan | Updated By |
|---------|----------|----------|------------|
| Strategic direction | `MVP-CHARTER.md` | Long | `/end-session` (rarely) |
| Current priorities | `roadmap/PRIORITIES.md` | Medium | `/end-session` |
| Validated learnings | `learnings/*.md` | Long | `/end-session` |
| Pain points | `roadmap/pain-*.md` | Medium | `/end-session` |
| Design rationale | `decisions/decision-*.md` | Long | `/end-session` (distilled from TIPs) |
| Feature framing | `implementation/frame-*.md` | Ephemeral | `/frame-feature` |
| Implementation plans | `implementation/tip-*.md` | Ephemeral | `/create-tip` |

---

## Cross-References

### Priority System
- **Learning**: `learnings/domain.md` (Priority drives recipe importance)
- **Learning**: `learnings/workflows.md` (Flat ingredient view with priority)
- **Pain**: `roadmap/pain-priority-pairing.md` (Gap for pantry items)
- **Decision**: TBD (approach to fix pairing)

### Recipe Editing
- **Learning**: `learnings/workflows.md` (Recipe editing essential for cooking workflow)
- **Pain**: `roadmap/pain-recipe-editing.md` (Context, examples, solution direction)
- **Decision**: TBD (chat vs edit approach)

### Shopping List
- **Learning**: `learnings/workflows.md` (Shopping list fills workflow gap)
- **Learning**: `learnings/technical.md` (Likelihood-based ingredient sourcing)
- **Pain**: Addressed (shopping list selection implemented)
- **TIP**: `implementation/tip-shopping-list-selection.md` (can be archived)

### Ingredient Claiming
- **Learning**: `learnings/domain.md` (Ingredient claiming is CRITICAL)
- **Learning**: `learnings/technical.md` (LLM/code separation, quantity-aware claiming)
- **Learning**: `learnings/workflows.md` (Sequential claiming prevents conflicts)
- **Decision**: TBD (could distill claiming model decision from early TIPs)

---

## Distillation Process

When completing implementation (during `/end-session`):

1. **Review completed TIPs** in `implementation/`
2. **Extract significant decisions** → Create `decisions/decision-[topic].md`
   - Why approach A over B?
   - What alternatives were considered?
   - What trade-offs did we accept?
3. **Extract validated learnings** → Add to `learnings/[category].md`
   - What worked better/worse than expected?
   - What patterns emerged?
   - What surprises did we discover?
4. **Delete ephemeral docs** after distillation
   - Frames and TIPs are scaffolding
   - Decisions and learnings are essence

**The goal**: Preserve high-value context, remove scaffolding, avoid information loss.
