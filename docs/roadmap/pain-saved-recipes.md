# Saved Recipes / "Greatest Hits"

**Status**: Next (phase: Recipe Memory & Trust — first pressure test of the durable-recipe
spine, see `phase-recipe-memory.md`)
**Impact**: Medium - Repeat successful dishes
**Discovered**: 2025-12-21 (Week 3 production use)
**Related**: `phase-recipe-memory.md` Insight 1, `pain-recipe-clipping.md`, `pain-recipe-feedback.md`

## The Pain

User wants to revisit recipes that were particularly successful, but currently no way to save or recall past favorites.

### User Quote

> "I'd still like to work in saved recipes and revisiting things that I've made in the past that have been a hit."

## Why It Matters

1. **Recipe repertoire**: Build up a collection of proven winners
2. **Ingredient utilization**: Saved recipes could be pitched when ingredients align
3. **User satisfaction**: Reduce variance by including known successful dishes

## Solution Direction

Mechanism to:
- Save/favorite recipes from past sessions
- Surface saved recipes during pitch generation (when ingredients match)
- Browse saved recipe library

## Relationship to Recipe Feedback

Overlaps with `pain-recipe-feedback` - recipes marked highly in feedback are natural candidates for saving/"greatest hits" status.

Could be implemented together:
- Feedback identifies hits
- Saved recipes preserves them
- Pitch generation surfaces them when appropriate
