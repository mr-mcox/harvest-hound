# Accept vs Claim Ingredients Workflow

**Discovered**: recipe-generation experiment, 2025-11-29
**Priority**: Medium (workflow clarity needed)

## Current State

- UI has "Accept Recipe" and "Claim Ingredients" buttons
- Unclear what happens when either is pressed
- Relationship between the two actions is undefined

## Questions

- What does "accept" mean?
  - Add to meal plan?
  - Mark as "interested"?
  - Reserve ingredients?

- Should "claim" be separate from "accept"?
  - Or are they the same action?
  - When does claiming happen? (accept → plan → cook → claim?)

- What happens if ingredients are no longer available after accepting?
  - Does accept fail?
  - Suggest substitutions?
  - Partial claim with "missing ingredients" list?

- Can user give feedback on individual recipes to tweak?
  - "Make it spicier"
  - "Use chicken instead of beef"
  - Regenerate variations?

## Edge Cases to Explore

- Accept recipe → ingredients gone when ready to cook
- Accept recipe → only some ingredients available
- Accept 3 recipes → overlapping ingredients → which recipe gets priority?
- Recipe needs 2 lbs carrots → only have 1 lb → partial recipe? substitute?

## Hypothesis

- "Accept" = add to meal plan for the week
- "Claim" happens when starting to cook (not at accept time)
- Need to explore ingredient claiming as negotiation, not just decrement

## Latest Exploration

**Date**: 2025-11-30 (ingredient-claiming experiment)

### Clarifications Made:

**Three distinct moments discovered:**
1. **Fleshing out** = Ephemeral claim on ingredients (implemented)
   - Reserves inventory items during session
   - Enables auto-pivot for subsequent recipes
   - Not persistent, not consumption

2. **Accept to meal plan** = Persistent claim (not yet explored)
   - Would make claim permanent for the week
   - Ingredients stay in inventory but marked "reserved"
   - Allows for life happening (pizza night, ingredient goes bad)

3. **Cooking** = Actual consumption (not yet explored)
   - Ingredients decremented from inventory
   - Can track feedback and note substitutions
   - "Cooked" button triggers consumption

**Distinction confirmed**: Claims ≠ Consumption
- Accepting reserves ingredients but doesn't decrement
- Prevents "shriveled turnip" problem (forgetting what was planned)
- Can see what's physically available vs planned

### Still Unexplored:

- What does "accept to meal plan" UI/UX look like?
- What happens if ingredients unavailable when ready to cook?
- Can user give feedback to tweak recipes after acceptance?
- How to handle overlapping ingredient needs across accepted recipes?
- Should there be a "meal plan view" showing all accepted recipes + reserved ingredients?

## Next Experiment

- `/discover-pain accept-to-meal-plan` - Explore acceptance workflow and meal plan management
