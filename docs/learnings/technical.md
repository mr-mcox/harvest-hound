# Technical Learnings

_Validated discoveries about BAML prompts, API patterns, and performance._

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

