# Ingredient Structure: Shopping vs Preparation

**Discovered**: store-based-claiming experiment, 2025-12-01
**Uncertainty**: High
**Architectural Impact**: Medium
**One-Way Door**: Partial (affects data model but can evolve)

## The Question

What fields are part of an "ingredient"? Where does shopping need end and recipe preparation begin?

## Context

Shopping list currently shows: "0.75 cup walnuts, roughly chopped"

Problem: User doesn't buy pre-chopped walnuts. The preparation instruction ("roughly chopped") leaked into the ingredient representation, making the shopping list less useful.

This reveals a blurry boundary:
- **Shopping needs**: "walnuts" (the thing to buy)
- **Recipe needs**: "walnuts, roughly chopped" (how to prepare for cooking)

## Current Behavior

LLM generates ingredients as single strings with preparation mixed in:
- "2 tablespoon butter"
- "1 medium shallot or yellow onion (finely diced)"
- "4 ounce goat cheese (crumbled)"
- "0.5 cup parmesan cheese (grated)"

Shopping list displays these verbatim, including preparation instructions.

## Options Considered

### Option 1: Keep Current Structure, Strip Preparation in UI
- Ingredient remains single string
- Shopping list view strips parenthetical and comma-separated preparation
- Regex or LLM parsing: "walnuts, roughly chopped" → "walnuts"
- **Pro**: No schema change, simple fix
- **Con**: Fragile parsing, may strip important info

### Option 2: Separate Fields: Base + Preparation
- Schema: `{base: "walnuts", preparation: "roughly chopped", quantity: 0.75, unit: "cup"}`
- Shopping list shows base only
- Recipe view shows full preparation
- **Pro**: Clean separation, flexible display
- **Con**: LLM must output structured format, more complex schema

### Option 3: Structured Ingredient Class with Optional Modifiers
- Schema: `{name: "walnuts", quantity: 0.75, unit: "cup", preparation: ["roughly chopped"], notes: null}`
- Preparation is array (could have multiple: "peeled, diced, roasted")
- **Pro**: Most flexible, handles complex cases
- **Con**: Highest complexity, may be over-engineered

### Option 4: Context-Aware Display (Current Structure)
- Keep single string, but display differently in different contexts
- Shopping view: LLM extracts base ingredient
- Recipe view: Show full string with preparation
- **Pro**: Flexible without schema change
- **Con**: Two LLM calls (generate + extract), potential inconsistency

## Architectural Implications

**Medium impact** - Affects how ingredients are represented throughout system

Data model changes:
- RecipeIngredient schema (BAML)
- Database storage (ingredients_json field)
- IngredientClaim table structure

Prompt changes:
- Recipe generation prompt structure
- Ingredient parsing expectations

UI changes:
- Shopping list rendering
- Recipe detail rendering
- Inventory item matching

## Next Steps to Explore

1. **Analyze ingredient corpus**: Review existing recipes, categorize preparation patterns
2. **Test Option 1**: Implement simple stripping logic, see if it handles 80% of cases
3. **Prototype Option 2**: Try structured schema in BAML, see if LLM complies
4. **User validation**: Show user both approaches, which feels more useful?
5. **Edge case collection**: "boneless skinless chicken breast" - is "boneless skinless" preparation or base?

## Related Discoveries

- Grocery list organization (open-questions/grocery-list-organization.md) - Clean ingredient names help categorization
- Likelihood-based claiming (open-questions/likelihood-based-claiming.md) - Need clean ingredient matching for probability judgment

## Success Criteria

Solution works when:
- Shopping list shows buyable items (no preparation instructions)
- Recipe view shows complete cooking instructions
- Ingredient matching works (walnuts in pantry matches "walnuts, chopped" in recipe)
- LLM generates ingredients reliably in expected format
