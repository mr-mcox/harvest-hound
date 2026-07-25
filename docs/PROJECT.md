# Project Reference

Standing constraints and validated bets, independent of any phase. Current phase strategy:
`roadmap/phase-*.md`. Current focus: `roadmap/PRIORITIES.md`.

## What This Is

Agentic meal planning for one household's CSA deliveries. Hobby scale, single user, one
production database. The corpus this system reasons over is small (tens of recipes, dozens
of inventory items) — design for legibility and iteration speed, never for scale.

## Optimization Priority

1. **Fast iteration** — changes land in under ~30 minutes of work
2. **Evolvability** — no change should have a 700-LoC blast radius

## Quality Bar

"Would show a colleague": clean enough to not be embarrassed, tests pass, reasonable
structure. Accepted debt: happy-path error handling, light test coverage (integration bugs
occasionally reach production — annoying but acceptable), Skeleton styling defaults.

## Anti-Goals

- Multi-user support
- Perfect error handling / comprehensive API tests
- Character/tone preservation in recipe generation (functional fidelity is what matters)
- Mobile-first design (quick phone entry may matter someday; not a driver now)

## Stack

| Layer | Choice |
|-------|--------|
| Backend | FastAPI + SQLModel + SQLite (Alembic migrations) |
| LLM | BAML for all LLM interactions — structured, testable, iterable |
| Frontend | Svelte + Skeleton v3, component-based page organization |
| Testing | Domain-first: test claiming/lifecycle logic; endpoint tests only where breakage emerges |

## Core Architectural Principles

Full discovery context in `learnings/`; these are the load-bearing rules:

- **LLM declares, code manages.** The LLM outputs culinary content and what it used; code
  owns state, claiming, and accounting. Never make the LLM do bookkeeping.
- **Recipe is the aggregate root** — long-lived and reusable. Pitches are session-scoped
  projections of recipes, disposable by design.
- **Ingredient-source assignment is planning-time context**, not a stored property of the
  recipe. Recipes remain valid across inventory states.
- **Three-tier ingredient sources**: Inventory (itemized, claimed) / Pantry Staples
  (unlimited, never claimed) / Grocery (multiple stores, list-building).
- **Every recipe ingredient is claimed against a source** — that's what makes shopping
  lists and pantry verification complete.
- **Household profile and pantry are prompt constants** (singleton config), not modeled
  entities.
- **Prompt-context curation follows performance = (correctness² × completeness) / size.**
  What enters a generation prompt is selected, not dumped: irrelevant context is a
  distractor, worse than absence.

## Red Flags (stop and reconsider)

- Adding abstraction layers for unproven needs
- Building a mechanism where the concept hasn't been named (see phase doc's naming commitments)
- Scale reflexes: indexes, embedding stores, tuned rankers, batch pipelines — the data
  fits in a prompt
- Worrying about edge cases before the happy path works

## Database Safety

- `harvest.db` = live user data — never modify directly; `./run` uses it (user only)
- `dev.db` = development default; `./dev` uses it
