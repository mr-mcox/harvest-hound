# Ingredient Claim Visibility

**Discovered**: recipe-persistence experiment, 2025-12-01
**Uncertainty**: Low (clear need, multiple UX approaches)
**Architectural Impact**: Low (data exists, needs view/query layer)
**One-Way Door**: No (can iterate on UX without changing data model)

## The Question

How should users see which ingredients are claimed by which recipes, and which ingredients remain available for the week?

## Context

User feedback after implementing persistent claims:
> "I think that we may want to be clearer on the ingredients list to understand 'why aren't I getting any recipes pitched for radishes...oh...I have a planned meal that I forgot about that reserved them'."

> "Which ingredients, which recipes <- yes. And also knowing what is claimed vs what's left. 'Oh - we aren't using the beets for anything this week? Maybe I'll roast them as a side'."

**Problem**: Claims work invisibly in background, but users need visibility to:
1. Understand why pitches avoid certain ingredients
2. Plan around unclaimed ingredients (roast beets as a side)
3. Identify meal planning gaps (beets going to waste)
4. Make informed decisions about recipe substitution/abandoning

## Use Cases

**UC1: Why no radish recipes?**
- User generates pitches, doesn't see radish options
- Wonders why (has radishes in inventory)
- Needs to see: "Radishes claimed by Honey-Butter Roasted Radishes (planned)"

**UC2: What's going unused?**
- User mid-week, reviewing planned meals
- Wants to identify ingredients not claimed by any recipe
- Needs quick scan: "Beets, turnips, kale unclaimed"
- Decision: Roast beets tonight as side dish

**UC3: Ingredient allocation across recipes**
- User has 2 lbs carrots, multiple recipes want them
- Needs to see: "Carrots: 1 lb claimed by Pot Roast, 0.5 lb claimed by Stir Fry, 0.5 lb available"
- Helps understand if there's enough for all planned recipes

## Options Considered

### Option A: Ingredient List View with Claims
Show inventory with claim information inline:
```
CSA Delivery:
  ✓ Radishes (2 bunches) - FULLY CLAIMED
     └─ Honey-Butter Roasted Radishes (1.5 bunches)
     └─ Quick Pickled Radishes (0.5 bunches)

  ⚠ Beets (3 medium) - UNCLAIMED

  ~ Carrots (2 lbs) - PARTIALLY CLAIMED (0.5 lb available)
     └─ Pot Roast (1 lb)
     └─ Stir Fry (0.5 lb)
```

**Pros**:
- Ingredient-centric view (natural for "what's in my CSA?")
- Clear visual status (fully/partially/unclaimed)
- Easy to spot waste opportunities

**Cons**:
- Redundant with "My Planned Recipes" section
- Requires separate UI component

### Option B: Recipe List with Claimed Ingredients
Show planned recipes with their claims:
```
My Planned Recipes:
  🥘 Honey-Butter Roasted Radishes
     Claims: 1.5 bunches radishes, 4 tbsp butter, 2 tbsp honey

  🍲 Pot Roast
     Claims: 1 lb carrots, 1 black radish, 3 lb beef roast
```

**Pros**:
- Recipe-centric (aligns with "My Planned Recipes" view)
- Already have this data structure
- Shows what each recipe needs

**Cons**:
- Harder to see what's unclaimed (need to cross-reference inventory)
- Doesn't answer "why no radish pitches?" directly

### Option C: Hybrid - Both Views with Toggle
Ingredient view + Recipe view, user switches between them:
```
[View: By Ingredient] [View: By Recipe]

When "By Ingredient":
  Shows Option A (ingredient list with claims)

When "By Recipe":
  Shows Option B (recipe list with claims)
```

**Pros**:
- Serves both use cases (ingredient planning, recipe management)
- User chooses their mental model

**Cons**:
- More UI complexity
- Potentially overkill for n=5-7 recipes per week

### Option D: Status Icons + Tooltips (Minimal)
Add status indicators to existing views:
```
Inventory:
  Radishes (2 bunches) 🔒  ← hover: "Claimed by 2 recipes"
  Beets (3 medium) ⚡      ← hover: "Unclaimed - use soon!"

Planned Recipes:
  Honey-Butter Roasted Radishes
  Claims: [click to expand ingredient list]
```

**Pros**:
- Minimal UI changes
- Progressive disclosure (hover/click for details)
- Works within existing layout

**Cons**:
- Less discoverable
- Requires interaction to see details

## Architectural Implications

**Data already exists**:
- `IngredientClaim` table tracks recipe_id → ingredient → quantity
- Can query in both directions:
  - Recipe → claims: `SELECT * FROM ingredient_claim WHERE recipe_id = ?`
  - Ingredient → recipes: `SELECT * FROM ingredient_claim WHERE ingredient_name = ?`

**No data model changes needed** - purely a view/query concern

**New endpoints might include**:
- `GET /api/inventory/claimed` - All ingredients with their claim status
- `GET /api/ingredients/{name}/claims` - Which recipes claim this ingredient
- Extend existing `/api/recipes/planned` to include claim details (already done)

## Latest Exploration - Table View Emerging

**Date**: 2025-12-01 (ingredient-priority experiment)

### User Feedback on Visibility Needs

User confirmed the need for claim visibility with specific requirements:

> "We're probably going to want a table treatment in the long run with the ability to change inventory, location, what's unclaimed, links to recipes that are claiming it."

**Current State**:
- Flat ingredient list with priority implemented (60% of actual inventory already feels long)
- Recipe list with claims exists in "My Planned Recipes" section
- But no way to see which ingredients are unclaimed or filter by claim status

**Emerging Solution: Option A Evolution → Inventory Management Table**

Combines ingredient-centric view with filtering and editing capabilities:

```
Columns:
- Ingredient name
- Quantity (editable inline)
- Location (e.g., chest freezer, refrigerator)
- Priority (editable inline via dropdown)
- Claims status (unclaimed / partially claimed / fully claimed)
- Recipe links (clickable to see which recipes claim it)

Filters:
- By location (for audit: "show chest freezer items")
- By claim status (unclaimed / claimed)
- By priority (urgent / high / medium / low)

Future enhancement:
- Sort by priority, color code rows by location
```

**Why Table View**:
- List is already long with 60% of inventory
- Need structured layout for multiple dimensions (quantity, location, priority, claims)
- Filtering essential for large inventories
- Bidirectional linking (ingredients ↔ recipes) fits table paradigm

**Implementation Note**: Post-prototype concern but validated as necessary direction

## Next Steps to Explore

1. ~~**Start with Option B** (Recipe list with claims) - already implemented in "My Planned Recipes"~~ ✅ DONE
2. ~~**Add unclaimed ingredient view** - simple list of ingredients with no claims~~ ❌ SKIP - table view more comprehensive
3. **Prototype table view** with key columns (ingredient, quantity, priority, claims)
4. **Add location filtering** for audit use case ("verify chest freezer")
5. **Add claim filtering** for planning use case ("what's unclaimed this week?")
6. **Test if table view is sufficient** for the week-by-week n=5-7 + full inventory management

## Related Questions

- **UI organization** (`ui-organization.md`) - Table view is a dedicated inventory management interface, separate from meal planning view
- **Week planning criteria** - Unclaimed ingredients could feed back into "generate side dishes" flow
- **store-claiming-semantics.md** - Location column in table aligns with location metadata direction
