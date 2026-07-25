# Recipe Feedback/Ratings

**Status**: Next (phase: Recipe Memory & Trust — the attention layer of the durable-recipe
spine, see `phase-recipe-memory.md` Insight 4)
**Impact**: Medium - Trust in metadata, "greatest hits" recall
**Discovered**: 2025-12-21 (Week 3 production use)
**Related**: `phase-recipe-memory.md`, `pain-saved-recipes.md`, `pain-pitch-time-mismatch.md`

**Framing**: Rating and feedback are **attention signals for recipe memory** — resurfacing
ranks candidates by recency-of-cooked and rating. Time-actuals feed the pitch-fidelity
trust loop. Sequencing: after durable recipes v1 — capture at the existing "cooked"
transition, consume during resurfacing.

## The Pain

Recipe metadata (especially time estimates) can be unreliable, and there's no way to capture user experience or mark successful recipes for future reference.

### User Examples

> "The thai curry I made last night tasted great but the 45 minutes active prep was a dirty rotten lie - It was more like 70 minutes prep and 90 minutes to get on the table."

## Why It Matters

1. **Trust in estimates**: Inaccurate time estimates affect planning (dinner timing, weeknight vs. weekend selection)
2. **Recipe quality**: Can't distinguish "would make again" from "never again"
3. **Learning loop**: No feedback mechanism to improve recipe generation over time

## What to Capture

Based on user example:
- Actual prep time vs. estimated
- Actual total time vs. estimated
- Taste/quality rating
- Difficulty assessment
- "Would make again" flag

## Solution Direction

Post-cooking feedback capability:
- Quick feedback form after marking recipe as cooked
- Capture time actuals, rating, notes
- Use to surface "greatest hits" for future sessions
- Potentially feed back into recipe generation (prefer patterns that worked)

## Relationship to Saved Recipes

Overlaps with `pain-saved-recipes` - feedback mechanism could identify recipes worth saving/revisiting.

## Notes

Post-MVP feature - not blocking current workflow, but would enhance trust and create learning loop.
