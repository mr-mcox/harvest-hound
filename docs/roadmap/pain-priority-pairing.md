# Priority System Gap (Pantry Pairing)

**Status**: Now
**Impact**: High - Pantry items not getting used
**Discovered**: 2025-12-21 (Week 3 production use)
**Related**: `pain-import-priority-adjustment.md`, `phase-recipe-memory.md` (coverage invariant)

## The Pain

The priority system works well for CSA produce (time-to-spoil freshness model) but fails for pantry items like dried beans and canned goods. These items are technically low-priority (won't spoil soon) but user wants them worked into meal plans.

### User Examples

> "I've got quite a few dried beans and while, yeah, they'll last a while, I've also had them sitting around for a year. They're technically low priority, but I want them worked in."

> "Similar thing with some of my canned sauces. I bumped up priority of japanese curry mix just to get it used."

## Why It Matters

1. **Pantry accumulation**: Long-shelf-life items sit unused even though user wants to use them
2. **Artificial workarounds**: User manually bumping priority feels wrong - "I don't want to pick a particular ingredient and artificially bump it in priority just to make it happen that week"
3. **Model gap**: Five types of dried beans - want system to work them in naturally with higher-priority ingredients

## Current Workaround

User creates criteria around specific ingredients (e.g., "use dried beans") or manually bumps priority. Neither feels natural.

## Solution Direction

Want pantry items **paired with high-priority ingredients** rather than artificially bumped. The system should recognize:
- This ingredient won't spoil soon (low priority by freshness)
- User wants it worked in (high priority by user preference)
- Should be paired with actual high-priority CSA items

## Potential Approaches

1. **Separate priority dimension**: Freshness vs. "want to use"
2. **Criteria enhancement**: Better support for "work in pantry items" as criterion type
3. **Pairing logic**: When generating pitches, look for opportunities to combine low-priority pantry with high-priority CSA
4. **User preference**: Explicit "work these in" flag separate from priority

## Notes

User assessment: "Lower lift" compared to recipe editing - likely because it's more of a logic/prompt change than new UI capability.

Key insight: Time-to-spoil model is correct for CSA produce but incomplete for overall ingredient utilization.
