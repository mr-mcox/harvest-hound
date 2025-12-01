# Ingredient Claiming Mechanics

**Discovered**: recipe-pitch-selection experiment, 2025-11-29
**Uncertainty**: Medium-High (current implementation works but has architectural smells)
**Architectural Impact**: High (affects BAML design, generation flow, state ownership, recipe schema)
**One-Way Door**: Yes (refactoring BAML prompts and generation flow is expensive)

## Problem

Multi-wave recipe generation reuses ingredients already allocated to selected pitches. When user picks 3 recipes using carrots, the next wave also suggests recipes with carrots even though they're "spoken for."

## Questions

**When are ingredients claimed?**
- When pitch is selected?
- When recipe is fleshed out?
- When recipe is accepted to meal plan?

**How are claims represented?**
- Decrement inventory quantities?
- Track "reserved" amounts separately?
- Ephemeral state during generation session vs persistent?

**When are claims released?**
- User deselects pitch?
- User removes recipe from meal plan?
- Session ends?
- Week is completed?

**How does claiming affect generation?**
- Exclude claimed ingredients from available inventory?
- Allow re-use but deprioritize?
- Track multiple "reservations" on same ingredient?

**Edge cases:**
- Ingredient partially claimed (2 lbs carrots, 1 lb claimed, 1 lb still available)
- User wants to "steal" ingredient from one recipe for another
- Ingredient expires before cooking happens

## Hypothesis

**Simple approach:**
- Claims are ephemeral during pitch browsing session
- Selecting a pitch "reserves" its key ingredients
- Deselecting releases them
- Fleshing out doesn't change claim state (still reserved)
- "Accept to meal plan" converts to persistent claim (decrements inventory)
- Claims released when meal is cooked or user removes from plan

## Latest Exploration

**Date**: 2025-11-30 (ingredient-claiming experiment - Phases 1 & 2)

### Questions ANSWERED:

**When are ingredients claimed?**
✅ **ANSWERED**: Fleshing out is the claiming moment (not pitch selection, not acceptance)
- Selecting pitch = visual selection only
- Fleshing out = creates ephemeral claim on inventory ingredients
- Sequential flesh-out prevents conflicts (Recipe 1 claims → Recipe 2 avoids)

**How are claims represented?**
✅ **ANSWERED**: Ephemeral claims filtered to inventory items only
- Track claimed ingredient names (not quantities yet)
- Filter to only items in inventory system (pantry staples don't get claimed)
- Pass claimed ingredients to next recipe generation for auto-pivot
- Not decrementing inventory, just tracking "spoken for" status

**When are claims released?**
⏸️ **PARTIALLY ANSWERED**: Ephemeral claims work, persistent claims unexplored
- Ephemeral claims during session (implemented)
- Persistent claims when accepting to meal plan (Phase 3 - not yet explored)
- Release on cooking vs removing from plan (Phase 3 - not yet explored)

**How does claiming affect generation?**
✅ **ANSWERED**: Exclude from available inventory, LLM auto-pivots
- Claimed ingredients passed to BAML generation
- LLM pivots to remaining inventory ingredients
- Works well when pivot stays within recipe concept
- **NEW DISCOVERY**: Needs identity validation (beef→pork broke recipe promise)

### New Complexities Discovered:

**Multiple claim types needed**:
- Inventory claiming: Reserve what you have (implemented)
- Grocery claiming: Build list for what you need (not implemented)
- Optional ingredients: Suggestions, not requirements (not implemented)

**Recipe identity boundaries**:
- Auto-pivot works BUT can break the pitch promise
- Example: "Beef Pot Roast" pitch → "Pork Butt Pot Roast" recipe = broken trust
- Need validator to check if pivot is too different

**Edge cases partially addressed**:
- Pantry staples: Solved (filter to inventory only)
- Partial claims: Not yet handled
- Stealing ingredients: Not yet explored
- Ingredient expiration: Not yet handled

## Architectural Implications

**Current approach (architectural smell)**:
```
Prompt: "Generate recipe avoiding: carrots, beef, potatoes"
LLM: *tries to remember what's available*
LLM: *does implicit inventory subtraction*
LLM: *might accidentally use claimed ingredients*
```

**Problems**:
- LLM doing inventory management (not its strength)
- Implicit state subtraction (error-prone)
- Unclear separation of concerns (who owns availability state?)

**Better approach**:
```
LLM: Generate recipe → outputs claimed_ingredients: ["carrots", "beef"]
Code: claimed.update(recipe.claimed_ingredients)
Code: available = inventory - claimed
LLM: Generate next recipe with explicit available list
```

**Benefits**:
- Clear separation: LLM generates, code manages state
- Deterministic claiming (auditable)
- LLM focuses on recipe quality, not inventory math
- Affects: RecipePitch schema needs `claimed_ingredients` field

## Still Open:

Phase 3 questions remain:
- Persistent claims when accepting to meal plan
- Claims release workflow (cooking vs removing from plan)
- Partial quantity claiming (2 lbs total, 1 lb claimed, 1 lb available)

## Next Experiments:

1. **Fix claiming implementation** (high priority) - Switch to explicit claiming with LLM outputting claimed ingredients
2. **Recipe identity validation** (high priority) - Prevent pivots that break pitch promise
3. **Store claiming semantics** (medium priority) - Different claim behavior per store type
4. **Phase 3: Meal plan acceptance** (future) - Persistent claims and release workflow
