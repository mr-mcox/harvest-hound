# Recipe Identity Validation

**Discovered**: ingredient-claiming experiment, 2025-11-30
**Uncertainty**: High (two approaches with unclear tradeoffs - constraints vs judge)
**Architectural Impact**: Medium-High (affects generation flow, claiming timing, error handling)
**One-Way Door**: Partially (affects generation flow, but more isolated than data model changes)

## Problem

When fleshing out recipes with claimed ingredients, the LLM auto-pivots to use remaining inventory. However, pivots can break the recipe identity and violate the pitch promise.

**Example**:
- Pitch: "Beef Pot Roast with Sirloin"
- User selects based on expectation of beef
- Fleshed out recipe: "Pot Roast with Pork Butt"
- Result: Broken trust - family says "that's not what I thought we were having"

## Three Pivot Failure Modes

User identified three boundaries where a pivot is "too different":

1. **Can't make with available ingredients**
   - Substitution is impossible
   - Should fail fast with clear message

2. **Effort significantly different**
   - Pitch suggested quick weeknight meal (30 min)
   - Fleshed out requires 3-hour braise
   - Time commitment violation

3. **Family expectations broken**
   - Core ingredient changed (beef → pork)
   - Cooking technique changed (roast → stew)
   - Dish identity no longer recognizable

## Questions

**How to validate recipe identity?**
- Separate BAML "judge" call after generation?
- Constraints in the generation prompt itself?
- Return confidence score with recipe?
- Pre-commit to core ingredients before fleshing out?

**What makes a substitution acceptable?**
- Same protein category? (beef → different beef cut ✓, beef → pork ✗)
- Same cooking technique? (roast → roast ✓, roast → stew ✗)
- Same time commitment? (30 min → 45 min ✓, 30 min → 3 hours ✗)
- Same flavor profile?

**When should pivot fail vs succeed?**
- Succeed: Radish → potato (similar vegetable, same cooking method)
- Fail: Beef sirloin → pork butt (different protein, different technique)
- Gray area: Chicken breast → chicken thighs? Carrots → parsnips?

**How to communicate failures?**
- "Can't flesh out this recipe with remaining ingredients"
- Show which ingredients are missing?
- Suggest which other pitches might work better?
- Auto-disable conflicting pitches?

## Hypothesis

**Two-phase validation:**

1. **During generation**: Constrain LLM with core ingredients
   - Extract "core ingredients" from pitch (main protein, key vegetables)
   - Pass to flesh-out with constraint: "These ingredients are REQUIRED"
   - LLM can pivot supporting ingredients but not core

2. **After generation**: Judge prompt validates
   - Input: original pitch + fleshed recipe
   - Question: "Does this recipe match the user's expectations from the pitch?"
   - Output: Pass/fail + explanation
   - If fail: Return error instead of recipe

**Alternative**: Pre-commit to ingredients
- After user selects pitch, show: "This will use: beef sirloin, carrots, potatoes"
- User confirms before fleshing out
- But this adds friction (extra click, decision fatigue)

## Success Criteria

- Fleshed recipes match pitch promises (protein, technique, time)
- Auto-pivot works for supporting ingredients (vegetables, garnishes)
- Clear failure when core ingredients unavailable
- User can trust that selecting a pitch = getting that dish concept

## Architectural Implications

**Affects generation flow**:
- **Constraints approach**: Must extract core ingredients before generation
  - Affects: BAML prompt structure (pass required ingredients)
  - Risk: Too restrictive → boring recipes

- **Judge approach**: Validate after generation
  - Affects: Error handling (what if validation fails?)
  - Affects: Claiming timing (claim before or after validation?)
  - Risk: Wasted tokens on failed validations

**Affects claiming timing**:
```
Option 1: Claim → Validate
- Recipe generates → claims ingredients → validator checks
- Problem: If validation fails, need to unclaim

Option 2: Generate → Validate → Claim
- Recipe generates → validator checks → then claims
- Better: No unclaiming needed, but more complex flow
```

**Affects error handling**:
- If validation fails: Regenerate? Show error? Disable pitch?
- User feedback: "Can't make this with remaining ingredients"
- UI implications: Loading states, error messages

## Edge Cases to Explore

- Pitch lists multiple protein options ("chicken or beef")
- Vague pitch that allows wide interpretation
- User explicitly wants flexibility ("surprise me")
- Budget constraint makes exact ingredient unavailable

## Next Experiment

1. Implement judge prompt to validate after generation
2. Test with intentionally conflicting scenarios
3. Measure: How often does judge catch bad pivots?
4. Refine: What makes a good "recipe identity" check?
5. Determine: Should validation happen before or after claiming?
