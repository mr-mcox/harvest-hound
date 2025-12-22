# Decision: Per-Criterion Independent Pitch Generation

**Date**: 2025-12-13
**Context**: Pitch Lifecycle & Generation Fixes
**Status**: Accepted

## Decision

Generate pitches independently for each criterion based on its own unfilled slots, rather than using global proportional distribution across all criteria. Skip criteria where all slots are filled.

## Rationale

### The Bug
Original implementation forced ALL criteria to receive ≥1 pitch via `max(1, round(criterion_share))`, even when criteria had all slots filled. This caused:
- Wasted LLM calls generating pitches user can't use
- Confusing counts (2 pitches for fully-filled criterion)
- Wrong mental model (pitches competing for shared budget)

### The Insight
**Criteria are independent meal planning contexts**, not competing slices of a global budget:
- "3 quick weeknight meals" is separate from "2 weekend cooking projects"
- Each criterion manages its own slot tracking
- User interacts with each criterion independently
- No reason to artificially limit one criterion because another needs pitches

### The Fix
For each criterion:
1. Calculate `unfilled_slots = criterion.slots - count(planned_recipes_for_criterion)`
2. If `unfilled_slots <= 0`: skip (don't generate)
3. If `unfilled_slots > 0`: generate pitches based on criterion's own needs

Much simpler than proportional distribution. No global coordination needed.

## Alternatives Considered

- **Proportional distribution with skip logic**: Still too complex
  - Would need to redistribute skipped criterion's share to others
  - Creates dependencies between criteria (one affects others)
  - Not how users think about meal planning

- **Global pitch budget with priority ranking**: Over-engineered
  - Criteria aren't competing resources
  - User has mental model of "fill slots per criterion"
  - Adding priority system adds complexity without user value

- **Generate for all criteria, filter in UI**: Wasteful
  - Still making unnecessary LLM calls
  - Backend knows which criteria need pitches, should skip

## Trade-offs Accepted

**Limitations**:
- No global optimization across criteria
  - Can't "borrow" unused slots from one criterion for another
  - Accepted: Not how users conceptualize meal planning

- Criteria are siloed
  - User might want "meals that work for both quick and weekend"
  - Accepted: Can manually select same pitch for multiple criteria if needed

**Constraints**:
- Slot tracking must be accurate for each criterion
- Planned recipe counting must be criterion-scoped

## Consequences

**Enables**:
- Correct pitch counts (only for unfilled criteria)
- No wasted LLM calls (efficiency + cost savings)
- Simpler mental model (criteria are independent)
- Easier to understand and maintain (no global distribution math)

**Constrains**:
- Each criterion must track its own state (slots, planned recipes)
- Can't do global optimizations across criteria

**Simplifies**:
- Generation logic: No proportional distribution calculations
- Testing: Each criterion can be tested independently
- Debugging: Easier to trace why a criterion got N pitches

## References

- Implemented in: PR #41 (fix: Pitch lifecycle)
- Original TIP: `docs/implementation/tip-pitch-lifecycle-fixes.md` (deleted 2025-12-22)
- Related learnings:
  - `learnings/workflows.md`: Multi-wave generation critical for iterative workflow
  - `learnings/ux.md`: Focus on meal slots, not pitch counts
