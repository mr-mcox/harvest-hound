# Feature Frame: Pitch Selection → Flesh Out → Ingredient Claiming

**Date**: 2025-12-07
**Status**: Draft - Awaiting Alignment

---

## Problem Statement

Users need to select promising pitches, flesh them out into complete recipes, and have ingredients automatically claimed to prevent double-booking in subsequent generation waves. The current implementation generates and displays pitches but has no selection or claiming mechanism, making iterative multi-wave generation impossible.

**From Prototype Discovery**:
- Two-phase recipe browsing validated: pitches → selection → flesh out (LEARNINGS.md:263-268)
- Ingredient claiming is CRITICAL for multi-wave generation (LEARNINGS.md:40-44)
- Fleshing out is the right moment to claim ingredients, not pitch selection (LEARNINGS.md:49)
- Complete ingredient claiming required - EVERY ingredient assigned to source (LEARNINGS.md:202-208)

---

## User Stories

### Story 1: Select Multiple Pitches for Flesh Out
**As a** meal planner
**I want** to select multiple recipe pitches before fleshing them out
**So that** I can review my choices and change my mind without wasting expensive LLM calls

**Acceptance Criteria**:
- [ ] User can click/tap pitch cards to mark them as selected (visual indicator)
- [ ] User can deselect pitches before fleshing out
- [ ] Selected pitches persist during page session (no accidental loss)
- [ ] UI shows count of selected pitches (e.g., "3 selected")
- [ ] "Flesh Out Selected" button visible when 1+ pitches selected
- [ ] Button disabled when no pitches selected

**From LEARNINGS.md**: User wants to "think about what I like and change my mind" before expensive LLM operations (user feedback on batch selection)

### Story 2: Flesh Out Selected Pitches Into Complete Recipes
**As a** meal planner
**I want** to convert selected pitches into full recipes with complete instructions
**So that** I can cook from them and have all the details I need

**Acceptance Criteria**:
- [ ] User clicks "Flesh Out Selected" to start batch generation
- [ ] System generates complete recipe for each selected pitch via BAML
- [ ] Recipes saved to database with all required fields (name, ingredients, instructions, times, servings)
- [ ] Progress indicator shown during generation (SSE streaming or status updates)
- [ ] Generated recipes associated with originating criterion and session
- [ ] Fleshed-out recipes removed from pitch pool (no longer selectable)
- [ ] Recipe state initialized as "planned" (lifecycle ready)

**From LEARNINGS.md**:
- Pitch → full recipe fidelity "in the ballpark" is good enough (line 385-388)
- Recipe lifecycle states validated: planned → cooked/abandoned (line 88-93)

### Story 3: Claim Ingredients From Inventory with Quantity Tracking
**As a** meal planner
**I want** ingredients automatically claimed when recipes are fleshed out
**So that** future generations don't double-book ingredients I've already allocated

**Acceptance Criteria**:
- [ ] When recipe fleshed out, system creates IngredientClaim records for inventory items
- [ ] Claims track: ingredient name, quantity, unit, recipe association
- [ ] Claims are "reserved" state initially (not yet consumed)
- [ ] Only ingredients matching inventory items are claimed (Pantry Staples not claimed)
- [ ] Claimed quantities accurate (match recipe requirements)
- [ ] Claim creation happens transparently (no user interaction needed)
- [ ] Claim creation is atomic (all claims for a recipe succeed or fail together)

**From LEARNINGS.md**:
- Quantity-aware claiming works smoothly, no edge cases found (line 74-80)
- IngredientClaim works invisibly in background (line 95-100)
- Only claim trackable inventory, not Pantry Staples (line 61-65)

### Story 4: Assign Grocery Claims with Purchase Likelihood
**As a** meal planner
**I want** non-inventory ingredients assigned to grocery sources with likelihood scores
**So that** I can see what I probably need to buy, force-ranked by confidence

**Acceptance Criteria**:
- [ ] LLM assigns EVERY ingredient to an ingredient source (Inventory, Pantry Staples, or Grocery)
- [ ] For non-inventory ingredients, LLM provides purchase likelihood (0.0-1.0 numeric score)
- [ ] High likelihood (>0.7): Definitely need to buy (e.g., "8 oz goat cheese")
- [ ] Medium likelihood (0.3-0.7): Review/verify (grey area items)
- [ ] Low likelihood (<0.3): Likely Pantry Staples (e.g., "2 tsp salt")
- [ ] Claims store likelihood score for shopping list ordering
- [ ] Grocery claims saved to database with ingredient source reference

