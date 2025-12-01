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

- [x] **Recipe representations**: Pitch as projection of underlying recipe concept
  - Pitch = lightweight view for browsing (name, emotional blurb, practical appeal, key ingredients, time)
  - Full = complete cooking instructions
  - Pitch might be projection of internal recipe concept that doesn't get fleshed out until selected
  - Works well: ~80% ready for decision-making
  - Needs refinement: Sometimes title + blurb overlap unnecessarily
  - Selection criteria: "excited to make it" vs "meh, doesn't sound good"
  - (discovered: recipe-pitch-selection experiment, 2025-11-29)

- [x] **Ingredient claiming is CRITICAL**: Multi-wave generation breaks without it
  - Problem discovered: "Generate More Pitches" reuses ingredients already allocated to selected recipes
  - Need to track which ingredients are "claimed" by selected pitches
  - Blocking issue for iterative workflow (pick 3 → generate more → pick 2 more)
  - (discovered: recipe-pitch-selection experiment, 2025-11-29)

- [x] **Claiming mechanics validated**: Phases 1 & 2 implemented and working
  - Wave 2 avoids claimed ingredients successfully (no sneaking ingredients in)
  - Auto-pivot works well (radish → potato pivot felt natural)
  - Fleshing out is the right moment to claim ingredients (not pitch selection, not meal plan acceptance)
  - Sequential claiming prevents conflicts across multiple recipes
  - (discovered: ingredient-claiming experiment, 2025-11-30)

- [x] **Claiming sophistication needed**: Different claim types for different ingredient sources
  - Inventory claiming: Reserve what you have (current implementation)
  - Grocery claiming: Build shopping list for what you need to buy (not yet implemented)
  - Optional ingredients: Things that would enhance meal but aren't required (coleslaw, cheese, garnishes)
  - Three ingredient sources emerging: Inventory (have it), Grocery Essential (need it), Grocery Optional (nice to have)
  - Grocery store claiming is fundamentally different - it's list-building, not reservation
  - (discovered: ingredient-claiming experiment, 2025-11-30)

- [x] **Pantry staples vs inventory items**: Only claim trackable inventory
  - Problem: Was claiming "baking powder", "garlic powder" - pantry staples shouldn't block future recipes
  - Solution: Filter claimed ingredients to only items in inventory system
  - Pantry staples are effectively unlimited, don't need claiming
  - (discovered: ingredient-claiming experiment, 2025-11-30)

- [x] **Store type separation validated**: Explicit vs definition stores works architecturally
  - Explicit stores (CSA, Freezer): Itemized with quantities, need claiming
  - Definition stores (Pantry Staples): Unlimited, never claimed
  - LLM receives them separately in prompt, understands the distinction
  - Code manages decremented inventory state for explicit stores only
  - (discovered: ingredient-claiming-cognitive-load experiment, 2025-12-01)

- [x] **Quantity-aware claiming works smoothly**: No edge cases found
  - Backend tracks inventory as nested dict: {store_name: {ingredient_name: (quantity, unit)}}
  - Claiming decrements quantities correctly
  - Partial availability tracked ("0.5 lb remaining")
  - Auto-pivot respects decremented quantities (rainbow radish → black radish when inventory changes)
  - User reaction: "That worked great"
  - (discovered: ingredient-claiming-cognitive-load experiment, 2025-12-01)

- [x] **Pitch explicit ingredients**: Backend needs it, UI doesn't
  - explicit_ingredients used for claiming logic (what to decrement from inventory)
  - But UI doesn't need to display it - title + blurb sufficient for browsing
  - Validates architectural separation: code owns state management, UI shows human-friendly info
  - (discovered: ingredient-claiming-cognitive-load experiment, 2025-12-01)

- [x] **Recipe identity boundaries**: Pivots can break the pitch promise
  - Example problem: Pitch said "Beef Pot Roast (sirloin)", fleshed out used pork butt - NOT the same dish!
  - Three pivot boundaries that break identity:
    1. Can't make with available ingredients (substitution impossible)
    2. Effort significantly different (quick weeknight → 3-hour braise)
    3. Family expectations broken ("that's not what I thought we were having")
  - Need recipe identity validation: Judge whether pivot is too different from pitch
  - Possible solution: Early commitment to core ingredients, validate before returning fleshed recipe
  - Open question: How to implement this judge? Separate BAML call? Constraints in generation?
  - (discovered: ingredient-claiming experiment, 2025-11-30)

- [x] **Time representation needs refinement**: Both active AND total time matter
  - Current: only shows active time in pitches
  - Want: active + total time visible
  - Future idea: Quadrant visualization (total time vs passive time, 4 quadrants)
  - Progressive reveal: Hover for time breakdown?
  - (discovered: recipe-pitch-selection experiment, 2025-11-29)

