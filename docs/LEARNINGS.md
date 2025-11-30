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

- [x] **Portioning constraints discovered**: Inventory has discrete vs infinitely divisible items
  - Freezer meat: 2 lbs = 2 separate 1-lb packages (can't use 1.5 lbs)
  - Vegetables: 2 lbs carrots = bulk (can use any amount)
  - Low confidence if worth modeling explicitly - could be store-level context
  - Affects: recipe generation (what amounts to suggest), inventory editing (increment/decrement UX)
  - (discovered: inventory-management experiment, 2025-11-29)

- [x] **Store definitions dual-purpose**: What belongs + parsing context
  - Example: "Freezer meat. Portions are typically 1 lb unless otherwise specified"
  - Might be overloading a concept, but both are LLM-facing so acceptable for now
  - Watch for: If non-LLM uses emerge, may need separation
  - (discovered: inventory-management experiment, 2025-11-29)

- [ ] Recipe states needed: **NEEDS EXPLORATION** - "recipe pitches" before full recipes desired
- [ ] Ingredient complexity level:

### Workflows That Feel Natural
1. [x] **Zero-click recipe generation**: Auto-loading all stores, optional context field
   - Big win: just click "Generate" without manual entry
   - Optional context useful when needed, ignorable when not
   - (discovered: recipe-generation experiment, 2025-11-29)

2. [x] **Bulk inventory entry via free text**: Single textarea replacing 3-field form
   - User reaction: "soooo much easier. I love it."
   - Real CSA delivery list pasted and parsed accurately
   - One action: paste → parse → all ingredients added
   - (discovered: inventory-management experiment, 2025-11-29)

3. [x] **Inline inventory editing**: Delete and update quantity per item
   - Delete works great, heavily used for cleanup
   - Update quantity works but feels "janky" for count-based items (3 roasts → 2 roasts)
   - Suggests portioning awareness could improve UX
   - (discovered: inventory-management experiment, 2025-11-29)

### Surprising Complexities

### Things Simpler Than Expected
- [x] **Single-page prototype goes far**: One page with progressive disclosure may be sufficient
  - Surprising that we don't need complex navigation yet
  - (discovered: recipe-generation experiment, 2025-11-29)

- [x] **Store management**: Used but infrequent
  - Deleted duplicate store (one-time cleanup)
  - Edited definition (refinement during setup)
  - Suggests: Could be buried in configuration interface long-term, doesn't need prominent UI
  - (discovered: inventory-management experiment, 2025-11-29)

## Technical Discoveries

### BAML Prompts That Work
- [x] **Recipe generation with household profile**: Baked-in context approach works
  - Template: household profile + inventory + optional context + anti-duplicate tracking
  - Sequential generation (one at a time) prevents duplicates
  - Sonnet 4.5 with extended thinking (2000 token budget): Quality matches prior Claude system
  - Dairy inference problem solved with explicit "only use inventory" constraint
  - (discovered: recipe-generation experiment, inventory-management experiment, 2025-11-29)

- [x] **Ingredient parsing with store context**: BAML ExtractIngredients + optional store definition
  - Handles "xN notation" (Butt Roast x3 → 3 roasts, not 3 pounds)
  - Store context influences parsing (e.g., "Freezer meat. Portions are typically 1 lb")
  - Parsing notes useful for problematic items
  - Accuracy: Successfully parsed real CSA delivery list
  - (discovered: inventory-management experiment, 2025-11-29)

- [x] **Item-based units for meats**: Using "roast", "chop", "pound" instead of just weights
  - Better context for recipe generation (knows 3 roasts vs 3 pounds)
  - Enables more accurate portioning suggestions
  - (discovered: inventory-management experiment, 2025-11-29)

- [ ] Substitution suggestions:

### API Shapes That Feel Right
- [x] **GET endpoint with query params for SSE**: EventSource compatibility matters
  - POST with request body doesn't work with EventSource
  - Query params for simple inputs (context, num_recipes) feels clean
  - (discovered: recipe-generation experiment, 2025-11-29)

- [x] **Bulk operations via single endpoint**: POST /stores/{id}/inventory/bulk
  - Free text input → BAML parsing → bulk insert
  - Returns added items + parsing notes + skipped items
  - Single round-trip for entire CSA delivery
  - (discovered: inventory-management experiment, 2025-11-29)

- [x] **Inline CRUD on inventory items**: Simple DELETE and PATCH by item ID
  - DELETE /inventory/{id} - one-click removal
  - PATCH /inventory/{id} - quantity updates
  - No need for batch operations, single-item is sufficient
  - (discovered: inventory-management experiment, 2025-11-29)

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

2. [x] **Bulk inventory entry**: Paste CSA delivery list and parse
   - Validated: Major workflow improvement, heavily used
   - Enables authentic testing with real inventory
   - (discovered: inventory-management experiment, 2025-11-29)

3. [x] **Basic inventory editing**: Delete and adjust quantities
   - Validated: Delete heavily used for cleanup
   - Update quantity works but could be better for count-based items
   - (discovered: inventory-management experiment, 2025-11-29)

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