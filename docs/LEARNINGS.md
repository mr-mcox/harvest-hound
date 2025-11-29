# Prototype Learnings

## Date Started: 2025-11-29

## Domain Model Discoveries

### Core Concepts
- [x] **Household Profile**: Can be baked into prompt, doesn't need database/UI complexity (at least for single-user)
  - Family context, equipment, preferences stored as prompt constants
  - Felt "in the ballpark" - may need prompt tweaking but approach is sound
  - (discovered: recipe-generation experiment, 2025-11-29)

- [x] **Store concept**: All stores auto-included for recipe generation feels right
  - Don't need per-generation store selection
  - Could potentially prioritize via context ("ingredients going bad") but not blocking
  - (discovered: recipe-generation experiment, 2025-11-29)

- [ ] Recipe states needed: **NEEDS EXPLORATION** - "recipe pitches" before full recipes desired
- [ ] Ingredient complexity level:

### Workflows That Feel Natural
1. [x] **Zero-click recipe generation**: Auto-loading all stores, optional context field
   - Big win: just click "Generate" without manual entry
   - Optional context useful when needed, ignorable when not
   - (discovered: recipe-generation experiment, 2025-11-29)

### Surprising Complexities

### Things Simpler Than Expected
- [x] **Single-page prototype goes far**: One page with progressive disclosure may be sufficient
  - Surprising that we don't need complex navigation yet
  - (discovered: recipe-generation experiment, 2025-11-29)

## Technical Discoveries

### BAML Prompts That Work
- [x] **Recipe generation with household profile**: Baked-in context approach works
  - Template: household profile + inventory + optional context + anti-duplicate tracking
  - Sequential generation (one at a time) prevents duplicates
  - May need more capable model (gpt-4o vs gpt-4o-mini) for quality
  - (discovered: recipe-generation experiment, 2025-11-29)

- [ ] Ingredient parsing:
- [ ] Substitution suggestions:

### API Shapes That Feel Right
- [x] **GET endpoint with query params for SSE**: EventSource compatibility matters
  - POST with request body doesn't work with EventSource
  - Query params for simple inputs (context, num_recipes) feels clean
  - (discovered: recipe-generation experiment, 2025-11-29)

### Performance Observations
- [x] **Streaming value: Yes, but still slow**
  - Seeing recipes one-at-a-time is better than waiting for all three
  - But ~3-5 sec per recipe still feels long
  - Suggests need for "recipe pitches" (faster, lighter) before full recipes
  - (discovered: recipe-generation experiment, 2025-11-29)

- [x] **Async BAML required for true streaming**
  - Sync mode blocks entire loop, all results flush at once
  - Async mode enables incremental SSE streaming
  - (discovered: recipe-generation experiment, 2025-11-29)

- [ ] Database queries:

## Use Cases (Keep Lean!)

### Essential (Must Have)
1. [x] **Generate recipes from current inventory with zero friction**
   - Validated: Auto-loading stores, optional context works well
   - (discovered: recipe-generation experiment, 2025-11-29)

2. [ ] **Quick inventory management** - Current bottleneck blocking authentic testing

3. [ ] **Recipe acceptance workflow** - Needs exploration of what "accept" means

### Nice to Have
- [ ] **5 recipes per week** (vs current 3) - easy parameter tweak, not blocking
- [ ] **Prioritize expiring ingredients** - could be solved via context field

### Not Needed
- [x] **Per-generation store selection** - Auto-including all stores works fine
  - (discovered: recipe-generation experiment, 2025-11-29) 

## Architecture Decisions for MVP

### Keep Simple
- [ ] 

### Still Don't Need  
- [ ] 

### Consider Adding
- [ ] 

## Next Steps
- [ ] Domain model sketch for MVP
- [ ] Priority features for implementation
- [ ] Technical debt worth taking