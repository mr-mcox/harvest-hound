# Feature Frame: Admin/Config Interface

**Date**: 2025-12-05
**Status**: Aligned

---

## Problem Statement

Before the steel thread can run (CSA delivery → planning → shopping list → cook), foundational configuration needs to exist: household context for recipe generation, pantry assumptions, and grocery stores for shopping list claims. These are set-once-tweak-occasionally settings that shouldn't clutter the main workflow.

**From Prototype Discovery**:
- Household profile as prompt constant works ("in the ballpark")
- Store management used but infrequent - "could be buried in configuration interface"
- Multiple grocery stores needed (Costco, Cub, Co-op) for different shopping rhythms

---

## Domain Model Refinement

The prototype's "store" concept splits into three distinct, non-unified concepts:

| Concept | Type | Purpose |
|---------|------|---------|
| **Household Profile** | Singleton text | Baked into LLM prompts - family context, equipment, preferences |
| **Pantry** | Singleton text | What's assumed always available (unlimited, unclaimed) |
| **Grocery Stores** | Multiple (name + definition) | Where to buy things, enables shopping list claims |
| **Inventory** | Flat list | Finite items with inferred metadata (priority, location, portion) |

**Naming Decision**: These concepts don't need a unifying "store" name - they're less cohesive than originally anticipated:
- **Pantry** = what we assume exists (singleton definition)
- **Inventory** = what we actually have (flat list, claimable)
- **Grocery Stores** = where we shop (multiple, for list-building)

---

## User Stories

### Story 1: Configure Household Profile
**As a** meal planner
**I want** to set my household's cooking context once
**So that** recipe generation fits my family's needs without repeating myself

**Acceptance Criteria**:
- [ ] Can view current household profile text
- [ ] Can edit household profile as free-form text
- [ ] Changes persist across sessions
- [ ] Profile is used in recipe generation prompts

**From LEARNINGS.md**: "Household profile as prompt constant (no DB/UI complexity) - felt 'in the ballpark'"

### Story 2: Configure Pantry
**As a** meal planner
**I want** to define what pantry staples I assume are always available
**So that** recipes can use common ingredients without adding them to shopping lists

**Acceptance Criteria**:
- [ ] Can view current pantry definition
- [ ] Can edit pantry as free-form text
- [ ] Pantry is used in recipe generation (as unlimited, unclaimed)
- [ ] Pantry items don't appear on shopping lists

**From LEARNINGS.md**: "Definition stores - unlimited, never claimed"

### Story 3: Manage Grocery Stores
**As a** meal planner
**I want** to configure my grocery stores (Cub, Costco, Co-op, etc.)
**So that** shopping lists can be organized by where I shop

**Acceptance Criteria**:
- [ ] Can add a grocery store with name and description/definition
- [ ] Can edit existing grocery store
- [ ] Can delete a grocery store (if no active claims against it)
- [ ] At least one grocery store exists for recipe generation to assign ingredients

**From LEARNINGS.md**: "Multiple grocery stores, not singleton - 'Costco run this week'"

### Story 4: Remove Hello World Scaffolding
**As a** developer
**I want** to remove the placeholder dishes functionality
**So that** the codebase is clean for real features

**Acceptance Criteria**:
- [ ] `/api/dishes` endpoint removed
- [ ] `/api/dishes/stream` endpoint removed
- [ ] `dishes.baml` removed or repurposed
- [ ] Frontend dishes UI removed
- [ ] `/api/hello` health check retained (useful for stack verification)

---

## Prototype Contrast

| Aspect | Prototype | MVP | Why Change |
|--------|-----------|-----|------------|
| Household profile | Hardcoded in BAML | Editable in settings | Allow tweaking without code changes |
| Pantry | `Store` with `store_type="definition"` | Dedicated `Pantry` singleton | Simpler model, clearer naming |
| Explicit stores | Multiple `Store` entities with inventory | Flat `Inventory` list | "Got cumbersome really quick" |
| Grocery stores | Single "Cub foods" hardcoded | Configurable `GroceryStore` list | Real workflow needs Costco, Co-op, etc. |
| Locations | Not implemented | Inferred metadata on inventory items | LLM can guess (kale → refrigerator) |

**Preserve from Prototype**:
- Pantry text used for both "what's available" and "parsing context"
- Grocery store description passed to LLM for context

**Fix from Prototype**:
- Remove rigid store containers for explicit inventory
- Make grocery stores configurable instead of hardcoded

**Change from Prototype**:
- Location as inferred item metadata, not organizational container
- Clear naming: Pantry, Inventory, Grocery Stores (not all "stores")

---

## Out of Scope (Deferred)

Explicitly NOT part of this feature:
- **Location filtering/audit view**: Deferred - steel thread doesn't need "verify chest freezer inventory"
- **Portion hint management UI**: Deferred - inferred during parsing, no edit UI yet
- **Per-session grocery store selection**: Deferred - use all configured stores for MVP
- **Batch update locations**: Deferred - can add if location inference proves insufficient

**Future Features This Enables**:
- Inventory bulk add with parsing context ("these are all frozen meats")
- Shopping list grouped by grocery store
- Inventory audit by location

---

## Technical Notes

**Database Models Needed**:
```
HouseholdProfile (singleton)
  - id, content (text), updated_at

Pantry (singleton)
  - id, content (text), updated_at

GroceryStore
  - id, name, description (text), created_at
```

**Seeding**: On first run, seed a default grocery store (e.g., "Grocery Store" with generic description) to avoid "no stores configured" edge cases.

**BAML Changes**:
- Extract household profile from config instead of hardcoding
- Extract pantry from config
- Pass grocery store names to recipe generation for assignment

**API Endpoints**:
- `GET/PUT /api/config/household-profile`
- `GET/PUT /api/config/pantry`
- `GET/POST /api/config/grocery-stores`
- `GET/PUT/DELETE /api/config/grocery-stores/{id}`

**UI Approach**:
- Settings panel accessible from main page
- Route decision (`/settings` vs modal) is weak - can evolve
- Text areas for household profile and pantry
- Table/list for grocery stores with add/edit/delete

---

## Decisions Made

1. **Naming**: Drop unified "store" concept. Use Pantry, Inventory, Grocery Stores as distinct concepts.
2. **Default grocery store**: Seed one on first run with generic description.
3. **Admin UI**: Settings panel from main page (route TBD).
4. **Household profile**: Pure free-form text.
