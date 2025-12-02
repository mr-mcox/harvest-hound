# Harvest Hound MVP Charter

**Status**: Living document - update as we learn, delete when MVP complete
**Created**: 2025-12-02
**Last Updated**: 2025-12-02

---

## 1. Domain Boundaries Discovered

### Core Entities

| Entity | Role | Notes |
|--------|------|-------|
| **Recipe** | Aggregate root | Reusable, long-lived. Ingredients WITHOUT store assignments. |
| **Pitch** | Projection of Recipe | Ephemeral, session-scoped. Not a separate entity. |
| **IngredientClaim** | Reservation | Links recipe → inventory. States: reserved → consumed/released. |
| **Inventory Item** | Tracked ingredient | Has: quantity, location, priority, optional portioning hint. |
| **Household Profile** | Prompt constant | Baked into LLM prompts. NOT a database entity. |

### Key Boundaries

- **Recipe ≠ Store Assignment**: Store resolution at planning time, not storage. Recipes are reusable across inventory states.
- **LLM declares, code manages**: LLM outputs what it used; code handles state/claiming. Don't make LLM do accounting.
- **Three-tier stores**: Explicit (itemized, claimed) → Pantry (unlimited, unclaimed) → Grocery (list-building)

### Modeling Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Portioning hints | Optional field on ingredient | Prevents "stuck with 1/2 lb chorizo" - defrost increments matter |
| Ingredient prep | Strip from ingredient, enforce in instructions | Prep surprises mid-cook are painful; instructions should be complete |
| Likelihood-based sourcing | Nice-to-have | Look for seams; solves "key ingredient buried in pantry assumptions" |

### Simpler Than Expected
- Household profile as prompt constant (no DB/UI)
- Store auto-selection (no per-generation UI needed)
- Single-page UI goes surprisingly far

### More Complex Than Expected
- Ingredient claiming is CRITICAL for multi-wave generation
- Recipe identity validation needed (pivots can break pitch promises)
- Multiple grocery stores, not singleton ("Costco run this week")
- Planning sessions with grouped criteria (not flat pitch pool)

## 2. Top Features for MVP

### Steel Thread Approach

Prove the loop first, polish second. The thread: **CSA delivery → planning session with constraints → shopping list → cook**

### Phase 1: Steel Thread

| Step | What to Build | OK to Be Ugly |
|------|---------------|---------------|
| Inventory entry | Bulk paste → parsed list with qty/location/priority | Simple list view, no filtering |
| Planning session | Create session → add criteria → generate grouped pitches | Free-form constraint text |
| Pitch generation | 3x pitches per criterion, adaptive to unfilled slots | Basic cards, no invalidation UI |
| Select + Flesh out | Sequential claiming, quantity-aware, identity validation | No claim visibility UI |
| Shopping list | Aggregate claims by store, copy button | No essential/optional split |
| Lifecycle | Cook (consume claims) / Abandon (release claims) | No history view |

### Phase 2: Fidelity Pass (After Loop Works)

- Inventory: Table view, location filtering, portioning hint display
- Claims: Visibility UI ("why no radish recipes?")
- Pitches: Invalidation/removal when ingredients claimed
- Shopping: Essential vs optional, likelihood ordering
- General UI polish

### New Entities for MVP

| Entity | Role |
|--------|------|
| **Session** | Named planning container ("Week of Dec 2") |
| **MealCriterion** | Constraint within session ("GF/DF leftovers", slots: 1) |

Relationships: Session → MealCriteria → Pitches → Recipe (with criterion remembered)

### Explicitly OUT of Scope

- Per-generation store selection
- Bulk recipe operations
- POINTER pitches (clipped/saved recipes)
- Recipe editing after planning (abandon + regenerate is workaround)

### Never Doing

- Character/tone preservation in recipe fidelity (functional fidelity is what matters)

## 3. Architectural Bets

### Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Backend | FastAPI + SQLModel + SQLite | Familiar, sufficient, fast iteration |
| LLM | BAML | Structured outputs, type safety, prompt iteration |
| Frontend | Svelte + Skeleton v3 | Reactive state for sessions, nice UI without thinking |
| Testing | Domain-first TDD | Test claiming/lifecycle logic; add endpoint tests if breakage emerges |

### Patterns to Keep (Validated)

- **BAML for all LLM interactions** - structured, testable, iterable
- **Household profile as prompt constant** - no DB/UI complexity
- **LLM declares, code manages state** - critical separation
- **SSE streaming for generation** - better UX than waiting
- **Technique diversity in prompts** - multiple options for same ingredient
- **Three-tier store architecture** - clean claiming logic

### Patterns to Change

| From (Prototype) | To (MVP) |
|------------------|----------|
| Single `app.py` | `models.py`, `routes.py`, `baml_functions.py` |
| `ingredients_json` blobs | Proper relational model |
| Vanilla JS | Svelte + Skeleton |
| Sync BAML | Async throughout |
| No tests | Domain TDD |

### Acceptable Technical Debt

- **Error handling**: Minimal, happy-path focus
- **Migrations**: Blow away DB during steel thread; add migrations post-steel-thread for authentic use
- **API naming**: Refine later
- **Styling**: Skeleton defaults, don't overthink

### Optimization Priority

1. **Fast iteration** (changes in < 30 min)
2. **Evolvability** (no 700 LoC blast radius)

### Anti-Goals

- Perfect error handling
- Comprehensive API tests
- Mobile responsiveness
- Multi-user support

## 4. Success Criteria

### Functionally Done When

"I can paste a CSA list, create a planning session with dietary constraints, get pitches grouped by meal type, select and flesh out recipes, generate a shopping list, and mark things cooked/abandoned - all without workarounds or manual tracking."

### Steel Thread Complete When

Used for **one actual week** of meal planning:
- CSA arrived → inventory entered
- Planning session created with constraints
- Meals planned from pitches
- Went shopping from generated list
- Cooked at least 3 recipes through the system

### Code Quality Bar

**"Would show a colleague"**: Clean enough to not be embarrassed, tests pass, reasonable structure.

### Scope Boundaries

| Category | Items |
|----------|-------|
| **Out for MVP** | Mobile, recipe library, multi-user, perfect errors |
| **Possible post-MVP** | Mobile responsiveness (quick entry, recipe on phone), recipe library (anticipated need) |
| **Not foreseeable** | Multi-user support, perfect error handling, character preservation |

### Red Flags (Stop and Reconsider If...)

- Adding abstraction layers "for later"
- Building features not in steel thread
- Spending > 30 min on a change
- Worrying about edge cases before happy path works

