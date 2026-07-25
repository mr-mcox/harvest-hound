# Can't Adjust Priority During Bulk Import

**Status**: Now (user's top pick — standalone, no domain change)
**Impact**: High friction at the highest-frequency entry point (weekly CSA paste)
**Discovered**: 2026-07 pain analysis (production use)
**Related**: `phase-recipe-memory.md` Insight 3, `learnings/ux.md`

## The Pain

User pastes a CSA delivery list; `ExtractIngredients` infers priorities from perishability.
Mostly right — but adjusting the misses requires navigating to `/inventory` and hunting
each item in a priority-sorted list that *re-sorts on change* (documented UX break:
`learnings/ux.md`, "Cycling badge UX in long sorted list").

The parse-results view — where every inference is visible and nothing is committed yet —
is read-only.

## The Pattern (not just a feature)

"LLM suggests, human adjusts" is a validated pattern (`learnings/ux.md`). This pain is
that pattern missing at its highest-leverage moment: **review at the point of inference,
before commit**. Build the import fix as the first instance of the pattern; the next
instances are already visible in learnings (`purchase_likelihood` grey-area items,
pantry-staple guesses).

## Current Flow

1. `/inventory/import` → paste free text → parse (`ExtractIngredients` BAML call)
2. Results shown with parsed quantities, units, priorities — read-only
3. "Add All" → bulk insert
