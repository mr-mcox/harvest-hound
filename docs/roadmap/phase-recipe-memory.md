# Phase: Recipe Memory & Trust

**Status**: Insight handoff, aligned 2026-07-25. No agent briefs written yet.

## How to use this doc

This is the entry point for framing next-phase work. It carries **insights and named
concepts, deliberately not solutions**. Per-feature solution selection happens in the
coding workflow's problem-space/solution-space phases (pi-platform `coding-workflow` +
`agent-brief` skills), reading this doc plus the relevant `pain-*.md`. If a mechanism
seems implied here, treat it as one candidate, not a decision.

When briefing one pain, read the **Tensions** section below and carry the tensions that
touch it into the brief's constraints and escalation triggers — that is how neighboring
pains stay felt while working one at a time.

## Where we are

MVP complete: the loop (CSA → inventory → pitches → flesh out → shop → cook) validated over
three weeks of production use ("only rutabaga left"). Seven active pains remain, and they
are not seven features — they reduce to two missing concepts (durable memory, pitch
fidelity) and one missing interaction pattern (review at the point of inference).

**Cost posture**: multi-step generation is acceptable; single-call cheapness is not a
requirement. See Insight 5 before designing pipelines.

## The insights

### 1. Recipes are the system's missing memory — the spine of this phase

The system remembers nothing beyond the week except inventory and config. It forgets what
it pitched (`pain-repetitive-pitches`), forgets what worked (`pain-saved-recipes`), and
cannot hold what the user clips (`pain-recipe-clipping`). Three pains, one concept:
**recipes as durable, first-class objects with provenance**.

The deep model was already discovered and validated, but never built:

- "Recipe = aggregate root (canonical, reusable, long-lived)" — `learnings/domain.md`
  (pitch-recipe-identity experiment)
- "Can add canonical recipe library without breaking current model" — `learnings/domain.md`
  (recipe-context-sources pressure test): ingredient-source assignment is planning-time
  context, so recipes are reusable across inventory states.

**Provenance is an attribute, not three subsystems.** A recipe generated this week, kept
from last month, or clipped from Milk Street is the same aggregate with a different origin.
The old POINTER/GENERATIVE split dissolves: pitches reference recipes; some recipes simply
existed before the session. Favorites and clipping become two entry points into one concept;
variety becomes a query over history rather than only a prompt tweak.

### 2. A pitch is a promise; trust is the product

