# Open Question: Portioning Constraints

**Status**: Open
**Created**: 2025-11-29
**Last Updated**: 2025-11-29

## The Question

Should we explicitly model portioning constraints for inventory items (discrete packages vs infinitely divisible), or is store-level context sufficient?

## Context

During inventory management implementation, we discovered that inventory items have different portioning behaviors:

**Discrete Portions** (Freezer meat):
- 2 lbs pulled pork = 2 separate 1-lb packages
- Can only use in whole increments (1 package or 2 packages, not 1.5)
- Recipe generator used all 2 lbs at once, but reality is you must use 1 or 2 packages
- Quantity editing feels "janky" for count-based items (3 roasts → 2 roasts)

**Infinitely Divisible** (Vegetables):
- 2 lbs carrots = bulk item
- Can use any amount (0.5 lbs, 1 lb, 1.7 lbs, etc.)
- Quantity editing works naturally

**Current Approach**: Store-level context in definition
- Example: "Freezer meat. Portions are typically 1 lb unless otherwise specified"
- BAML uses this for parsing and potentially recipe generation

## Symptoms

1. **Parsing ambiguity**: "2 lbs pulled pork" → is this 2 packages or bulk weight?
2. **UX friction**: Increment/decrement doesn't make sense for count-based items
3. **Recipe constraints**: LLM doesn't know it can only use whole packages

## Options Considered

### Option 1: Store-level context (current)
**Pros**:
- Simple, no data model changes
- LLM can infer constraints from context
- Works for current prototype

**Cons**:
- Not explicitly modeled, relies on LLM interpretation
- UX can't adapt based on portioning type
- Recipe generator might not respect constraints

### Option 2: Explicit portioning field on inventory items
**Pros**:
- Clear data model
- UX can adapt (show +1/-1 buttons for discrete, free input for divisible)
- Recipe generator gets explicit constraints
- Better long-term scalability

**Cons**:
- More complex data model
- Need to determine portioning at entry time
- Adds cognitive overhead during inventory stocking

### Option 3: Hybrid - portioning hints at store level, optional override per item
**Pros**:
- Store defaults reduce repetition (freezer defaults to 1-lb portions)
- Can override for exceptions (3-lb roast)
- Balances simplicity and flexibility

**Cons**:
- Most complex option
- Cognitive overhead to understand the system

## Confidence Level

**Low** - Only surfaced in one experiment. Need more data points to know if this is:
- A fundamental domain requirement
- A temporary UX annoyance
- Something LLM context can solve adequately

## Next Steps to Explore

1. **Test recipe generation**: Does the LLM respect store context and suggest whole-package amounts?
2. **Test editing workflow**: How often does the "janky" UX actually cause problems?
3. **Watch for pattern**: If portioning pain appears in 2+ more experiments, elevate to explicit modeling

## Related Learnings

- **Item-based units**: Using "roast", "chop" helps (discovered: inventory-management experiment)
- **Store context for parsing**: Works well for "xN notation" (discovered: inventory-management experiment)
- **Portioning affects**: Parsing, editing UX, recipe generation constraints

## Decision Criteria

Promote to explicit modeling if:
- Recipe generation frequently violates portioning constraints
- UX friction causes repeated user complaints
- Alternative approaches (LLM context) prove insufficient

Keep as store-level context if:
- LLM respects context adequately in practice
- UX annoyance is rare/tolerable
- Explicit modeling doesn't meaningfully improve experience
