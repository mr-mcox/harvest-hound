---
status: "proposed"
date: 2025-01-02
---

# Lazy Ingredient Normalization During Recipe Materialization

## Context and Problem Statement

Recipe ingredients come from various sources in different formats ("2 lbs carrots", "32 oz carrots", "carrot - 2 pounds"). The IngredientBroker needs to negotiate ingredient availability across stores, requiring consistent ingredient names and unit representations. We need to decide where and when to normalize ingredient names and quantities to enable accurate availability matching while preserving recipe authenticity and enabling context-aware normalization.

Key question: Should normalization happen at recipe storage, during broker negotiation, or when recipes are materialized for meal planning?

## Decision Drivers

* **Recipe authenticity** - Preserve original recipe formats for user experience
* **Context-aware normalization** - Leverage current inventory knowledge for better matching
* **Separation of responsibilities** - Clear ownership of normalization vs availability logic
* **Performance** - Normalize only when needed for active planning
* **Flexibility** - Enable normalization improvements without recipe data migration
* **User experience** - Show original recipes while enabling clean internal operations
* **System maintainability** - Minimize complexity in critical negotiation paths

## Considered Options

* **Recipe-level normalization at intake** - Normalize when recipes are stored, lose original format
* **IngredientBroker-level normalization** - Broker handles normalization during negotiation
* **Lazy normalization during materialization** - Normalize when recipe is used in meal planning
* **Recipe conforms to ingredient catalog** - Require predefined ingredient formats

## Decision Outcome

Chosen option: **"Lazy normalization during materialization"**, because it preserves recipe authenticity while enabling context-aware normalization with current inventory knowledge, provides clean separation between recipe storage and planning operations, and allows normalization logic to evolve independently.

### Consequences

* Good, because original recipe formats are preserved for authentic user experience
* Good, because normalization occurs with full inventory context, improving accuracy
* Good, because normalization overhead only occurs during active meal planning
* Good, because recipe storage remains simple and focused on recipe management
* Good, because normalization logic can evolve without requiring recipe migrations
* Good, because enables context-aware matching (e.g., "tomatoes" → "Roma tomatoes" if available)
* Bad, because normalization complexity is deferred rather than eliminated
* Bad, because materialization process becomes more complex with normalization step
* Bad, because potential performance impact during meal planning initialization

### Confirmation

Implementation compliance can be confirmed through:
- Recipe catalog stores original ingredient specifications without modification
- Recipe materialization produces IngredientRequirement objects with normalized data
- IngredientBroker negotiation uses only normalized ingredient representations
- User interface displays original recipe formats while planning uses normalized data
- Performance tests validate materialization overhead remains acceptable

## Pros and Cons of the Options

### Lazy normalization during materialization

Create normalized IngredientRequirement objects when recipes are materialized for meal planning, while preserving original recipe formats in storage.

* Good, because preserves authentic recipe representation for user display
* Good, because enables context-aware normalization with current inventory knowledge
* Good, because normalization occurs only when needed for active planning
* Good, because allows normalization improvements without recipe data migration
* Good, because clean separation between recipe storage and planning operations
* Bad, because adds complexity to recipe materialization process
* Bad, because potential performance overhead during meal planning initialization

### Recipe-level normalization at intake

Normalize ingredient names and units when recipes are created/imported.

* Good, because creates consistent internal representation
* Good, because normalization overhead occurs once at creation
* Bad, because original recipe formatting is permanently lost
* Bad, because normalization lacks inventory context for accuracy

### IngredientBroker-level normalization

Preserve original formats, normalize during broker negotiation.

* Good, because preserves recipe authenticity
* Bad, because adds complexity to critical negotiation path
* Bad, because normalization overhead during time-sensitive operations

### Recipe conforms to ingredient catalog

Require recipes to use predefined ingredient formats.

* Good, because ensures perfect consistency
* Bad, because creates poor user experience requiring format compliance
* Bad, because prevents natural language recipe input

## More Information

This decision introduces the concept of recipe "materialization" - the process of converting a stored recipe into a working representation for meal planning. The materialization process will use a separate IngredientNormalizer service (likely in a dedicated Ingredient bounded context) to convert original ingredient specifications into canonical IngredientRequirement objects.

The IngredientRequirement domain object should capture both normalized data for internal operations and original specifications for user reference:

```python
@dataclass
class IngredientRequirement:
    ingredient: Ingredient      # Normalized ingredient entity
    quantity: float            # Converted to standard units
    unit: str                  # Canonical unit
    original_spec: str         # "2 lbs carrots" - preserved for reference
```

This approach enables future enhancements like seasonal ingredient substitution, regional name variations, and improved LLM-based normalization without requiring changes to stored recipe data.
