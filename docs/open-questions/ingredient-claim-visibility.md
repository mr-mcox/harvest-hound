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

## Next Steps to Explore

1. **Start with Option B** (Recipe list with claims) - already implemented in "My Planned Recipes"
2. **Add unclaimed ingredient view** - simple list of ingredients with no claims
3. **Test if that's sufficient** for the week-by-week n=5-7 use case
4. **Iterate to Option A or D** if users need more granular ingredient visibility

## Related Questions

- **UI organization** (`ui-organization.md`) - This ties into broader view management needs
- **Week planning criteria** - Unclaimed ingredients could feed back into "generate side dishes" flow
