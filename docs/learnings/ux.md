# UX Learnings

_Validated discoveries about UI/UX patterns and interaction design._

## UI/UX Discoveries

### Interaction Patterns That Work
- [x] **LLM-suggested priorities with manual adjustment**: AI + human collaboration
  - LLM provides smart defaults based on perishability
  - User adjusts when needed (but mostly accepts defaults)
  - Reduces data entry burden while maintaining control
  - Now realized on /inventory page (post-commit) and /inventory/import parse-results view (pre-commit)
  - (discovered: ingredient-priority experiment, 2025-12-01; import adjustment feature, 2025-07-25)

- [x] **Progressive disclosure for recipe context**: Hide details until needed
  - Shopping list shows "2 onions - used in: Recipe A, Recipe B"
  - Recipe context ("why am I buying this?") useful but optional
  - Could be hidden/collapsed, revealed on hover or click
  - Reduces visual noise while keeping sanity-check info accessible
  - (discovered: store-based-claiming experiment, 2025-12-01)

- [x] **Single-page prototype goes far**: One page with progressive disclosure may be sufficient
  - Surprising that we don't need complex navigation yet
  - (discovered: recipe-generation experiment, 2025-11-29)

- [x] **Ingredient source management**: Used but infrequent
  - Deleted duplicate source (one-time cleanup)
  - Edited Pantry Staples definition (refinement during setup)
  - Suggests: Could be buried in configuration interface long-term, doesn't need prominent UI
  - (discovered: inventory-management experiment, 2025-11-29)

### Interaction Patterns That Don't Work
- [x] **Cycling badge UX in long sorted list**: Item disappears when clicked
  - Problem: Clicking priority badge cycles it, item re-sorts to new position (jumps down list)
  - Confusing in long lists - user loses track of what they just changed
  - Better UX: Dropdown/menu that keeps item in place while changing priority
  - Or: Debounced re-sort so item stays visible briefly after change
  - Not an issue on the import parse-results view (no priority sort = items stay in parse order)
  - (discovered: ingredient-priority experiment, 2025-12-01; import adjustment feature, 2025-07-25)

### Emerging Needs
- [x] **Different views for different contexts**: Single page getting cluttered
  - Need planning view, cooking view, reviewing view as distinct modes
  - Compact recipe representation works for weekly hub
  - More detailed view needed for cooking
  - System needs thoughtful information architecture as features grow
  - (discovered: recipe-persistence experiment, 2025-12-01)

- [x] **Inventory management table view**: List gets long, needs structured management
  - Current: 60% of actual inventory already feels long
  - Need: Table with columns for ingredient, quantity (editable), location, priority, claims, links to recipes
  - Filtering by location for audit ("verify chest freezer inventory")
  - Filtering by claimed/unclaimed status
  - Post-prototype concern but emerging need is clear
  - Future idea: Sort by priority, color code by location
  - (discovered: ingredient-priority experiment, 2025-12-01) 

