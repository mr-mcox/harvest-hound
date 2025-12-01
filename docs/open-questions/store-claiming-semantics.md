# Store Claiming Semantics

**Discovered**: ingredient-claiming experiment, 2025-11-30
**Uncertainty**: High (only validated inventory claiming, grocery claiming untested)
**Architectural Impact**: High (affects claiming mechanics, data model, how stores are represented)
**One-Way Door**: Yes (claiming behavior is foundational to how the system works)

## The Question

What does "claiming an ingredient" mean for different store types? Does claiming behavior vary by store, or is it uniform?

## Context

Current implementation only handles inventory claiming (reservation of what you have). But recipes will need ingredients from grocery stores (what you need to buy). The semantics of "claiming" are fundamentally different:

**Inventory store claiming = Reservation**
- You HAVE the ingredient
- Claiming marks it as "spoken for"
- Prevents other recipes from using it
- Sequential claiming prevents conflicts

**Grocery store claiming = List Building**
- You DON'T have the ingredient
- Claiming adds it to shopping list
- Multiple recipes can share grocery items (buy once, use in multiple meals)
- Not blocking/conflicting like inventory

## Options Considered

### Option 1: Uniform Claiming (Current)
All stores use same claiming semantics (reservation).

**Pros**:
- Simple, one model
- Already implemented for inventory

**Cons**:
- Doesn't fit grocery stores (can't "reserve" what you don't have)
- Forces awkward workarounds

### Option 2: Store-Specific Claiming Semantics
Each store type defines what "claiming" means.

```python
class Store:
    name: str
    store_type: "inventory" | "grocery" | "pantry"
    claiming_behavior: "reserve" | "list_build" | "unlimited"

# Inventory stores
claiming_behavior = "reserve"  # Block other recipes from using

# Grocery stores
claiming_behavior = "list_build"  # Add to shopping list, not blocking

# Pantry stores
claiming_behavior = "unlimited"  # Never claim, always available
```

**Pros**:
- Models reality accurately
- Clear semantics per store type
- Extensible (can add new store types with different behaviors)

**Cons**:
- More complex claiming logic
- Need to handle different behaviors in generation flow

### Option 3: No Claiming for Grocery
Inventory stores use claiming (reservation), grocery stores don't claim at all.

**Pros**:
- Simpler than Option 2
- Separates concerns (inventory = claiming, grocery = just a list)

**Cons**:
- Less unified model
- Harder to reason about "what ingredients are needed for this week"

## Architectural Implications

**Affects claiming mechanics**:
```python
# Current (uniform):
claimed_ingredients = Set[str]

# Store-specific:
class Claim:
    ingredient: str
    store_id: int
    behavior: "reserve" | "list_build"

inventory_claims = {ingredient: store_id}  # Blocking
grocery_list = {ingredient: [recipe_ids]}  # Non-blocking, shared
```

**Affects recipe generation**:
- When LLM suggests ingredient, does it know which store it's from?
- Does claiming behavior affect ingredient selection?
- Example: "Use carrots from inventory OR add carrots to grocery list"

**Affects data model**:
- Need `Store.claiming_behavior` field?
- Or infer from `Store.store_type`?
- How to represent claims that span multiple stores?

**Affects grocery list view**:
- Grocery list is projection of "list_build" claims
- Shows which recipes need each ingredient
- User can review before shopping

## Related but Separate: Ingredient Optionality

**IMPORTANT**: Optionality (required vs optional) is ORTHOGONAL to store type.

- Inventory carrots can be optional ("would be nice if I use them")
- Grocery cheese can be required ("must buy for this recipe")
- Pantry paprika can be optional ("adds flavor but not essential")

Don't conflate these concerns. See `ingredient-optionality.md` for that question.

## Latest Exploration

**Date**: 2025-12-01 (ingredient-claiming-cognitive-load experiment)

### What Was Validated:

✅ **Explicit vs Definition Store Separation Works**
- Implemented two store types in BAML prompt:
  - **Explicit stores** (CSA, Freezer): Itemized with quantities, need claiming
  - **Definition stores** (Pantry Staples): Unlimited, never claimed
- LLM receives them in separate prompt sections, understands the distinction
- Code manages decremented inventory state for explicit stores only
- Backend tracks: `{store_name: {ingredient_name: (quantity, unit)}}`
- Definition stores never get claimed (always available)

✅ **Quantity-Aware Claiming Works**
- Claiming behavior: "reserve" (for explicit stores)
- Decrements quantities correctly
- Partial availability tracked: "0.5 lb remaining"
- No edge cases found in testing

### Store Type Mapping:

Current implementation maps to Option 2 (Store-Specific Claiming):

| Store Type | Claiming Behavior | Implementation Status |
|------------|-------------------|----------------------|
| Explicit (CSA, Freezer) | `reserve` | ✅ Implemented |
| Definition (Pantry) | `unlimited` | ✅ Implemented |
| Grocery | `list_build` | ❌ Not yet explored |

### What Remains Open:

**Grocery Store Claiming** (list-building semantics):
- Haven't tested recipes that need grocery ingredients yet
- Questions remain:
  - How does LLM decide ingredient comes from grocery vs inventory?
  - Can multiple recipes share same grocery item?
  - How to present grocery list to user?
  - Does claiming affect grocery differently than inventory?

## Success Criteria

- ✅ Clear definition of what "claim" means per store type (explicit = reserve, definition = unlimited)
- ✅ Inventory claiming continues to work (reservation validated)
- ❌ Grocery claiming builds useful shopping list (not yet tested)
- ✅ No confusion between claiming semantics and optionality (kept separate)

## Next Experiment

1. ~~Implement store-specific claiming (Option 2)~~ ✅ DONE for explicit/definition stores
2. **Add grocery store type with list-building behavior**
3. Test with recipes that use both inventory and grocery ingredients
4. Mock grocery list view
5. Validate: Does reservation vs list-building distinction work?