**From LEARNINGS.md**:
- Complete ingredient claiming critical - every ingredient assigned (line 202-208)
- Likelihood-based sourcing replaces binary Grocery/Pantry split (line 233-240)
- Three-tier ingredient source architecture validated (line 225-231)

### Story 5: Generate More Pitches Respecting Claims
**As a** meal planner
**I want** to generate additional pitches after selecting some recipes
**So that** I can iteratively fill my weekly meal plan with diverse options

**Acceptance Criteria**:
- [ ] "Generate More" button available after initial pitch generation
- [ ] System calculates unfilled slots per criterion (slots - fleshed-out recipes)
- [ ] Generates 3x unfilled slots pitches per criterion (same as initial sizing)
- [ ] Decremented inventory state passed to BAML (original - claimed quantities)
- [ ] Claimed ingredients list passed to BAML for pivot logic
- [ ] New pitches avoid claimed ingredients (auto-pivot to remaining inventory)
- [ ] Progress feedback during generation (SSE streaming)
- [ ] Generated pitches saved and displayed grouped by criterion

**From LEARNINGS.md**:
- Multi-wave generation essential for iterative workflow (line 271-274)
- Wave sizing: 3x unfilled slots validated (line 282)
- Auto-pivot with claimed ingredients works well (line 391-396)
- Sequential generation prevents conflicts (line 50-51)

---

## Prototype Contrast

| Aspect | Prototype | MVP | Why Change |
|--------|-----------|-----|------------|
| **Selection** | Pitch cards display-only | Multi-select with flesh-out action | Enable batch decision-making before expensive LLM calls |
| **Recipe entity** | `ingredients_json` blob | Structured ingredients with preparation field | Enables claiming logic + flexible rendering (LEARNINGS.md:335-341) |
| **Claiming** | Manual inventory decrement | Automatic IngredientClaim creation | LLM declares, code manages state (MVP-CHARTER.md:24) |
| **Ingredient sources** | Simple store assignment | Three-tier with likelihood scoring | Enables smart shopping list (LEARNINGS.md:233-240) |
| **Multi-wave** | Broken (double-books ingredients) | Claim-aware generation | Critical for iterative planning (LEARNINGS.md:40-44) |

**Preserve from Prototype**:
- SSE streaming for generation progress
- BAML sequential generation (one recipe at a time)
- Recipe lifecycle states (planned/cooked/abandoned)
- Household profile + pantry staples + inventory context to LLM

**Fix from Prototype**:
- Add Recipe entity with structured ingredient schema
- Add IngredientClaim entity with state tracking
- Implement claim-aware inventory state for multi-wave generation
- Separate ingredient preparation from shopping (prep leak bug)

**Change from Prototype**:
- Batch selection (not immediate flesh-out on click)
- Structured ingredients (not JSON blob)
- Likelihood-based sourcing (not binary Grocery/Pantry)

---

## Recipe Schema Design

### Structured Ingredients (balance structure + flexibility)

```python
class RecipeIngredient:
    quantity: str          # "0.25", "1-2", "to taste" - string for flexibility
    unit: str             # "cup", "tablespoon", "pound", "" (for count)
    name: str             # "napa cabbage kimchi"
    preparation: str | None  # "minced", "diced", "at room temperature"
    notes: str | None     # "see Tip", "such as Chardonnay"
```

**Rationale**:
- **Structured**: Enables claiming logic, ingredient querying, reliable LLM transformations
- **Flexible**: Quantity as string handles ranges, "to taste", approximations
- **Separation**: Preparation field solves shopping list prep leak (LEARNINGS.md:335-341)
- **Rendering**: LLM can transform into Joy of Cooking inline style, sous chef prep lists, etc.

### Recipe Fields

```python
class Recipe(SQLModel, table=True):
    id: UUID
    session_id: UUID              # Links to planning session
    criterion_id: UUID            # Originating meal criterion
    name: str
    description: str              # Long-form story/context (like CookBook)
    ingredients: list[dict]       # JSON list of RecipeIngredient dicts
    instructions: list[str]       # Step-by-step directions
    active_time_minutes: int
    passive_time_minutes: int
    servings: int
    state: str                    # "planned", "cooked", "abandoned"
    notes: str                    # User-added notes
    created_at: datetime
    planned_at: datetime
    cooked_at: datetime | None
```

