# Feature Frame: Shopping List & Recipe Lifecycle (Steel Thread Completion)

**Date**: 2025-12-07
**Status**: Aligned - Ready for Technical Planning

---

## Problem Statement

Users need to see what groceries to buy (ingredients from planned recipes minus what's already claimed from inventory) and mark recipes as cooked or abandoned to complete the weekly meal planning loop. These are the final two pieces of the steel thread: **planning → shopping → cooking**.

**From Prototype Discovery**:
- Shopping list fills workflow gap between planning and actual shopping (LEARNINGS.md:324-331)
- Recipe lifecycle validated: planned → cooked/abandoned (LEARNINGS.md:88-93)
- Likelihood-based sourcing enables force-ranked grocery list (LEARNINGS.md:233-240)

---

## User Stories

### Story 1: Generate Force-Ranked Shopping List
**As a** meal planner
**I want** to see what groceries I need to buy for my planned recipes, ordered by confidence
**So that** I can efficiently shop for ingredients not already in my inventory

**Acceptance Criteria**:
- [ ] GET endpoint aggregates all ingredients from planned recipes in a session
- [ ] System subtracts claimed inventory items from ingredient list
- [ ] Remaining ingredients scored with purchase likelihood (0.0-1.0)
- [ ] Response groups ingredients by type: Pantry Staples vs Grocery items
- [ ] Grocery items ordered by purchase likelihood (high confidence first)
- [ ] Each ingredient shows: name, total quantity needed, which recipes use it
- [ ] Pantry Staples section shows items to verify before cooking
- [ ] Purchase likelihood comes from BAML (LLM judgment during flesh-out)

**From LEARNINGS.md**:
- Shopping list aggregates claims by ingredient source (line 446-451)
- Format: "2 onions - used in: Recipe A, Recipe B" (line 326-327)
- Pantry verification checklist reduces anxiety (line 328)
- Likelihood-based sourcing (line 233-240)

### Story 2: Mark Recipe as Cooked
**As a** meal planner
**I want** to mark a recipe as cooked when I make it
**So that** the system consumes the ingredient claims and tracks what I've completed

**Acceptance Criteria**:
- [ ] POST endpoint to mark recipe as cooked by recipe ID
- [ ] Recipe.state transitions from PLANNED to COOKED
- [ ] Recipe.cooked_at timestamp set to current time
- [ ] All IngredientClaims for recipe are deleted (consumed/fulfilled)
- [ ] InventoryItem quantities decremented by claimed amounts
- [ ] Inventory stays accurate (reflects physical reality in kitchen)
- [ ] Action is idempotent (can mark cooked multiple times without error)
- [ ] Returns updated recipe state and inventory items affected

**From LEARNINGS.md**:
- Recipe lifecycle states validated (line 88-93)
- Cook action consumes claims, decrements inventory (line 302)
- Claims work transparently in background (line 95-100)

### Story 3: Mark Recipe as Abandoned
**As a** meal planner
**I want** to abandon a recipe I no longer plan to cook
**So that** the claimed ingredients are released back to inventory for other recipes

**Acceptance Criteria**:
- [ ] POST endpoint to mark recipe as abandoned by recipe ID
- [ ] Recipe.state transitions from PLANNED to ABANDONED
- [ ] All IngredientClaims for recipe are deleted (releases inventory)
- [ ] Released ingredients become available for future generation waves
- [ ] Action is idempotent (can mark abandoned multiple times without error)
- [ ] Returns updated recipe state

**From LEARNINGS.md**:
- Abandon action releases claims without consuming inventory (line 302)
- Low-friction abandoning makes auto-save acceptable (line 304)
- Recipe lifecycle states validated (line 88-93)

---

## Prototype Contrast

| Aspect | Prototype | MVP | Why Change |
|--------|-----------|-----|------------|
| **Shopping list** | Manual tracking outside system | Computed endpoint with likelihood ranking | Complete the planning → shop → cook loop |
| **Ingredient sourcing** | Binary Grocery/Pantry split | Likelihood-based scoring (0.0-1.0) | Force-ranked list, user judgment on grey area items |
| **Recipe lifecycle** | No state transitions | Cook/Abandon endpoints | Enable ingredient release and inventory updates |
| **Claim lifecycle** | Permanent records | Temporary reservations (deleted on cook/abandon) | Claims are planning-time constructs, not permanent audit trail |
| **Inventory accuracy** | Not maintained | Decremented on cook, released on abandon | Inventory reflects physical reality in kitchen |

**Preserve from Prototype**:
- IngredientClaim only tracks inventory items (not extended to all ingredients)
- Claims work invisibly in background
- Recipe lifecycle state enum (RecipeState)

**Fix from Prototype**:
- Add shopping list aggregation (gap in workflow)
- Add lifecycle transition endpoints (no way to complete recipes)

**Change from Prototype**:
- Shopping list is computed on-demand (not stored claims)
- Likelihood scoring for non-inventory ingredients (cached during flesh-out)
- Claims are temporary (deleted on cook/abandon, not transitioned to CONSUMED state)

---

## Technical Design

### Shopping List Computation Algorithm

**Purchase likelihood cached during flesh-out** - computed on-demand from cached data:

**Step 1: Extend RecipeIngredient schema** (stored in Recipe.ingredients JSON):
```python
class RecipeIngredient(BaseModel):
    name: str
    quantity: str
    unit: str
    preparation: str | None
    notes: str | None
    # NEW FIELDS (assigned during flesh-out):
    ingredient_source: str | None       # "inventory" | "pantry" | "grocery"
    purchase_likelihood: float | None   # 0.0-1.0 for grocery/pantry, None for inventory
```

**Step 2: FleshOutRecipe BAML assigns likelihood**:
- During recipe flesh-out, LLM assigns ingredient_source and purchase_likelihood for EVERY ingredient
- LLM has full context: recipe, household profile, current inventory state
- Better judgments than scoring ingredients in isolation later

**Step 3: Shopping list endpoint aggregates** (on-demand, not stored):
1. Query all planned recipes in session
2. Extract all ingredients from Recipe.ingredients JSON
3. Query all current InventoryItems (for staleness mitigation)
4. For each ingredient:
   - If ingredient.name matches current InventoryItem → skip (already have it, handles staleness)
   - Else use cached ingredient_source and purchase_likelihood
5. Aggregate quantities by ingredient name (simple concat: "2 cups + 1 whole")
6. Group by Pantry Staples (likelihood <0.3) vs Grocery (≥0.3)
7. Sort grocery items by likelihood descending (high confidence first)
8. Track which recipes use each ingredient

**Staleness mitigation**: Re-checking current inventory handles edge case where user adds ingredient between flesh-out and shopping list generation (rare in practice - typically minutes apart).

### Shopping List Response Schema

```python
class ShoppingListItem(BaseModel):
    ingredient_name: str
    total_quantity: str          # "2 cups + 1 whole" (simple concat across recipes)
    unit: str                    # Dominant unit (or empty if mixed)
    purchase_likelihood: float   # 0.0-1.0
    used_in_recipes: list[str]   # Recipe names that use this ingredient

class ShoppingListResponse(BaseModel):
    grocery_items: list[ShoppingListItem]     # likelihood ≥0.3, sorted desc
    pantry_staples: list[ShoppingListItem]    # likelihood <0.3
    session_id: UUID
```

**UI Note**: All items shown in single list with visual separator (e.g., horizontal rule) at 0.3 threshold. User can see full spectrum from "definitely buy" to "probably have".

### Lifecycle Endpoint Schemas

```python
class CookRecipeRequest(BaseModel):
    recipe_id: UUID

class CookRecipeResponse(BaseModel):
    recipe_id: UUID
    new_state: str                      # "cooked"
    claims_deleted: int                 # Number of claims deleted
    inventory_items_decremented: int    # Number of inventory items updated

class AbandonRecipeRequest(BaseModel):
    recipe_id: UUID

class AbandonRecipeResponse(BaseModel):
    recipe_id: UUID
    new_state: str              # "abandoned"
    claims_released: int        # Number of claims deleted (inventory released)
```

**Cook action implementation**:
1. Query IngredientClaims for recipe
2. For each claim: decrement InventoryItem.quantity by claim.quantity
3. Delete all claims for recipe
4. Update Recipe.state to COOKED, set cooked_at timestamp
5. All in single transaction (atomic)

**Abandon action implementation**:
1. Delete all IngredientClaims for recipe (releases inventory)
2. Update Recipe.state to ABANDONED
3. Inventory unchanged (claims never consumed)

---

## Out of Scope (Deferred)

Explicitly NOT part of this feature:

- **Copy-to-clipboard functionality**: Frontend implementation (deferred to fidelity pass)
- **Essential vs optional ingredients**: All ingredients treated as essential (deferred per MVP-CHARTER.md:68)
- **Multiple grocery stores**: Shopping list doesn't group by store (Cub, Costco, etc.) - deferred
- **Bulk lifecycle actions**: No "mark all cooked" - individual recipes only
- **Recipe editing after planning**: Abandon + regenerate is workaround
- **History view**: No record of cooked/abandoned recipes beyond state field

**Future Features This Enables**:
- Grocery store grouping (Costco run vs Cub run)
- Shopping list export formats (PDF, email, SMS)
- Recipe history dashboard (what we've cooked this month)
- Ingredient waste tracking (what got abandoned)

---

## Design Decisions (Aligned)

1. **Purchase likelihood storage**: Cache during flesh-out (Approach A)
   - Extend RecipeIngredient with ingredient_source and purchase_likelihood fields
   - LLM assigns during FleshOutRecipe (full context → better judgments)
   - Staleness mitigation: re-check current inventory during shopping list aggregation
   - Rationale: Better data quality, simpler endpoint, aligns with "LLM declares, code manages"

2. **Quantity aggregation**: Simple string concatenation
   - Example: "2 cups + 1 whole - used in: Recipe A, Recipe B"
   - Simplest approach for MVP, good enough for steel thread
   - Can refine to unit normalization later if needed

3. **Pantry threshold**: <0.3 = Pantry Staples, ≥0.3 = Grocery
   - Show all items in single list with visual separator at boundary
   - User sees full spectrum from "definitely buy" to "probably have"

4. **Cook action**: Delete claims + decrement inventory (NO CONSUMED state)
   - Claims are temporary reservations, not permanent records
   - Inventory stays accurate (reflects physical reality)
   - Simpler state machine, fewer edge cases
   - Rationale: Inventory should reflect what's physically in kitchen

---

## Complexity Assessment

**Shopping List Computation: Simple**
- Likelihood already cached in Recipe.ingredients (assigned during flesh-out)
- Aggregate recipe ingredients: straightforward JSON field extraction
- Staleness mitigation: simple inventory name matching (one SELECT + in-memory filter)
- Quantity aggregation: string concatenation ("2 cups + 1 whole")
- Grouping/sorting: basic array operations (filter by threshold, sort by likelihood)

**Lifecycle Transitions: Simple**
- Cook endpoint: Query claims → decrement inventory → delete claims → update recipe (single transaction)
- Abandon endpoint: Delete claims → update recipe (single transaction)
- No complex state machine - just two transitions from PLANNED state
- Idempotency: Check recipe.state first (if already COOKED/ABANDONED, no-op)

**Total complexity: Simple** - both features are straightforward database operations with minimal business logic. No CONSUMED state eliminates state machine complexity.

---

## Alignment Complete

**Status**: Ready for technical planning

**User confirmation received**:
- ✅ Purchase likelihood cached during flesh-out (Approach A with staleness mitigation)
- ✅ Quantity aggregation: simple string concatenation
- ✅ Pantry threshold: <0.3 with visual separator showing all items
- ✅ Cook action: delete claims + decrement inventory (no CONSUMED state)
- ✅ Stories validate steel thread completion

**Next step**: Use `create-tip steel-thread-completion` to plan the technical implementation.
