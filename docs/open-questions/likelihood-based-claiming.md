# Likelihood-Based Ingredient Sourcing

**Discovered**: store-based-claiming experiment, 2025-12-01
**Uncertainty**: Medium
**Architectural Impact**: High
**One-Way Door**: Partial (can evolve approach, but changes claiming model)

## The Question

Should ingredient claiming use probability-based sourcing instead of rigid pantry/grocery split?

## Context

User insight: "There are only three kinds of stores and two of them are singletons:
1. Explicit stores (CSA, Freezer, etc.) - we know we have it
2. Our pantry (singleton) - assume we have common staples
3. Grocery stores (multiple) - where we buy things

The claiming logic should be: If we've explicitly stated that we have it, then we have it. If not, then have the LLM judge the likelihood that we'd need to grocery shop for that ingredient."

Current problem: Binary pantry/grocery split doesn't match reality
- Example: "Check you have 2.5 tsp salt" - silly, obviously have salt
- Example: "8 oz goat cheese" - definitely need to buy
- Grey area: "1 onion" - maybe have it, maybe not

## Proposed Approach

Replace binary with likelihood judgment:

### Three Tiers:
1. **High likelihood need to buy** - Definitely grocery list
   - Unusual ingredients (goat cheese, specialty items)
   - Large quantities beyond normal stock ("2 lbs walnuts")
   - Items not in pantry definition

2. **Medium likelihood (verify)** - User review needed
   - Common items in uncertain quantities ("3 onions" - do I have 3?)
   - Pantry items that might be low ("flour" - need 2 cups, may be running low)
   - Borderline specialty items

3. **Low likelihood (assume pantry)** - Don't show
   - Tiny quantities of common items ("2.5 tsp salt")
   - Universal staples below threshold
   - Things definitely in pantry definition

### LLM Judgment Inputs:
- Ingredient name and quantity
- Pantry definition (what user typically has)
- Previous corrections (learning over time)
- Quantity threshold (2 tsp vs 2 cups makes a difference)

## Options Considered

### Option 1: Hard-Coded Rules
- Define thresholds: salt < 1 tbsp = ignore, > 1 tbsp = verify
- Category lists: definitely-pantry, probably-pantry, probably-grocery
- **Pro**: Predictable, fast
- **Con**: Brittle, doesn't adapt to user

### Option 2: LLM Likelihood Judgment
- Prompt LLM: "Given pantry definition and ingredient, rate likelihood user needs to buy this (high/medium/low)"
- Include reasoning: "8oz goat cheese - HIGH because specialty cheese not in pantry definition and significant quantity"
- **Pro**: Flexible, learns from pantry definition
- **Con**: Extra LLM call, potential inconsistency

### Option 3: Hybrid - Rules + LLM Refinement
- Start with simple rules (tiny quantities, common spices → skip)
- Use LLM for grey area items
- **Pro**: Fast for obvious cases, smart for uncertain cases
- **Con**: Complexity of two systems

### Option 4: Learning System
- Start with LLM judgment
- User corrects ("Actually, I need to buy onions" or "I always have onions")
- System learns patterns over time
- **Pro**: Adapts to user
- **Con**: Requires correction UI, persistence, training period

## Architectural Implications

**High impact** - Changes fundamental claiming model

Data model:
- Add likelihood field to IngredientClaim: `likelihood: "high" | "medium" | "low"`
- Track user corrections for learning
- Store likelihood reasoning for transparency

Prompt changes:
- Add likelihood judgment step to recipe generation
- Pass pantry definition with context
- Include quantity thresholds in prompts

UI changes:
- Shopping list sections: "Buy" (high) → "Verify" (medium) → "Pantry" (low/hidden)
- User can promote/demote items between sections
- Reasoning visible on hover ("Why is this here?")

Code changes:
- Claiming logic evaluates likelihood
- Shopping list filters by likelihood
- Correction feedback loop

## Next Steps to Explore

1. **Test LLM judgment accuracy**: Generate likelihood ratings for test ingredients, validate against intuition
2. **Prototype three-tier UI**: Show high/medium/low sections, user feedback on utility
3. **Threshold experimentation**: What quantity cutoffs feel right? (1 tsp vs 1 cup salt)
4. **Correction patterns**: Track if users consistently move certain items → learn rules
5. **Pantry context impact**: Does better pantry definition reduce medium-likelihood items?

## Related Discoveries

- Pantry definition learning (open-questions/pantry-definition-learning.md) - Better pantry = better likelihood
- Multiple grocery stores (open-questions/multiple-grocery-stores.md) - Likelihood may vary by store
- Ingredient structure (open-questions/ingredient-structure.md) - Need clean ingredient matching
- Grocery list organization (open-questions/grocery-list-organization.md) - Likelihood-based ordering

## Success Criteria

Solution works when:
- User never sees silly items ("verify you have 1 tsp salt")
- High-confidence items always on shopping list
- Medium items catch real gaps ("oh yeah, I am low on onions")
- Corrections reduce over time (system learns)
- Grocery list feels "just right" - not too sparse, not too cluttered
