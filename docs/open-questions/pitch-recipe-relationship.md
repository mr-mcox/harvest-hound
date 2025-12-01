# Pitch vs Recipe Relationship

**Discovered**: ingredient-claiming-cognitive-load experiment, 2025-12-01
**Uncertainty**: High
**Architectural Impact**: High
**One-Way Door**: Yes

## The Question

Are Pitch and Recipe separate concepts, or are they the same aggregate root with different states/representations?

## Context

Currently treating them as separate:
- Pitch = lightweight view for browsing (name, blurb, explicit_ingredients, time)
- Recipe = full cooking instructions (ingredients, instructions, servings, notes)

But user insight suggests they might be related:
> "I'm curious long term whether it's a pitch state machine or recipe state machine and how we disambiguate pitches from fleshed out recipes. It's possible that they both have the same aggregate root but different states."

## Options Considered

### Option A: Separate Concepts
- Pitch and Recipe are distinct entities
- Pitch exists for browsing, gets "fleshed out" into Recipe
- Multiple Pitches could theoretically flesh out to same Recipe concept
- Simpler, no shared state management

### Option B: Same Aggregate, Different States
- Recipe is the aggregate root
- Pitch is a "proposed" state of Recipe
- Fleshing out is state transition: `proposed → detailed`
- Recipe identity is preserved across states
- Enables recipe equivalence checking via judge

### Option C: Pitch as Projection
- Recipe concept exists (possibly abstract)
- Pitch is a projection/view of that concept
- Fleshing out materializes the full recipe
- Multiple representations possible (pitch view, cooking view, grocery view)

## Architectural Implications

**Data model**:
- Option A: Two separate tables (pitch, recipe)
- Option B: Single table with state field
- Option C: Recipe core + view projections

**State management**:
- How do we track "this pitch was selected"?
- How do we know if a fleshed-out recipe matches its pitch?
- Can multiple pitches be the same underlying recipe?

**Identity and equivalence**:
- User mentioned: "We could employ the judge to evaluate whether they're functionally equivalent or not"
- Need judge to validate pitch → recipe fidelity
- Recipe identity matters for cooking sessions (same recipe, multiple instances)

**Claiming semantics**:
- Currently: Pitch declares explicit_ingredients (what it will claim)
- Fleshing out: Actually claims those ingredients
- If same aggregate: claiming is state transition side effect

## Related Concepts

**Cooking Session**:
> "I'm curious if there will be a concept of a unique cooking session - we could make exactly the same recipe multiple times, but for grocery shopping or feedback purposes we need something to hold them separate."

This suggests:
- Recipe = reusable template/concept
- Cooking Session = specific instance of making that recipe
- Multiple sessions can reference same recipe

**Recipe Representations**:
> "A fleshed out recipe could have multiple representations as well - different ways of formatting based on the current need."

Suggests different views:
- Cooking view (step-by-step instructions)
- Grocery view (shopping list)
- Meal planning view (summary info)
- Nutrition view (if needed later)

## Next Steps to Explore

1. **Test pitch equivalence**: When fleshing out multiple pitches, do any become "the same recipe"?
2. **Track cooking sessions**: When user makes recipe multiple times, what needs to be distinct?
3. **Prototype judge**: Can BAML evaluate if fleshed recipe matches pitch promise?
4. **Explore recipe variants**: If user tweaks a recipe, is it a new recipe or same recipe modified?

## Current Decision

**Defer** - Keep separate for now (Pitch and Recipe as distinct entities)
- Works for current prototype
- Low risk: can refactor later once we understand the relationship better
- Gather more data on equivalence and session tracking needs