- [x] **Week-level planning criteria**: Real need for structured constraints
  - Example: "1 weekend meal, 1 guest meal (weeknight), 2 quick meals, 1 leftovers meal"
  - Different from ad-hoc context ("busy week")
  - Helps system generate balanced variety for the week
  - (discovered: recipe-pitch-selection experiment, 2025-11-29)

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

4. [x] **Two-phase recipe browsing**: Pitches → selection → flesh out
   - Pitch browsing feels right for exploring options
   - Click-to-select interaction works well (reduced UI clutter vs checkboxes)
   - Fleshing out selected recipes feels right
   - User reaction: "This is what I hoped for from the system"
   - Pitch quality ~80% there for decision-making
   - (discovered: recipe-pitch-selection experiment, 2025-11-29)

5. [x] **Iterative recipe generation in waves**: Pick some → generate more → pick rest
   - Workflow confirmed: "Pick 3 → regenerate → pick 2 more → have 5 for the week"
   - BROKEN without ingredient claiming: second wave reuses already-claimed ingredients
   - Adaptive generation count needed: If picked N, don't need full 10 in next wave
   - (discovered: recipe-pitch-selection experiment, 2025-11-29)

6. [x] **Structured meal planning workflow**: Specs upfront, systematic filling
   - User provides meal needs with constraints: "quick weeknight x2", "guest meal that cooks while I work", "leftovers meal"
   - System generates pitches per category/spec
   - User selects from each category
   - Next wave fills remaining slots with remaining ingredients
   - Different from ad-hoc "generate 10 pitches" - this is purposeful, constraint-driven planning
   - Wave sizing: 3x the number of unfilled meal slots (if need 2 more meals, generate 6 pitches)
   - (discovered: ingredient-claiming experiment, 2025-11-30)

7. [x] **Pitch lifecycle management**: Invalid pitches should be removed automatically
   - Pitches using claimed ingredients become invalid (insufficient inventory)
   - Initially tried graying out invalid pitches for visibility
   - User feedback: "I'd like them removed" - don't want to see unavailable options
   - Suggests pitch pool maintenance: remove invalid, optionally backfill with new pitches
   - (discovered: ingredient-claiming experiment, ingredient-claiming-cognitive-load experiment, 2025-11-30/12-01)

8. [x] **Pitch pool self-healing**: Generate to maintain availability threshold
   - After claiming ingredients, some pitches become invalid (removed)
   - Want to maintain consistent pool of available options
   - Automatic backfill: when available pitches drop below threshold, generate more
   - Decision: Defer automatic backfill, manual "Generate More" works for now
   - (discovered: ingredient-claiming-cognitive-load experiment, 2025-12-01)

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

- [x] **Recipe pitch generation**: Two-field structure works well
  - Emotional blurb (1 sentence, sensory, makes you hungry) + practical "why" (3-5 words)
  - Blurb length about right for compelling decision-making
  - Sometimes title + blurb overlap unnecessarily (room for refinement)
  - Diversity prompt improvements: Removed time optimization bias, added explicit time diversity
  - Batch generation (all 10 pitches at once) then stream to frontend works well
  - ~80% ready for production, needs minor cleanup
  - (discovered: recipe-pitch-selection experiment, 2025-11-29)

- [x] **Pitch → full recipe fidelity**: "In the ballpark" is good enough
  - Fleshed out recipes roughly match pitch concept
  - Don't need perfect correspondence, just directionally correct
  - (discovered: recipe-pitch-selection experiment, 2025-11-29)

- [x] **Auto-pivot with claimed ingredients**: LLM handles substitutions well
  - Pass claimed ingredients to recipe generation → LLM pivots automatically
  - Example success: Radish → potato pivot in pot roast felt natural
  - Example failure: Beef sirloin → pork butt broke recipe identity (needs validation)
  - LLM prompt: "DO NOT use these ingredients, pivot to remaining inventory"
  - Works well when pivot stays within recipe concept
  - Breaks when core protein/technique changes significantly
  - (discovered: ingredient-claiming experiment, 2025-11-30)

- [x] **Optional ingredients for grocery enhancement**: Recipe suggestions beyond essentials
  - Recipes include optional additions: coleslaw, cheese, garnishes, etc.
  - These are "nice to have" not "must have" for the recipe
  - Creates opportunity for grocery list view with two sections:
    - Essential: Can't make recipe without these
    - Optional: Would enhance the meal, user decides
  - User can review optional items and decide which to add to grocery list
  - Different claiming model: optional items are suggestions, not reservations
  - (discovered: ingredient-claiming experiment, 2025-11-30)

