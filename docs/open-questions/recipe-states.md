# Recipe States & Lifecycle

**Discovered**: recipe-generation experiment, 2025-11-29
**Priority**: Medium (workflow clarity needed)

## Current Model

Recipe = just data (name, ingredients, instructions)

## Emerging States

- Pitch? (lightweight preview)
- Generated (full recipe available)
- Accepted (added to meal plan)
- Cooking (active step-by-step mode?)
- Completed (cooked, possibly with feedback)

## Questions

- What states actually matter?
- What transitions are allowed? (can you unclaim ingredients? re-generate variation?)
- Does MealPlan own accepted recipes or just reference them?
- When do recipes get saved to database vs ephemeral?

## Latest Exploration

**Date**: 2025-11-29 (recipe-pitch-selection experiment)

### What We Learned

**Pitch state CONFIRMED**:
- Pitch is a real, distinct representation (not just a summary)
- Works as a projection of an underlying recipe concept
- Pitch = name + emotional blurb + practical appeal + key ingredients + time
- Full recipe = complete cooking instructions
- Transition: User selects pitch → system fleshes out → full recipe generated

**Ingredient claiming is CRITICAL**:
- Selecting a pitch needs to "reserve" its key ingredients
- Without claiming, multi-wave generation reuses ingredients (broken workflow)
- Claims need to be ephemeral during pitch browsing session
- Still unclear: When does claim become persistent? (at acceptance? at cooking?)

**Still unknown**:
- What does "accept to meal plan" actually mean?
- When do recipes get saved to database vs stay ephemeral?
- Can you unclaim ingredients (deselect pitch)?
- Can you "steal" ingredient from one recipe for another?

### Updated State Understanding

**Confirmed states**:
1. **Pitch** (lightweight, browsable, ephemeral) - ingredients reserved but not claimed
2. **Full Recipe** (fleshed out, ready to cook) - still ephemeral? or saved?
3. **Accepted** (added to meal plan?) - persistent claim on ingredients?
4. **Cooking** (active mode?) - TBD
5. **Completed** (cooked, ingredients consumed) - TBD

**Key insight**: Recipe representations are more important than recipe states. Same recipe concept can have multiple views (pitch, full, sous chef version, etc.)

## Next Experiment

**High priority**: Implement ingredient claiming for pitch selection workflow

**Medium priority**: Explore recipe acceptance workflow to clarify when recipes become persistent
