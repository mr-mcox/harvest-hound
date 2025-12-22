# Domain Model Learnings

_Validated discoveries about entities, boundaries, and modeling decisions._

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
  - **VALIDATED IN PRODUCTION**: First recipe cooked 2025-12-08, steel thread complete
  - (discovered: recipe-persistence experiment, 2025-12-01; validated: production use, 2025-12-08)

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

- [x] **Produce utilization validated**: System successfully minimizes CSA waste
  - User reaction after week 3: "Only rutabaga left from delivery that week"
  - Core loop works: Pick variety → get options → confident weekly meal plan
  - Variety + confidence = key value proposition validated
  - Steel thread complete: System used for actual weekly meal planning in production
  - (discovered: production use week 3, 2025-12-21)

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
  - **Production validation**: Recipe timing "pretty close" - time estimates are accurate enough for planning
  - (discovered: recipe-pitch-selection experiment, 2025-11-29; validated: production use, 2025-12-09)

- [x] **Recipe formatting affects cooking efficiency**: Instructions need better ergonomics
  - Production pain point: Flipping back and forth between recipe sections while cooking
  - Recipe format should minimize context switching during active cooking
  - Opportunity: Improve recipe instruction layout/formatting for cooking workflow
  - Not just about correctness - ergonomics matter for real use
  - (discovered: production use, 2025-12-09)

- [x] **Ingredient substitution preferences emerging**: User food preferences affect recipe selection
  - Example: "What if we could substitute dill because I really don't like dill"
  - Not just dietary restrictions - personal taste preferences matter
  - Different from recipe editing (which is "tweak this recipe") - this is "avoid X in all recipes"
  - Opportunity: Capture user ingredient preferences to guide generation
  - (discovered: production use, 2025-12-09)

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

- [x] **Priority system gap for pantry items**: Time-to-spoil model incomplete
  - Priority works great for CSA produce (freshness-based)
  - Fails for pantry items: dried beans, canned goods technically low-priority but user wants them used
  - User quote: "I don't want to artificially bump priority just to make it happen that week"
  - Desired behavior: Pair pantry items with high-priority CSA ingredients naturally
  - Gap reveals need for separate dimension: freshness vs. "want to use"
  - Current workaround: Manual priority bumping or criteria creation (both feel wrong)
  - (discovered: production use week 3, 2025-12-21)

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
  - **Production validation**: Pantry guesses not as accurate as expected - affects both grocery list ranking and recipe generation
  - **Feedback loop opportunity**: Grocery list selections could inform pantry definitions and improve ranking accuracy
  - (discovered: store-based-claiming experiment, 2025-12-01; validated: production use, 2025-12-09)

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