**Inspiration**: CookBook YAML exports (`.scratch/CookBook-Recipes-YAML-20251202T0829579140600/`)
- Times as integers (minutes) not ISO durations (simpler for MVP)
- Description field for LLM-generated recipe stories
- Instructions as list of strings (don't over-structure)

### IngredientClaim Schema

```python
class IngredientClaim(SQLModel, table=True):
    id: UUID
    recipe_id: UUID                    # FK to Recipe
    ingredient_name: str
    quantity: float
    unit: str
    ingredient_source_type: str        # "inventory", "pantry", "grocery"
    ingredient_source_id: int | None   # FK to GroceryStore or InventoryItem (if applicable)
    purchase_likelihood: float | None  # 0.0-1.0 for grocery items, None for inventory/pantry
    state: str                         # "reserved", "consumed"
    created_at: datetime
```

**Design notes**:
- Tracks all ingredients (not just inventory) for complete shopping list
- Purchase likelihood enables force-ranked grocery list
- State tracking enables cook/abandon lifecycle
- ingredient_source_id allows lookup of specific inventory item or grocery store

---

## Out of Scope (Deferred)

Explicitly NOT part of this feature:

- **Optional ingredient marking**: Separate essential vs nice-to-have claims (deferred per user request)
- **Pitch invalidation UI**: Graying out/removing pitches when ingredients exhausted (deferred to fidelity pass per MVP-CHARTER.md:68)
- **Claims visibility UI**: Showing which ingredients are claimed in main interface (deferred - "trust in background")
- **Recipe editing after planning**: Modify ingredients/instructions in saved recipes (abandon + regenerate is workaround)
- **Cook/Abandon actions**: Lifecycle transitions from planned state (deferred to next iteration)
- **Shopping list view**: Display aggregated claims grouped by source (separate feature)

**Future Features This Enables**:
- Shopping list generation (aggregate claims by source)
- Claim visibility dashboard ("why no radish recipes?")
- Cook/Abandon workflow with inventory consumption
- Recipe library/history view

---

## Technical Planning Notes

### BAML Function Design

**FleshOutRecipe** (new function):
- Input: pitch data, household context, inventory state
- Output: Complete recipe with structured ingredients + ingredient source assignments + purchase likelihoods
- Behavior: Generate full recipe maintaining pitch promises (name, key ingredients, effort level)

**GenerateRecipePitches** (modify existing):
- Add input: claimed_ingredients list, decremented_inventory state
- Add constraint: "DO NOT use these ingredients, pivot to remaining inventory"
- Maintains existing structure for output

### Complexity Assessment

**All components: Simple**

Prototype validated claiming works smoothly with no edge cases (LEARNINGS.md:74-80, 95-100).

**IngredientClaim creation**: **Simple**
- BAML declares ingredient source assignments + purchase likelihood
- Code loops through and creates claim records (just recording what LLM says)
- Atomic commit: trivial with SQLModel (add all claims, commit once)
- No fuzzy matching needed - trust LLM declarations

**Claim-aware inventory for "Generate More"**: **Simple**
- Query claims for session where `state="reserved"`
- Sum quantities by ingredient name
- Subtract from original inventory to get decremented state
- Pass decremented inventory + claimed list to BAML for pivot logic
- Same pattern prototype used successfully

**Recipe schema**: **Simple**
- Create new Recipe table
- No data migration (fresh start acceptable for MVP)

---

## Open Questions

**For alignment before technical planning**:

1. **Recipe identity validation**: Should flesh-out include validation that recipe matches pitch promises? Or trust LLM fidelity? (LEARNINGS.md:109-118 discusses pivot boundaries)
   - Suggest: Defer to post-MVP (abandon + regenerate is workaround)

2. **Purchase likelihood calibration**: Do we need to tune LLM prompts for likelihood scores or accept initial LLM judgment?
   - Suggest: Implement and test with real usage; adjust prompts if needed

---

## Alignment Complete

**User confirmation received**:
- ✅ Recipe schema looks solid (structured ingredients balance flexibility + structure)
- ✅ Numeric purchase likelihood (0.0-1.0) is correct granularity
- ✅ "Generate More" included in scope (claim-aware infrastructure needed for flesh-out anyway)
- ✅ Batch selection UX confirmed
- ✅ Recipe lifecycle state included (cook/abandon actions deferred to next iteration)
- ✅ Claiming complexity simplified - prototype proved this is straightforward

**Status**: Ready for technical planning

**Next step**: Use `create-tip pitch-selection-claims` to plan the technical implementation.
