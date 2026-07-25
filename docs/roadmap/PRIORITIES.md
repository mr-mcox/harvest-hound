# Current Priorities

**Updated**: 2026-07-25
**Status**: Post-MVP. Current phase: **Recipe Memory & Trust** — read `phase-recipe-memory.md` first.

## Now

- `pain-import-priority-adjustment` - Adjust LLM-inferred priorities in the parse-results
  view before commit. Standalone (no domain change), user's top pick.

## Next

- `pain-saved-recipes` - Durable recipes v1: favorite + resurface. First pressure test of
  the phase spine (recipes as durable memory with provenance).
- `pain-pitch-time-mismatch` - Pitch fidelity v1. Independent of the spine; can run
  before/parallel.

## Next (after spine v1 exists)

- `pain-recipe-editing` - Third spine strand: *edits* fold into durable memory (final
  product, no changelog); *asking* half is independent and can ship anytime.
- `pain-recipe-feedback` - Attention layer: rating + cooked-recency rerank resurfacing;
  time actuals feed pitch fidelity.

## Later

- `pain-recipe-clipping` - URL clip → corpus. Extends the spine; sequence after saved-recipes.
- `pain-repetitive-pitches` - Re-evaluate once a corpus exists; may partially fall out of spine work.
- `pain-recipe-formatting` - Carried from December 2025 queue.

## Strategy

**Phase spine**: recipes become durable, first-class, *living* objects with provenance and
attention metadata. Saved, clipped, and edited recipes are incremental realizations of one
concept; rating/recency govern how memory resurfaces. Trust (pitch fidelity) and
review-at-inference are independent tracks. See `phase-recipe-memory.md` for insights,
approach commitments, and superseded scope decisions.
