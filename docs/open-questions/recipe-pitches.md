# Recipe Pitches vs Full Recipes

**Discovered**: recipe-generation experiment, 2025-11-29
**Priority**: High (blocking progress)

## Observation

- Even with streaming, ~3-5 seconds per recipe feels slow
- User wants "recipe pitches" before fleshed out recipes

## Questions

- What's a "recipe pitch"? (name + key ingredients + time estimate?)
- Is this progressive disclosure? (scan pitches → select interesting → get full recipe)
- Or parallel generation? (fast pitches + slow full recipes in background)
- Does this change the domain model? (Recipe has PitchState + FullState?)

## Hypothesis

- Generate lightweight pitches first (~1 sec each)
- User picks 2-3 interesting ones
- Generate full recipes only for selected pitches

## Next Experiment

`/discover-pain` around recipe browsing speed
