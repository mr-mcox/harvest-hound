# Repetitive Pitches (Taco-Adjacent Drift)

**Status**: Later (phase: Recipe Memory & Trust — re-evaluate once recipe corpus exists)
**Impact**: Medium - Erodes the "variety" half of the value proposition
**Discovered**: 2026-07 pain analysis (production use)
**Related**: `phase-recipe-memory.md` Insight 1, `pain-saved-recipes.md`, `pain-recipe-clipping.md`

## The Pain

Week after week, pitches gravitate toward similar formats — tacos, enchiladas, tostadas,
burrito bowls. Mexican/Tex-Mex overwhelms other cuisines.

## Why It Happens

Pitch generation is stateless across sessions — the system has no memory of what it
pitched last week. Diversity guidance in `GenerateRecipePitches` is technique-focused
(a deliberate prior fix — see `learnings/technical.md`, "Technique diversity over
ingredient diversity"), not cuisine- or format-aware across sessions.

## Deferral Rationale

User confirmed this is likely prompt-tunable and is ok deferring until a recipe corpus
exists (`pain-saved-recipes.md`, `pain-recipe-clipping.md`). A corpus naturally injects
variety; cross-session pitch history becomes *queryable* once recipes are durable. Framing
this before the spine exists risks building a bespoke variety mechanism the corpus would
obsolete.
