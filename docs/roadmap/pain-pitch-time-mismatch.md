# Pitch-to-Recipe Time Mismatch

**Status**: Next (phase: Recipe Memory & Trust — pitch fidelity concept)
**Impact**: High - Breaks trust in pitch cards, the basis of meal selection
**Discovered**: 2026-07 pain analysis (production use)
**Related**: `phase-recipe-memory.md` Insight 2, `pain-recipe-feedback.md`

## The Pain

User says "I want a quick weeknight meal." Pitch card claims 20 minutes. User selects it
and fleshes out the recipe — which says 60 minutes active, or "simmer for 1 hour."

### User Quote

> "Thai curry tasted great but 45 minutes active prep was a dirty rotten lie."
> (`learnings/workflows.md`, "Recipe metadata unreliable")

## Why It Matters

The validated value proposition is variety + **confidence** — confidence is trusting the
pitch card. Effort mismatch is one of the three recipe-identity boundaries already
validated in `learnings/domain.md` ("Recipe identity boundaries", "bidirectional
promise-keeping"): ingredients, effort, family expectations.

## The Concept (not a solution)

**Pitch fidelity**: the pitch's promises must survive flesh-out, on all three identity
dimensions. Time is the first dimension to enforce, not the definition of the concept.

## Distinct From

General LLM time-estimation inaccuracy (`pain-recipe-feedback.md` — capturing actuals,
ratings). This pain is the *pitch promise not being enforced* during flesh-out: the pitch
sets expectations the flesh-out is currently free to ignore.

## Grounding Fact

`FleshOutRecipe()` in `src/backend/baml_src/recipes.baml` does not receive the pitch's
`active_time_minutes`, though `RecipePitch` has it. Threading it through is a likely
ingredient of any fix, but the framing decision (constrain generation vs. judge after vs.
both) is open — see `phase-recipe-memory.md` open questions.
