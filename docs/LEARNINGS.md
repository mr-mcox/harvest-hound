# Prototype Learnings

## Date Started: 2025-11-29

## Domain Model Discoveries

### Core Concepts
- [x] **Household Profile**: Can be baked into prompt, doesn't need database/UI complexity (at least for single-user)
  - Family context, equipment, preferences stored as prompt constants
  - Felt "in the ballpark" - may need prompt tweaking but approach is sound
  - (discovered: recipe-generation experiment, 2025-11-29)

- [x] **Ingredient source concept**: All ingredient sources auto-included for recipe generation feels right
  - Don't need per-generation ingredient source selection
  - Could potentially prioritize via context ("ingredients going bad") but not blocking
  - (discovered: recipe-generation experiment, 2025-11-29)

- [x] **Portioning constraints discovered**: Inventory has discrete vs infinitely divisible items
  - Freezer meat: 2 lbs = 2 separate 1-lb packages (can't use 1.5 lbs)
  - Vegetables: 2 lbs carrots = bulk (can use any amount)
  - Low confidence if worth modeling explicitly - could be ingredient-level context
  - Affects: recipe generation (what amounts to suggest), inventory editing (increment/decrement UX)
  - (discovered: inventory-management experiment, 2025-11-29)

- [x] **Ingredient source definitions dual-purpose**: What belongs + parsing context
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
  - Grocery source claiming is fundamentally different - it's list-building, not reservation
  - (discovered: ingredient-claiming experiment, 2025-11-30)

- [x] **Pantry Staples vs inventory items**: Only claim trackable inventory
  - Problem: Was claiming "baking powder", "garlic powder" - Pantry Staples shouldn't block future recipes
  - Solution: Filter claimed ingredients to only items in inventory system
  - Pantry Staples are effectively unlimited, don't need claiming
  - (discovered: ingredient-claiming experiment, 2025-11-30)

- [x] **Ingredient source type separation validated**: Inventory vs Pantry Staples works architecturally
  - Inventory sources: Itemized with quantities, need claiming
  - Pantry Staples source: Unlimited, never claimed
  - LLM receives them separately in prompt, understands the distinction
  - Code manages decremented inventory state for Inventory sources only
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

- [x] **Recipe lifecycle states**: Planned → Cooked/Abandoned works well
  - Three states sufficient: planned (reserved), cooked (consumed), abandoned (released)
  - Auto-save on flesh-out feels natural (no "don't save" needed since abandon is low effort)
  - Models how user wants to use system: plan for week → cook or abandon as week progresses
  - User reaction: "That model seemed to work quite well"
  - (discovered: recipe-persistence experiment, 2025-12-01)

- [x] **IngredientClaim as persistent entity**: Works invisibly in background
  - Two claim states: reserved (planned), consumed (cooked)
  - Claims work transparently - user doesn't think about them, they just work
  - Distinction could be clearer in UI ("why aren't I getting radish recipes? oh, forgot about that planned meal")
  - Physical vs available inventory distinction validated
  - (discovered: recipe-persistence experiment, 2025-12-01)

- [x] **Recipe persistence transforms system feel**: From session tool to weekly hub
  - Page refresh with recipes persisted changes entire experience
  - User reaction: "Now feeling like a central hub to keep coming back to over the course of a week, feels a lot more authentic"
  - Validates hypothesis: persistence eliminates planning work loss frustration
  - Critical bug: Pitches must respect saved recipe claims to prevent double-booking ingredients
  - (discovered: recipe-persistence experiment, 2025-12-01)

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

- [x] **Pitch as projection, not entity**: Architectural clarity achieved
  - Pitch = ephemeral view/projection of recipe concept (not separate entity)
  - Recipe = aggregate root (canonical, reusable, long-lived)
  - Multiple pitches can point to same underlying recipe (session-scoped, disposable)
  - Don't need lineage tracking (pitch → recipe history)
  - Bidirectional promise-keeping: pitch→recipe AND recipe→pitch must be faithful
  - (discovered: pitch-recipe-identity experiment, 2025-12-02)

- [x] **Functional fidelity > character preservation**: What matters in recipe generation
  - Technique fidelity is CRITICAL: "flip every 4-7 minutes" vs "move around with tongs" = broken dish
  - Example: Spaghetti All'Assassina requires specific flipping technique for crispy bottom
  - Character/tone preservation doesn't matter (style can adapt)
  - Contextual adaptations are FEATURES not bugs:
    - Kid-friendly modifications (less spicy, familiar flavors)
    - Pantry substitutions (dried herbs instead of fresh)
    - These improve usability, don't break recipe identity
  - Judge dimensions that matter: ingredient compatibility, technique preservation, effort alignment
  - Judge dimensions that don't: character, writing style, tone
  - (discovered: pitch-recipe-identity experiment, 2025-12-02)

- [x] **POINTER vs GENERATIVE pitches**: Two distinct patterns (deferred for MVP)
  - POINTER pitches: Reference existing canonical recipe (NYT clip → should return original)
  - GENERATIVE pitches: Novel recipe creation from inventory
  - Different handling: POINTER returns stored recipe, GENERATIVE creates new
  - For MVP: Skip POINTER entirely (clipped recipes + mixed workflow too complex for prototype)
  - For MVP: Only GENERATIVE pitches from inventory
  - (discovered: pitch-recipe-identity experiment, 2025-12-02)

- [x] **Recipes exist independently of ingredient source assignments**: Architectural principle validated
  - Ingredient source assignment is PLANNING-TIME context, not storage-time intrinsic property
  - Recipe concept: "Kimchi Carbonara needs butter and kimchi" (no ingredient sources mentioned)
  - Planning context: "I'll get butter from my cupboard, kimchi from fridge" (or "buy from Cub")
  - Applies to BOTH generative and canonical recipes:
    - Generative: LLM assigns ingredient sources during generation (current MVP flow)
    - Canonical: System assigns ingredient sources when recipe selected for planning (future)
  - Both create `IngredientClaim` at planning time, different resolution mechanisms
  - Enables recipe reusability across different inventory states
  - Enables recipe library import without pre-computing ingredient source assignments
  - Ingredient source assignment changes with context: staples restocked, grocery sources available this week
  - **Architectural win**: Can add canonical recipe library without breaking current model
  - (discovered: recipe-context-sources architectural pressure test, 2025-12-02)

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

- [x] **Location for inventory organization**: Physical storage location as metadata
  - Location is organizational metadata (chest freezer, refrigerator, cellar, shelves)
  - User didn't need explicit inventory grouping (auto-created "My Inventory" worked invisibly)
  - Location matters for audit/review ("verify chest freezer has all our meat")
  - Location does NOT drive recipe generation - priority does
  - LLM can guess location during parsing (frozen meat → chest freezer, bacon → refrigerator)
  - User reaction: "The store concept fades away"
  - Note: This is distinct from architectural "ingredient sources" (Inventory, Pantry Staples, Grocery)
  - (discovered: ingredient-priority experiment, 2025-12-01)

- [x] **Priority drives recipe importance**: Location informs priority, priority drives recipes
  - Priority values: low (staples-level), medium (normal), high (use soon), urgent (spoiling)
  - Location explains WHY something has a priority: frozen meat → low, fridge bacon → high
  - Priority visible in UI, location is background metadata explaining the rating
  - Normal distribution is healthy (lots in medium is expected and good)
  - Low priority barely above Pantry Staples (not worth tracking oats, flour, etc.)
  - User reaction: "Makes a lot of sense"
  - (discovered: ingredient-priority experiment, 2025-12-01)

- [x] **Ingredient dimensions are orthogonal**: Priority, location, optionality are independent
  - Priority: How urgently should this be used (meal planning priority)
  - Location: Where is it stored (audit/organization)
  - Optionality: Is it required for recipe (not yet implemented)
  - Each dimension serves different purpose, don't conflate them
  - Validates separation of concerns in ingredient metadata
  - (discovered: ingredient-priority experiment, 2025-12-01)

- [x] **Complete ingredient claiming is critical**: EVERY ingredient must be claimed against an ingredient source
  - Discovery: Initial implementation only claimed inventory items, grocery items disappeared
  - Problem: Beet risotto needed goat cheese, but no claim created → shopping list empty
  - Solution: LLM assigns every ingredient to an ingredient source (Inventory, Pantry Staples, or Grocery)
  - Enables complete shopping list generation and Pantry Staples verification
  - User reaction: "That's insufficient for this use case" (before fix)
  - (discovered: store-based-claiming experiment, 2025-12-01)

- [x] **Pantry Staples definition emerges from LLM behavior**: System reveals assumptions
  - LLM assigned honey, walnuts, onion to Grocery source
  - User considers these Pantry Staples (always have on hand)
  - Gap reveals Pantry Staples definition is fuzzy, user-specific
  - Opportunity: Use Grocery assignments to refine Pantry Staples definition over time
  - Question: How does system learn what user considers Pantry Staples?
  - (discovered: store-based-claiming experiment, 2025-12-01)

- [x] **Multiple grocery sources, not singleton**: Different grocery stores for different rhythms
  - Not "the grocery store" but: Cub (regular), Costco (bulk runs), Co-op, Asian grocery
  - Grocery source availability varies by week rhythm ("making a Costco run this week")
  - User may select which grocery sources are available for meal planning
  - Changes architecture: Grocery not a single source, but multiple shopping options
  - (discovered: store-based-claiming experiment, 2025-12-01)

- [x] **Three-tier ingredient source architecture**: Inventory, Pantry Staples (singleton), Grocery (multiple)
  - Inventory: Itemized ingredients we definitely have (CSA, freezer items, tracked ingredients)
  - Pantry Staples (singleton): Assumed staples like salt, oil, common spices - verify before cooking
  - Grocery (multiple sources): Where we buy things, user selects available stores (Cub, Costco, Co-op, etc.)
  - Claiming logic: If explicitly in Inventory → claim it. If not → judge likelihood of needing to buy.
  - Replaces rigid Grocery/Pantry Staples split with flexible judgment
  - (discovered: store-based-claiming experiment, 2025-12-01)

- [x] **Likelihood-based ingredient sourcing**: Replace binary Grocery/Pantry Staples with probability
  - Instead of "is this Pantry Staples or Grocery?", ask "how likely do we need to buy this?"
  - High likelihood: Definitely buy (unusual items, large quantities)
  - Medium likelihood: Review/verify (grey area for user decision)
  - Low likelihood: Assume Pantry Staples (salt, common spices under threshold)
  - Enables smarter grocery list ordering (high confidence items first)
  - Example: "2.5 tsp salt" = silly to verify, but "8 oz goat cheese" = need to buy
  - (discovered: store-based-claiming experiment, 2025-12-01)

- [ ] Ingredient complexity level:

### Workflows That Feel Natural
1. [x] **Zero-click recipe generation**: Auto-loading all ingredient sources, optional context field
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

9. [x] **Recipe persistence workflow**: Auto-save on flesh-out → cook/abandon lifecycle
   - Fleshing out automatically saves recipe to "My Planned Recipes" (no separate accept step)
   - Planned recipes visible at top of page (compact view) as weekly hub
   - Cook action: consumes claims, decrements inventory, marks recipe complete
   - Abandon action: releases claims without consuming inventory, marks recipe abandoned
   - Low-friction abandoning makes auto-save acceptable (no "don't save this" needed)
   - Page becomes central hub to return to throughout week
   - User reaction: "Feels a lot more authentic"
   - (discovered: recipe-persistence experiment, 2025-12-01)

10. [x] **Flat ingredient view with priority**: Single list sorted by priority
    - Reduces cognitive load vs store-centric organization
    - User doesn't think about "which store?" when adding ingredients
    - Auto-creates default store invisibly when needed
    - Priority sorting surfaces urgent items at top
    - User reaction: "Reduced cognitive load and number of steps"
    - (discovered: ingredient-priority experiment, 2025-12-01)

11. [x] **LLM-suggested priorities mostly right**: AI guesses are accurate
    - LLM considers perishability when suggesting priority (frozen → low, fridge → high)
    - Mostly accepts suggested priorities without adjustment
    - Normal distribution (lots in medium) is healthy, not a problem
    - Validates AI-assisted data entry approach
    - (discovered: ingredient-priority experiment, 2025-12-01)

12. [x] **Shopping list view fills workflow gap**: Planning → Shop → Cook flow complete
    - Shopping list aggregates claims by ingredient source (Grocery vs Pantry Staples)
    - Format: "2 onions - used in: Recipe A, Recipe B"
    - Copy-paste button for transferring to shopping app
    - Pantry Staples verification checklist ("Check you have 2c polenta for Recipe X")
    - User reaction: "This works great"
    - Fills missing step between meal planning and actual shopping
    - (discovered: store-based-claiming experiment, 2025-12-01)

### Surprising Complexities
- [x] **Ingredient representation mixes shopping and preparation**: Blurry boundary
  - Problem: Shopping list shows "0.75 cup walnuts, roughly chopped"
  - User doesn't buy pre-chopped walnuts - preparation instruction leaked into ingredient
  - Reveals question: What fields are part of an ingredient?
  - Shopping needs: "walnuts" (the thing to buy)
  - Recipe needs: "walnuts, roughly chopped" (how to prepare)
  - May need separation: ingredient base + preparation modifier
  - (discovered: store-based-claiming experiment, 2025-12-01)

### Things Simpler Than Expected
- [x] **Single-page prototype goes far**: One page with progressive disclosure may be sufficient
  - Surprising that we don't need complex navigation yet
  - (discovered: recipe-generation experiment, 2025-11-29)

- [x] **Ingredient source management**: Used but infrequent
  - Deleted duplicate source (one-time cleanup)
  - Edited Pantry Staples definition (refinement during setup)
  - Suggests: Could be buried in configuration interface long-term, doesn't need prominent UI
  - (discovered: inventory-management experiment, 2025-11-29)

## Technical Discoveries

### BAML Prompts That Work
- [x] **Recipe generation with household profile**: Baked-in context approach works
  - Template: household profile + inventory + optional context + anti-duplicate tracking
  - Sequential generation (one at a time) prevents duplicates
  - Sonnet 4.5 with extended thinking (2000 token budget): Quality matches prior Claude system
  - Inference problem solved with explicit "only use available ingredients" constraint
  - (discovered: recipe-generation experiment, inventory-management experiment, 2025-11-29)

- [x] **Ingredient parsing with inventory context**: BAML ExtractIngredients + optional context
  - Handles "xN notation" (Butt Roast x3 → 3 roasts, not 3 pounds)
  - Context influences parsing (e.g., "Freezer meat. Portions are typically 1 lb")
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

- [x] **Round-trip fidelity testing**: Recipe→Pitch→Recipe validates technique preservation
  - Approach: Take human-crafted recipe → generate pitch → flesh out → judge fidelity
  - Test corpus: 4 characterful recipes (Kimchi Carbonara, Spaghetti All'Assassina, Chicken Yassa, Haluski)
  - Results: 69.5% overall fidelity (medium-low)
    - Ingredient: 66.75%, Effort: 85.25%, Experience: 71%, Character: 50.5%
  - Key finding: Technique drift breaks recipes (flip vs toss = different dish)
  - Validated: Can measure fidelity, but character scoring was wrong dimension
  - Experiment sufficient for architectural clarity, not worth implementing for prototype
  - (discovered: pitch-recipe-identity experiment, 2025-12-02)

### API Shapes That Feel Right
- [x] **GET endpoint with query params for SSE**: EventSource compatibility matters
  - POST with request body doesn't work with EventSource
  - Query params for simple inputs (context, num_recipes) feels clean
  - (discovered: recipe-generation experiment, 2025-11-29)

- [x] **Claims aggregation endpoint**: GET /api/claims/by-source
  - Groups claims by ingredient source, aggregates quantities across recipes
  - Returns: {source_name: {ingredients: {name: {total_qty, unit, recipes[]}}}}
  - Enables shopping list view and Pantry Staples verification
  - Structure supports multiple grocery sources (not just singleton)
  - (discovered: store-based-claiming experiment, 2025-12-01)

- [x] **Bulk operations via single endpoint**: POST /inventory/bulk
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

7. [x] **Ingredient claim visibility**: Need to see what's claimed vs available
   - Essential: "Why aren't I getting radish recipes? Oh, forgot about that planned meal that claimed them"
   - Need bidirectional lookup: which recipes → which ingredients, which ingredients → which recipes
   - Week-level view: "Oh we aren't using beets for anything this week? Maybe I'll roast them as a side"
   - Helps prevent ingredient waste and reveals meal planning gaps
   - Week-by-week operation means n is small, so detailed tracking is feasible
   - (discovered: recipe-persistence experiment, 2025-12-01)

8. [x] **Recipe editing/tweaking after planning**: Substitute ingredients in saved recipes
   - Nice to have: "I planned this earlier but now want to substitute Y ingredient"
   - Feedback option: "That's close, but please do X" to refine recipe
   - Not blocking for MVP, abandoning is low-effort workaround
   - (discovered: recipe-persistence experiment, 2025-12-01)

9. [x] **Shopping list generation from claims**: Aggregated view by store
   - Essential: Can't go shopping without knowing what to buy
   - Validated: Fills workflow gap (plan → shop → cook)
   - Format works: "2 onions - used in: Recipe A, Recipe B"
   - Copy-paste to shopping app successful
   - Pantry verification checklist reduces anxiety
   - User reaction: "This works great"
   - (discovered: store-based-claiming experiment, 2025-12-01)

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

- [x] **Bulk operations on recipes**: Week-by-week n is small enough
  - No need for "abandon all", "reorder", or other batch operations
  - Individual recipe management sufficient for 5-7 planned recipes per week
  - (discovered: recipe-persistence experiment, 2025-12-01)

- [x] **POINTER vs GENERATIVE pitch distinction**: Too complex for prototype/MVP
  - Mixed workflow (clipped recipes + generated recipes) is overengineered
  - Clipped recipe storage and retrieval adds complexity without validating core hypothesis
  - MVP: Focus only on GENERATIVE pitches from inventory
  - Post-MVP consideration: Recipe library + reuse workflow could be valuable later
  - (discovered: pitch-recipe-identity experiment, 2025-12-02)

- [x] **Character preservation in fidelity**: Doesn't matter for recipe quality
  - Character/tone/writing style can adapt freely
  - User cares about functional fidelity (will recipe work?), not prose quality
  - Kid-friendly adaptations and pantry substitutions improve usability
  - Technique preservation is what matters, not character consistency
  - (discovered: pitch-recipe-identity experiment, 2025-12-02)

## UI/UX Discoveries

### Interaction Patterns That Work
- [x] **LLM-suggested priorities with manual adjustment**: AI + human collaboration
  - LLM provides smart defaults based on perishability
  - User adjusts when needed (but mostly accepts defaults)
  - Reduces data entry burden while maintaining control
  - (discovered: ingredient-priority experiment, 2025-12-01)

- [x] **Progressive disclosure for recipe context**: Hide details until needed
  - Shopping list shows "2 onions - used in: Recipe A, Recipe B"
  - Recipe context ("why am I buying this?") useful but optional
  - Could be hidden/collapsed, revealed on hover or click
  - Reduces visual noise while keeping sanity-check info accessible
  - (discovered: store-based-claiming experiment, 2025-12-01)

### Interaction Patterns That Don't Work
- [x] **Cycling badge UX in long sorted list**: Item disappears when clicked
  - Problem: Clicking priority badge cycles it, item re-sorts to new position (jumps down list)
  - Confusing in long lists - user loses track of what they just changed
  - Better UX: Dropdown/menu that keeps item in place while changing priority
  - Or: Debounced re-sort so item stays visible briefly after change
  - (discovered: ingredient-priority experiment, 2025-12-01)

### Emerging Needs
- [x] **Different views for different contexts**: Single page getting cluttered
  - Need planning view, cooking view, reviewing view as distinct modes
  - Compact recipe representation works for weekly hub
  - More detailed view needed for cooking
  - System needs thoughtful information architecture as features grow
  - (discovered: recipe-persistence experiment, 2025-12-01)

- [x] **Inventory management table view**: List gets long, needs structured management
  - Current: 60% of actual inventory already feels long
  - Need: Table with columns for ingredient, quantity (editable), location, priority, claims, links to recipes
  - Filtering by location for audit ("verify chest freezer inventory")
  - Filtering by claimed/unclaimed status
  - Post-prototype concern but emerging need is clear
  - Future idea: Sort by priority, color code by location
  - (discovered: ingredient-priority experiment, 2025-12-01) 

## Architecture Decisions for MVP

### Keep Simple
- [x] **Recipes as reusable entities, ingredient sources as planning context**
  - Recipe schema: ingredients without ingredient source assignments
  - Ingredient source resolution happens at planning time (when recipe selected)
  - Don't conflate recipe identity with ephemeral planning context
  - Temporal separation: recipe persists (long-lived), ingredient source assignments are session/week scoped
  - **Key insight**: In prototype, BAML generation and ingredient source assignment happen together (efficient), but they're separate CONCEPTS that shouldn't be architecturally coupled
  - Enables future: import recipes, reuse across different inventory states, regenerate with different ingredient sources
  - (discovered: recipe-context-sources architectural pressure test, 2025-12-02)

### Still Don't Need
- [x] **Recipe library / canonical recipes**: Defer to post-MVP
  - Architectural pressure test passed: no constraints created by deferring
  - Store assignment independence enables clean addition later
  - For MVP: generative recipes only
  - (discovered: recipe-context-sources architectural pressure test, 2025-12-02)

- [x] **Session-scoped recipes for MVP with canonical migration path**
  - Recipe has session_id (session-specific for now)
  - Recipe.ingredients stored WITHOUT source assignments (canonical-ready)
  - Enables clean future migration: Add CanonicalRecipe table, rename Recipe → PlannedRecipe, backfill
  - "Favorite" curation before canonicalization: Only recipes user wants to make again become canonical
  - Doesn't paint into architectural corner while keeping MVP simple
  - (discovered: pitch-selection-claims alignment, 2025-12-07)

- [x] **IngredientClaim only for inventory items**
  - Claims are quantity-tracked reservations against specific inventory items
  - Only create claims for ingredients matching inventory (not grocery/pantry)
  - IngredientClaim schema: recipe_id, inventory_item_id (FK), ingredient_name, quantity, unit, state
  - Grocery/pantry likelihood deferred to shopping list feature (separate TIP)
  - Simplifies claiming logic: exact match inventory → create claim, else skip
  - (discovered: pitch-selection-claims alignment, 2025-12-07)

- [x] **Decremented inventory pattern for multi-wave generation**
  - Pass decremented inventory state to BAML (physical minus reserved claims)
  - Remove "DO NOT use these ingredients" constraint (unnecessary, LLM pivots naturally)
  - Prototype already implements this correctly in load_available_inventory()
  - Simpler and more reliable than exclusion lists
  - (discovered: pitch-selection-claims alignment, 2025-12-07)

### Consider Adding
- [ ]

## Next Steps
- [ ] Domain model sketch for MVP
- [ ] Priority features for implementation
- [ ] Technical debt worth taking
