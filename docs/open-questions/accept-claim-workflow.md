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

## Next Experiment

- Set up edge cases in prototype (conflicting recipes, missing ingredients)
- `/discover-pain` around recipe acceptance workflow
