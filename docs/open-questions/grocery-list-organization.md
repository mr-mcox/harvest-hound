# Grocery List Organization

**Discovered**: store-based-claiming experiment, 2025-12-01
**Uncertainty**: Low
**Architectural Impact**: Low
**One-Way Door**: No

## The Question

How should grocery lists be organized for optimal shopping experience?

## Context

Current shopping list is flat: ingredient, quantity, recipes using it.

User suggestion: "LLM could further categorize likelihood of having items in pantry and/or organize grocery list by section of the store (produce, dairy, etc)."

Two organization axes emerged:
1. **By likelihood** - High confidence → Medium → Low (pantry assumptions)
2. **By store section** - Produce, dairy, meat, dry goods, etc.

## Current Behavior

Shopping list shows:
```
Grocery Store:
- 2 onions (used in: Recipe A, Recipe B)
- 8 oz goat cheese (used in: Recipe C)
- 1 bunch kale (used in: Recipe A)

Pantry (Verify):
- 2 cups arborio rice (for Recipe C)
- 1.5 cups polenta (for Recipe D)
```

No grouping within stores, no section organization.

## Options Considered

### Option 1: Likelihood-Based Sections
- Three sections: Definitely Buy → Verify → Assume Pantry
- Matches user mental model for shopping confidence
- **Pro**: Reduces noise (hide low-likelihood items), focuses on real needs
- **Con**: Doesn't help navigation in store

### Option 2: Store Section Categories
- Group by: Produce, Dairy, Meat, Bakery, Dry Goods, etc.
- Matches physical store layout
- **Pro**: Efficient shopping path, reduces backtracking
- **Con**: Store layouts vary, may not match user's store

### Option 3: Both - Likelihood + Sections
- Top level: Likelihood (Buy → Verify → Pantry)
- Within "Buy": Group by store section
- **Pro**: Both benefits - confidence filtering AND efficient navigation
- **Con**: More complex UI, may be over-organized

### Option 4: User-Configurable
- Default: Likelihood-based
- Option to switch view: By section, by likelihood, by recipe
- **Pro**: Flexibility for different use cases
- **Con**: UI complexity, mode switching friction

### Option 5: Smart Grouping Based on Store
- Costco → Bulk categories (frozen, dry bulk, fresh bulk)
- Cub Foods → Standard categories (produce, dairy, meat, etc.)
- Co-op → Specialty sections (local, organic, bulk bins)
- **Pro**: Store-appropriate organization
- **Con**: Requires store-specific configuration

## Architectural Implications

**Low impact** - Primarily UI/display concern

Data model:
- Optional: Add section field to ingredients (LLM-assigned or rule-based)
- Optional: Store section preferences (user-configured)

Prompt changes:
- Ask LLM to categorize ingredients by store section
- Example: "onion" → "produce", "goat cheese" → "dairy"

UI changes:
- Collapsible sections within shopping list
- View mode toggles (if Option 4)
- Store-specific layouts (if Option 5)

No database schema changes needed - can be pure display logic.

## Next Steps to Explore

1. **Test LLM categorization**: Can LLM reliably assign store sections?
2. **User store layout**: Does user's Cub Foods match standard grocery layout?
3. **Prototype Option 3**: Show likelihood + sections, test if it helps or clutters
4. **Shopping app integration**: Does user's shopping app already categorize? (duplicate effort?)
5. **Mobile vs desktop**: Organization more important on mobile during shopping?

## Related Discoveries

- Likelihood-based claiming (open-questions/likelihood-based-claiming.md) - Likelihood sections already planned
- Multiple grocery stores (open-questions/multiple-grocery-stores.md) - Different stores may need different organizations
- Ingredient structure (open-questions/ingredient-structure.md) - Clean ingredient names enable categorization

## Success Criteria

Solution works when:
- User can find items quickly in store (reduce search time)
- List matches shopping flow (produce first, frozen last, etc.)
- Organization feels natural, not forced
- Minimal configuration needed (works out-of-box)
- Copy-paste to shopping app still works cleanly

## Implementation Notes

Simple starting point (Option 1):
- High likelihood → "Shopping List"
- Medium likelihood → "Verify You Have"
- Low likelihood → Hidden or collapsed "Pantry Assumptions"

Future enhancement (Option 3):
- Add section grouping within "Shopping List"
- Use LLM or simple rules (onion → produce, milk → dairy)
- Collapsible sections for cleaner view
