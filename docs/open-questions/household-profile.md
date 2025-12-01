# Household Profile Effectiveness

**Discovered**: recipe-generation experiment, 2025-11-29
**Uncertainty**: Low (feels "in the ballpark", just needs minor refinement)
**Architectural Impact**: Low (just prompt tuning, no data model or flow changes)
**One-Way Door**: No (can iterate on prompt anytime)

## Current State

- Household profile baked into BAML prompt
- Felt "in the ballpark" but hard to judge without full inventory

## Questions

- Does prompt need tweaking to emphasize kid-friendly, active time minimization?
- Is gpt-4o-mini sufficient or need gpt-4o for better quality?
- How do we validate recipes match household preferences?
- Is there a feedback loop? ("This recipe was too complex" → adjust future generations)

## Next Experiment

After inventory is easier, evaluate recipe quality authentically
