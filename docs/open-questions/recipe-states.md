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

## Next Experiment

Explore recipe acceptance workflow to clarify states
