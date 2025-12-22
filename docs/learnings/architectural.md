# Architectural Learnings

_Architecture decisions, patterns to keep/change, and acceptable technical debt._

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
