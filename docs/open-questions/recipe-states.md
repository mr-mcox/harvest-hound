# Recipe States & Lifecycle

**Discovered**: recipe-generation experiment, 2025-11-29
**Uncertainty**: Medium (some states validated, Phase 3+ still unclear)
**Architectural Impact**: High (affects persistence, what gets saved, state transitions)
**One-Way Door**: Yes (state management and persistence are foundational)

**Note**: Overlaps with `accept-claim-workflow.md` - consider consolidating after Phase 3 exploration

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

## Latest Exploration (Update 2)

**Date**: 2025-11-30 (ingredient-claiming experiment)

### Additional Learnings:

**Fleshing out timing confirmed**:
- Fleshing out is when ingredients get claimed (ephemeral)
- Not at pitch selection (just visual selection)
- Not at acceptance (that's persistent claim - unexplored)

**Recipe identity validation needed**:
- NEW STATE DISCOVERED: Recipe can pivot during flesh-out
- Pivot should stay within recipe concept (radish→potato ✓)
- Pivot can break identity (beef→pork ✗)
- Need validator: Does fleshed recipe match pitch promise?
- Three failure modes:
  1. Can't make with available ingredients
  2. Effort significantly different (quick→long braise)
  3. Family expectations broken ("that's not what I thought")

**Pitch lifecycle states**:
- Active (selectable)
- Ingredient Conflict (should be disabled/grayed when ingredients claimed)
- Selected (user picked it)
- Fleshed Out (full recipe generated)

### Updated State Understanding:

**Confirmed states with timing**:
1. **Pitch** (lightweight, browsable) - ephemeral, no claims yet
2. **Selected Pitch** - visual selection, still ephemeral
3. **Fleshing Out** - generating full recipe, THIS is where ephemeral claims happen
4. **Full Recipe** - fleshed out, ingredients claimed (ephemeral), ready to review
5. **Accepted** (to meal plan) - persistent claim on ingredients (unexplored)
6. **Cooking** - consumption event (unexplored)
7. **Completed** - cooked, ingredients consumed, can provide feedback (unexplored)

**Also discovered**: Pitches need lifecycle management
- Pitches should be disabled/grayed when their key ingredients are claimed by fleshed-out recipes
- Visual feedback for ingredient conflicts

## Next Experiments

**High priority**:
1. Recipe identity validation - Judge whether pivot is acceptable
2. Pitch disabling when ingredients claimed

**Medium priority**:
3. Explore recipe acceptance workflow to clarify persistent claims
