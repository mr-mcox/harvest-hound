# Separate Ingredient and InventoryItem with Dynamic Ingredient Creation

## Context and Problem Statement

When users upload inventory ("2 lbs carrots, 1 bunch kale"), we need to decide how to model the relationship between ingredient concepts (what is a "carrot") and inventory quantities (how much carrots do I have). This affects data modeling, duplicate handling, unit management, and future recipe integration. The core question is: should ingredients be predefined entities or created dynamically from user input?

## Considered Options

* Inline ingredient data within InventoryItem (no separate Ingredient entity)
* Predefined ingredient catalog with matching/normalization on input
* Dynamic ingredient creation with separate Ingredient aggregate
* Hybrid approach with ingredient catalog fallback to dynamic creation

## Decision Outcome

Chosen option: "Dynamic ingredient creation with separate Ingredient aggregate", because it provides clean domain separation while avoiding premature complexity around ingredient catalogs and duplicate detection.

### Consequences

* Good, because ingredients become reusable entities that can later link to recipes
* Good, because domain model clearly separates "what is an ingredient" from "how much do I have"
* Good, because we avoid complex ingredient matching logic in MVP
* Good, because LLM can handle parsing variations without rigid schema constraints
* Bad, because duplicate ingredients will be created (e.g., "carrots" and "carrot")
* Bad, because no validation of ingredient names (could create "crrots" typo)
* Bad, because quantities stored as separate unit strings rather than normalized amounts

## Implementation Details

```python
class Ingredient:
    ingredient_id: UUID
    name: str           # "carrots" - exactly as parsed by LLM
    default_unit: str   # "lbs" - suggested unit for this ingredient

class InventoryItem:
    store_id: UUID
    ingredient_id: UUID  # Links to dynamically created Ingredient
    quantity: float      # 2.0
    unit: str           # "lbs" - actual unit for this inventory
```

**Happy Path Assumptions:**
- No duplicate ingredient detection (always create new Ingredient)
- No unit conversion (store exactly as parsed)
- LLM provides clean, consistent parsing

**Future Migration Path:**
- Add ingredient matching service for duplicate detection
- Implement unit conversion and normalization
- Build ingredient catalog with canonical names
- All existing data remains valid through aggregate IDs