The validated value prop is "variety + confidence" — confidence *is* trusting the pitch
card. `pain-pitch-time-mismatch` ("45 minutes active prep was a dirty rotten lie") is one
dimension of the three already-validated identity boundaries: ingredients, effort, family
expectations (`learnings/domain.md`, "Recipe identity boundaries" and "bidirectional
promise-keeping"). The concept is **pitch fidelity**: the pitch's promises must survive
flesh-out on all three dimensions. It stays stable whether the mechanism is constraint
threading, a judge step, or both — and enforcing only the time dimension first doesn't
make the concept time-shaped.

### 3. Review at the point of inference is a pattern, not an import feature

"LLM suggests, human adjusts" is validated (`learnings/ux.md`). `pain-import-priority-adjustment`
is that pattern missing at its highest-leverage moment: the parse-results view, where every
inference is visible and nothing is committed. Framed as a pattern, it also covers the next
instances already visible in learnings: `purchase_likelihood` grey-area items and
pantry-staple guesses ("pantry guesses not as accurate as expected"). Build the import fix
as the first instance and later ones get cheaper.

### 4. Durable recipes are living documents, and attention is part of memory

Real cooking mutates recipes — substitutions, accidents, adjustments. "Chat with recipe"
is two distinct interactions:

- **Editing** (mutation): "swap sour cream for the creme fraiche." Changes the recipe.
- **Asking** (conversation): "will rice wine work instead of white wine here?" Changes
  nothing — it's context-aware guidance against the recipe.

Only mutation touches memory, and **the corpus stores the final product, not the edit
transcript** (decided — no changelog of edits). The recipe you keep is the recipe as you
actually cook it. This is what makes editing a spine strand rather than a standalone
feature: an edit to an ephemeral recipe is a convenience; an edit that folds into durable
memory is the corpus staying true.

The second half: **remembering is ranking, not just storing.** The corpus takes inputs
from multiple entry points (kept, clipped, edited), and resurfacing selects from it by a
blend of legible signals — alignment (match with available inventory), attention (rating,
how recently cooked), novelty (recently clipped, never cooked), coverage (does it use what
wants using). Time-actuals captured at the same feedback moment feed pitch fidelity
(Insight 2's trust loop).

**Retrieval serves generation, not a results page.** Resurfacing decides which recipes
enter the generation prompt, so ranking is context curation under
performance = (correctness² × completeness) / size: an irrelevant recipe in the prompt is
a distractor — worse than absence, because it spends attention *and* invites bad riffs.
And a planning session is assembled as a **slate, not a ranked list**: the success
criteria (priority coverage, variety) are properties of the week's set of recipes, and
the candidate pool shifts as claims land. Item-level scoring alone can't express that.

### 5. Name seams, not pipelines

The pains demand two *capabilities*: generation can **consult durable memory** before it
starts, and results can be **checked against promises** before they're shown. Whether that
becomes a multi-phase pipeline or two small seams in the current flow should be forced by
concrete needs, not committed upfront. Name the seams — **candidate sourcing** and
**fidelity check** — with today's behavior as the only implementation. If a corpus and a
judge both materialize, a pipeline shape emerges; if prompting suffices for variety, no
unused phases were built.

## Approach commitments (supple design)

1. **Name concepts by domain intent** (provenance, pitch fidelity, candidate sourcing) —
   never by mechanism (pipeline phase, critic, corpus table).
2. **Each feature is the smallest realization of its concept** — e.g., favorites v1 is
   "keep this recipe past the session; surface it when inventory aligns," nothing more.
3. **Let extensions prove the spine** — clipping and variety must arrive as extensions of
   durable recipes, not as new systems. If they can't, the spine is wrong; revisit it.
4. **Don't restructure generation until two concrete capabilities force it.**

## Tensions to Keep in View

One pain is worked at a time, but each solution must feel the pull of its neighbors —
these are the standing cross-constraints. Briefs carry the relevant ones as constraints
and escalation triggers.

- **Editing ↔ Memory**: every edit path must leave a recipe clean enough to resurface.
  The final-product rule means no delta storage, no annotation layer the corpus can't read.
- **Fidelity ↔ Resurfacing**: promise-keeping applies to corpus-sourced pitches too. A
  resurfaced favorite adapted to this week's inventory carries *stronger* expectations
  than a novel pitch ("that's not the mac and cheese we remember").
- **Saved ↔ Clipped (provenance)**: whatever marks a kept recipe must not assume recipes
  originate in planning sessions — clipped recipes arrive with an external source and no
  session. A bare `is_favorite` boolean fights the next strand.
- **Attention ↔ Novelty (cold start)**: ranking by rating and cooked-recency must not
  bury never-cooked clipped recipes; their signal is novelty, not history.
- **Review pattern ↔ its next instances**: the import-priority review UI is the first
  instance of review-at-point-of-inference; purchase-likelihood and pantry-guess review
  should be able to reuse it without rework.
- **Slate ↔ item quality**: variety and priority coverage are set-level properties of the
  week; nothing built for a single pain should assume recipes are judged one at a time.
- **Candidate sourcing ↔ inventory priorities**: corpus matches join generation as another
  candidate source and must serve inventory priorities, not bypass them — a resurfaced
  favorite that ignores the urgent produce defeats the core loop.

## Suggested ordering

1. `pain-import-priority-adjustment` — standalone (pure interaction pattern, no domain
   change), user's top pick, quick win.
2. `pain-saved-recipes` (durable recipes v1: favorite + resurface) — first pressure test
   of the spine.
3. `pain-pitch-time-mismatch` (pitch fidelity v1) — independent of the spine, can go
   before/parallel to 2.
4. `pain-recipe-editing` — third spine strand. Sequence the *mutation* half after durable
   recipes v1 so edits have somewhere durable to land; the *asking* half (conversation,
   no persistence) can ship anytime. Unpack piece by piece.
5. `pain-recipe-feedback` — attention layer (rating + cooked-recency reranking, time
   actuals). Naturally follows saved-recipes v1: capture at the existing "cooked"
   transition, consume during resurfacing.
6. `pain-recipe-clipping` — extends the spine (new entry point: URL → canonical recipe).
7. `pain-repetitive-pitches` — re-evaluate once a corpus exists; may partially fall out of
   spine work. Deferred by user as prompt-tunable until then.

**Also queued**: `pain-recipe-formatting`.

## Scope Notes

- Saved and clipped recipes (the recipe library) are **in scope** — they are the spine.
- Generation cost: multi-step generation is acceptable; "cheap to generate" is not a
  constraint.
- Older learnings entries that no longer bind are annotated SUPERSEDED/REFINED in place —
  trust the annotation over the original entry.

## Grounding facts for implementers (verified 2026-07-25)

- `Recipe.session_id` is already **nullable** (`src/backend/models.py`, Recipe class) — the
  model can hold a session-less recipe today. There is no `is_favorite`, no provenance/
  `recipe_type` field, and no surfacing mechanism.
- `FleshOutRecipe()` (`src/backend/baml_src/recipes.baml`) receives pitch name, blurb, and
  ingredients — **not** the pitch's `active_time_minutes`, though `RecipePitch` has it.
- `Pitch` rows link to their fleshed-out `recipe_id`; pitches are session-scoped and
  disposable (correct per "pitch as projection").
- Pitch generation is stateless across sessions; diversity guidance in
  `GenerateRecipePitches` is technique-focused only.

## Open questions (genuinely open — resolve during framing, with the user)

- Candidate selection mechanism: retrieval's *purpose* is settled (curate the generation
  prompt). Open: does code score candidates numerically, or does the LLM prune a
  signal-annotated corpus? What's the candidate budget per session?
- Direct matches: when the corpus contains a strong as-is match ("you can make that Milk
  Street dish"), does it present alongside generated pitches without adaptation?
- Minimal provenance: an origin enum? source URL? Is "kept" distinct from "cooked and rated"?
- Fidelity: constrain generation, judge after, or both? (Round-trip fidelity experiment in
  `learnings/technical.md` showed effort fidelity 85% — judge dimensions already known.)
- Parametric favorites ("mac and cheese + [CSA vegetable]") — explicitly later; don't design
  for it now, but don't preclude slot-like extension of durable recipes.
- Rating model: scale vs. "would make again" flag vs. free-text notes — and which of these
  the rerank function actually consumes (decided: recency-of-cooked and rating are the
  first-class attention signals).
- Where does editing happen — during cooking (the documented moments are mid-cook), during
  planning, or both? Does the shopping list re-sync on edit (December pain doc says yes)?
- Does the *asking* interaction need any persistence at all, or is it purely ephemeral
  conversation against the recipe?
