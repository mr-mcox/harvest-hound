# Ingredient Claiming Mechanics

**Discovered**: recipe-pitch-selection experiment, 2025-11-29
**Priority**: High (blocking iterative workflow)

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

## Next Experiment

Implement claiming as ephemeral state during pitch generation:
- Track selected pitches + their key ingredients
- Pass "unavailable_ingredients" to next wave generation
- Test if this unblocks iterative workflow

## Success Criteria

- Second wave doesn't reuse ingredients from selected pitches
- User can pick 3 → generate more → pick 2 more successfully
- Feels natural (doesn't require explaining the claiming concept)