- [x] **LLM/code separation of concerns**: Architectural win for recipe quality
  - Before: LLM did recipe creation AND inventory math simultaneously (cognitive overload)
  - After: LLM declares what it used (explicit_ingredients), code manages state
  - Benefits observed:
    - Quantity-aware claiming works smoothly (no edge cases)
    - Auto-pivot respects decremented inventory (rainbow radish → black radish)
    - Recipe quality improved (LLM focuses on recipes, not accounting)
  - User reaction: "This change is working quite well"
  - Validates architectural principle: LLM for content generation, code for state management
  - (discovered: ingredient-claiming-cognitive-load experiment, 2025-12-01)

- [x] **Technique diversity over ingredient diversity**: Prompt fixed CSA usage problem
  - Problem: LLM interpreted "MAXIMALLY DIVERSE" as "use different ingredients"
  - Result: Only 1 radish recipe when radishes are main CSA item → others rot if pitch unappealing
  - Fix: Explicit prompt guidance "diverse in TECHNIQUE, not ingredient choice"
  - Added: "5-7 radish recipes with different techniques is BETTER than forcing diversity across ingredients"
  - Success: User got multiple radish options, found something appealing
  - User reaction: "I have trouble with radishes and saw something I liked"
  - Validates: Fresh ingredients are high priority, need multiple creative options
  - (discovered: ingredient-claiming-cognitive-load experiment, 2025-12-01)

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

4. [x] **Browse recipe pitches before committing token budget**
   - Validated: Two-phase generation (pitches → flesh out) feels right
   - Essential for exploring diverse options without expensive full generation
   - User reaction: "This is what I hoped for from the system"
   - (discovered: recipe-pitch-selection experiment, 2025-11-29)

5. [x] **Ingredient claiming for multi-wave generation**
   - Validated: CRITICAL for iterative workflow
   - Without it, second wave reuses already-allocated ingredients
   - Blocking issue for "pick 3 → generate more → pick 2 more" workflow
   - Implemented in Phases 1 & 2: Wave 2 claiming + greedy flesh-out
   - (discovered: recipe-pitch-selection experiment, ingredient-claiming experiment, 2025-11-29/30)

6. [x] **Recipe identity validation**: Prevent pivot from breaking pitch promise
   - Essential: User picks "Beef Pot Roast", system delivers "Pork Butt Pot Roast" - broken trust
   - Need judge/validator to check if pivot is too different
   - Three boundaries: ingredients unavailable, effort significantly different, family expectations broken
   - (discovered: ingredient-claiming experiment, 2025-11-30)

7. [ ] **Recipe acceptance workflow** - Needs exploration of what "accept" means

### Nice to Have
- [x] **Week-level planning criteria**: Structured constraints for balanced variety
  - Example: "1 weekend meal, 1 guest meal (weeknight), 2 quick meals, 1 leftovers meal"
  - Different from ad-hoc context, helps generate balanced week
  - Evolved to: Structured meal planning workflow (specs upfront, systematic filling)
  - (discovered: recipe-pitch-selection experiment, ingredient-claiming experiment, 2025-11-29/30)

- [x] **Adaptive generation count**: Generate fewer pitches in subsequent waves
  - If already picked 3, don't need full 10 in next wave (just 2-3 more)
  - Efficiency + reduced cognitive load
  - Evolved to: 3x unfilled meal slots (need 2 meals → generate 6 pitches)
  - (discovered: recipe-pitch-selection experiment, ingredient-claiming experiment, 2025-11-29/30)

- [x] **Time diversity in pitches**: Mix quick weeknight + leisurely weekend
  - Not quite enough diversity yet in time commitments
  - Want both active AND total time visible
  - Future: Quadrant visualization (total vs passive time)
  - (discovered: recipe-pitch-selection experiment, 2025-11-29)

- [x] **Pitch disabling when ingredients claimed**: Visual conflict indication
  - Pitches using claimed ingredients should be grayed out/disabled
  - Better UX than status messages showing "avoiding X, Y, Z"
  - Reveals conflicts immediately, prevents impossible selections
  - (discovered: ingredient-claiming experiment, 2025-11-30)

- [x] **Grocery list view with optional ingredients**: Essential vs nice-to-have
  - Show what's required vs what would enhance meals
  - User decides which optional items to add to grocery run
  - Two sections: Essential (must buy), Optional (user choice)
  - (discovered: ingredient-claiming experiment, 2025-11-30)

- [x] **Recipe prioritization by uncommon ingredients**: Flesh out CSA items first
  - Prevents common ingredients getting claimed before exotic CSA produce
  - Nice to have, not blocking (auto-pivot works well enough)
  - (discovered: ingredient-claiming experiment, 2025-11-30)

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
