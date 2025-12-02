# Ingredient Optionality

**Discovered**: ingredient-claiming experiment, 2025-11-30
**Uncertainty**: Medium (observed in recipes, but not yet modeled)
**Architectural Impact**: Medium (affects ingredient representation, recipe generation)
**One-Way Door**: Partially (affects data model, but mostly additive)

## The Question

How should we model required vs optional ingredients? Is optionality independent of ingredient source (inventory, grocery, pantry)?

## Context

Recipes naturally include optional ingredients that enhance the meal but aren't essential:
- Coleslaw for pulled pork sandwiches (nice to have)
- Cheese for topping soup (enhances but not required)
- Garnishes like cilantro or green onions (visual appeal)

**Key insight**: Optionality is ORTHOGONAL to source.
- Inventory ingredients can be optional
- Grocery ingredients can be optional
- Pantry ingredients can be optional

## Current State

**Observed in recipes**:
- LLM suggests optional ingredients naturally
- Currently treating all ingredients as required
- No way to distinguish "must have" from "nice to have"

## Options Considered

### Option 1: Binary Optional Flag
```python
class IngredientRequirement:
    name: str
    quantity: float
    optional: bool  # True = nice to have, False = required
```

**Pros**:
- Simple, clear
- Easy for LLM to output

**Cons**:
- Binary might be too coarse (some ingredients more optional than others)

### Option 2: Optionality Levels
```python
class IngredientRequirement:
    name: str
    quantity: float
    necessity: "required" | "recommended" | "optional"
```

**Pros**:
- More nuanced
- Allows prioritization in grocery list

**Cons**:
- More complex
- Harder for LLM to distinguish levels

### Option 3: No Explicit Modeling
Just use natural language in recipe instructions.

**Pros**:
- Simplest
- Flexible

**Cons**:
- Can't filter or prioritize programmatically
- Grocery list can't separate essential from optional

## How This Interacts With Store Types

**Important**: Optionality is about the RECIPE, not the STORE.

```python
# Example: Optional ingredient from inventory
{
    name: "carrots",
    source: "inventory",  # From CSA delivery store
    optional: True  # Would be nice but not required
}

# Example: Required ingredient from grocery
{
    name: "ground beef",
    source: "grocery",  # Need to buy
    optional: False  # Recipe needs this
}

# Example: Optional ingredient from grocery
{
    name: "sour cream",
    source: "grocery",  # Would need to buy
    optional: True  # Just for topping, not essential
}
```

**Don't conflate**:
- Optional ≠ from grocery store
- Required ≠ from inventory store
- These are separate dimensions

## Architectural Implications

**Affects ingredient representation**:
```python
class IngredientRequirement:
    name: str
    quantity: float
    unit: str
    source_store_id: int  # Where it comes from
    optional: bool  # Whether recipe needs it
```

**Affects recipe generation**:
- LLM outputs optionality per ingredient
- Prompt: "Mark ingredients as optional if they enhance but aren't essential"

**Affects grocery list view**:
```
Essential (must buy):
- Ground beef (for Tacos)
- Tortillas (for Tacos)

Optional (nice to have):
- Sour cream (for topping Tacos)
- Cilantro (for garnish)
```

**Affects claiming behavior**:
- Should optional ingredients be claimed?
- Example: Optional inventory carrots → don't block other recipes?
- Or: Mark as "lightly claimed" (can be stolen if needed)?

## Related: Store Claiming Semantics

See `store-claiming-semantics.md` for how claiming behavior varies by store type. That's a separate concern from whether an ingredient is optional.

## Latest Exploration - Orthogonal Dimensions Validated

**Date**: 2025-12-01 (ingredient-priority experiment)

### Key Insight: Ingredient Metadata Dimensions Are Independent

**Discovery**: Priority, location, and optionality are separate, orthogonal ingredient dimensions.

✅ **Validated Separation**:
- **Priority**: How urgently should this be used (drives recipe generation)
  - Values: low, medium, high, urgent
  - Example: Frozen meat = low, fridge bacon = high

- **Location**: Where is it physically stored (audit/organization)
  - Values: chest_freezer, refrigerator, cellar, pantry, premade
  - Example: Bacon in refrigerator (informs priority suggestion)

- **Optionality**: Is it required for the recipe (NOT YET IMPLEMENTED)
  - Values: required, optional
  - Example: Sour cream topping = optional, ground beef = required

**Each dimension serves a different purpose**:
- Priority → Meal planning (what to use this week)
- Location → Audit/organization (verify inventory)
- Optionality → Recipe flexibility (required vs nice-to-have)

**Don't conflate these**:
- Optional ≠ low priority (optional cream could be high priority if it's about to spoil)
- Location ≠ priority (refrigerator item could be low priority if not spoiling soon)
- Optionality ≠ source (optional ingredients can come from inventory, grocery, or pantry)

### Architectural Alignment

This validates Option 1 (Binary Optional Flag) approach:

```python
class IngredientItem:  # For inventory management
    name: str
    quantity: float
    unit: str
    location: str  # chest_freezer, refrigerator, cellar, pantry
    priority: str  # low, medium, high, urgent
    # No optionality here - that's recipe-specific, not inventory property

class IngredientRequirement:  # For recipes
    name: str
    quantity: float
    unit: str
    source_store_id: int  # Where it comes from
    optional: bool  # Whether recipe needs it
```

**Why this matters**: Optionality is a RECIPE property (is this ingredient required for THIS recipe?), not an INVENTORY property. The same ingredient could be required in one recipe and optional in another.

## Success Criteria

- Recipes can express optional ingredients naturally
- Grocery list shows essential vs optional sections
- User can decide which optional items to buy
- Optional ingredients don't unnecessarily block other recipes (if from inventory)
- Optionality remains orthogonal to location and priority

## Next Experiment

1. Add `optional: bool` to IngredientRequirement schema (recipe-level, not inventory-level)
2. Update BAML prompt to output optionality per ingredient per recipe
3. Test: Does LLM mark ingredients as optional appropriately?
4. Mock grocery list view with essential/optional sections
5. Validate: Optional inventory items don't block other recipes (claiming behavior)
