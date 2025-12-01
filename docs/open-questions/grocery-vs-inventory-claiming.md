# Grocery vs Inventory Claiming Models

**Discovered**: ingredient-claiming experiment, 2025-11-30
**Priority**: Medium (future feature, architectural clarity needed)

## Problem

Current claiming model assumes all ingredients come from inventory (what you have). But recipes also need ingredients you DON'T have yet - groceries. Claiming a grocery store is fundamentally different from claiming inventory.

**Three ingredient sources discovered:**
1. **Inventory** (have it) - CSA produce, freezer meat, existing pantry
2. **Grocery Essential** (need it) - Required to make recipe, must buy
3. **Grocery Optional** (nice to have) - Would enhance meal (coleslaw, cheese, garnishes)

## Current State

**Inventory claiming (implemented)**:
- Reserve what you have
- Filter to trackable items (exclude pantry staples)
- Ephemeral claims during session
- Sequential flesh-out prevents conflicts

**Grocery claiming (not implemented)**:
- Need to BUY these ingredients
- Not reserving something you have
- Building a shopping list, not claiming inventory

## Questions

**How should grocery claiming work?**
- Is it even "claiming" or is it "list building"?
- Do essential grocery items block other recipes? (can two recipes use "cheddar cheese" from store?)
- Do optional grocery items accumulate across recipes?

**When do recipes suggest grocery items?**
- Only when inventory is insufficient?
- LLM decision: "I could use X from inventory OR suggest buying Y for better result"?
- User preference: minimize grocery trips vs optimize quality?

**How to display grocery list?**
- Single list for the week's meals?
- Grouped by recipe?
- Essential vs optional sections?
- Show which recipes need each item?

**Should grocery items be reservable?**
- Example: User accepts "Pasta Carbonara" → adds "pancetta" to grocery list
- Before shopping, they accept "Breakfast Hash" → also uses pancetta
- Both recipes share the grocery list item?
- Or each recipe has independent grocery needs?

**What about pantry staples?**
- Currently ignored for claiming (treated as unlimited)
- Should they appear in grocery list if truly out? ("buy more flour")
- How to model "need to restock" vs "always available"?

## Three Claiming Models

### Model 1: Separate Systems

**Inventory claiming:**
- Reserves what you have
- Prevents conflicts
- Ephemeral → persistent claims

**Grocery list building:**
- Accumulates needed items
- No reservation (you don't have them yet)
- Just a list to buy

**Pros**: Clear separation, simpler logic
**Cons**: Recipes span both systems, user sees fragmentation

### Model 2: Unified Ingredient Sources

**All ingredients have a source:**
- Source: Inventory (have it, can claim)
- Source: Grocery (need to buy, add to list)
- Source: Optional (nice to have, user decides)

**Single "ingredient requirement" concept:**
- Recipe requires "2 lbs carrots"
- System checks: Do we have them? → Claim from inventory
- System checks: Don't have them → Add to grocery list (essential)
- System suggests: "coleslaw mix would be nice" → Add to grocery list (optional)

**Pros**: Unified view, recipes don't care about source
**Cons**: More complex claiming logic, mixing reservation and list-building

### Model 3: Two-Phase Claiming

**Phase 1: Recipe selection (current)**
- Flesh out with inventory only
- Claim inventory ingredients

**Phase 2: Grocery enhancement**
- After acceptance, show "missing ingredients"
- User reviews: Essential (must buy) vs Optional (nice to have)
- Builds grocery list from accepted recipes

**Pros**: Separates concerns, user makes conscious decisions
**Cons**: Two-step process, may feel like extra work

## Hypothesis

**Model 2 seems most aligned with user workflow:**
- Recipe generation considers ALL ingredient sources
- System determines: use from inventory, buy essential, suggest optional
- Grocery list is a projection of "what to buy" from accepted recipes
- User makes final call on optional items

**Implementation sketch:**
```
IngredientRequirement {
  name: string
  quantity: float
  unit: string
  source: "inventory" | "grocery_essential" | "grocery_optional"
  source_detail: string? // which inventory item or why needed
}
```

## Edge Cases to Explore

- Recipe needs 2 lbs carrots, have 1 lb → split between inventory and grocery?
- Optional ingredient appears in multiple recipes → consolidate on grocery list?
- User shops and adds groceries to inventory → update recipe sources?
- Ingredient expires before cooking → swap back to grocery list?

## Success Criteria

- Recipes can use both inventory and grocery ingredients naturally
- Grocery list is useful (shows essentials + optionals, grouped sensibly)
- User can review and modify grocery list before shopping
- No duplicate/conflicting grocery items across recipes

## Next Experiment

Not blocking for current phase. Revisit when implementing:
1. Meal plan acceptance workflow
2. Grocery list view
3. Multi-week planning (when grocery restocking becomes important)
