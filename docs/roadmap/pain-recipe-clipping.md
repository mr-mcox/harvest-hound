# Milk Street / Cooks Illustrated Not Woven In (Recipe Clipping)

**Status**: Later (phase: Recipe Memory & Trust — extends the durable-recipe spine)
**Impact**: Medium - Subscriptions the user pays for don't feed the system
**Discovered**: 2026-07 pain analysis (production use)
**Related**: `phase-recipe-memory.md` Insight 1, `pain-saved-recipes.md`

## The Pain

User subscribes to Milk Street and Cooks Illustrated and wants to clip recipes ("this
looks interesting, I'd like to try it someday") and have them surface when ingredient
availability aligns.

**User's intent**: Not "make this exact recipe this week" — "I've clipped things I want
to try; surface them when the stars align."

## Why It Matters

Same concept as saved recipes: durable recipes with provenance. A clipped recipe is the
same aggregate as a kept favorite, with origin "clipped from URL" instead of "generated
and kept." Architectural support already validated: recipes store ingredients without
source assignments; source resolution happens at planning time (`learnings/domain.md`,
"Recipes exist independently of ingredient source assignments").

## Sequencing

Must arrive as an *extension* of the durable-recipe spine (`pain-saved-recipes.md` goes
first as its pressure test), not as a parallel system. If clipping can't be expressed as
"new entry point into the same corpus," the spine model is wrong — surface that rather
than working around it.
