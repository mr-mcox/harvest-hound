# Multiple Grocery Stores

**Discovered**: store-based-claiming experiment, 2025-12-01
**Uncertainty**: Low
**Architectural Impact**: Medium
**One-Way Door**: No

## The Question

How should the system handle multiple grocery stores with different shopping rhythms?

## Context

User shops at different stores for different purposes:
- **Cub Foods**: Regular weekly shopping
- **Costco**: Bulk runs (less frequent, specific items)
- **Co-op**: Specialty items, local produce
- **Asian grocery**: Specific ingredients for Asian recipes

Store availability varies by week:
- Some weeks: "Making a Costco run, can buy bulk items"
- Other weeks: "Just Cub Foods this week, avoid bulk-only items"

Current implementation assumes single "grocery store" concept - doesn't match reality.

## Current Behavior

- Pantry is definition store (unlimited staples)
- "Cub foods" is definition store (what's available at grocery)
- LLM assigns ingredients to stores during recipe generation
- No way to specify which stores are available this week

## Options Considered

### Option 1: All Stores Always Available
- List all grocery stores, assign ingredients to best-fit store
- User sees shopping list per store, chooses which stores to visit
- **Pro**: Simple, no configuration needed
- **Con**: May suggest Costco items when user can't make Costco run

### Option 2: Week-Level Store Selection
- User selects which stores are available for this week's planning
- LLM only assigns ingredients to available stores
- **Pro**: Matches user's shopping rhythm
- **Con**: Requires UI for store selection, state management

### Option 3: Store Priority/Fallback System
- User ranks stores: Cub (always) > Co-op (if needed) > Costco (bulk runs only)
- LLM assigns to preferred store, falls back to alternatives
- **Pro**: Smart defaults with flexibility
- **Con**: Complex rules, may not match week-to-week variance

### Option 4: Store Constraints Per Recipe
- When generating pitches, specify store constraints
- "Generate recipes using Cub Foods and Asian grocery only"
- **Pro**: Maximum control
- **Con**: Extra friction in workflow

### Option 5: Hybrid - Default + Override
- Default: All stores available
- Optional: Specify store constraints for week
- **Pro**: Works without config, supports power users
- **Con**: Two code paths to maintain

## Architectural Implications

**Medium impact** - Changes store model from singleton to collection

Data model:
- Multiple grocery definition stores (already supported technically)
- Store availability state (week-level configuration)
- Store preferences/priority (user settings)

Prompt changes:
- Pass only available stores to LLM during recipe generation
- Store context (bulk store vs regular) may influence recipes

UI changes:
- Store selection interface (weekly planning phase)
- Shopping list grouped by store
- Store-specific features (Costco → bulk quantities)

## Next Steps to Explore

1. **Validate assumption**: Do stores really vary week-to-week, or mostly stable?
2. **Test Option 1**: Implement all-stores-always, see if user naturally ignores certain stores
3. **Observe patterns**: Track which stores get assignments, whether mismatches occur
4. **Prototype Option 2**: Add simple "Available this week" checkboxes, test friction
5. **Store characteristics**: Do bulk stores (Costco) need different recipe generation logic?

## Related Discoveries

- Likelihood-based claiming (open-questions/likelihood-based-claiming.md) - Store assignment is part of likelihood judgment
- Pantry definition learning (open-questions/pantry-definition-learning.md) - Pantry vs which grocery store
- Grocery list organization (open-questions/grocery-list-organization.md) - List grouped by store

## Success Criteria

Solution works when:
- User can express shopping plans ("Costco run this week")
- Recipes don't require stores user won't visit
- Shopping list clearly shows which store for each item
- Flexibility for ad-hoc store visits ("Actually, I'll hit the Co-op")
- Minimal configuration burden (works well with zero config)
