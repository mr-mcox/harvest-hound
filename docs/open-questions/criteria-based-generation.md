# Criteria-Based Recipe Generation

**Discovered**: ingredient-claiming-cognitive-load experiment, 2025-12-01
**Uncertainty**: Medium
**Architectural Impact**: Medium
**One-Way Door**: No

## The Question

How should we generate pitches for multiple meal criteria simultaneously (e.g., "weekend meal", "quick weeknight", "guest meal with long passive time")?

## Context

User insight:
> "I'm also curious if there are multiple criteria, simultaneously creating pitches for all of them - eg 'weekend meal', 'quick weeknight', 'short active but potentially long cooking for weeknight guest' as separate criteria and we lay out pitches according to those criteria."

This relates to the "structured meal planning workflow" discovery:
- User provides meal needs upfront with constraints
- System generates pitches per category/spec
- UI displays pitches grouped by criteria
- User selects from each category

## Options Considered

### Option A: Single BAML Call with Keyed Output
- One generation call with all criteria
- BAML output includes criteria key for each pitch
- Example output:
  ```json
  [
    {criteria: "weekend", name: "...", ...},
    {criteria: "quick_weeknight", name: "...", ...},
    {criteria: "guest_meal", name: "...", ...}
  ]
  ```
- Frontend groups pitches by criteria for display

**Pros**:
- Single LLM call = faster, cheaper
- LLM can optimize across criteria (balance variety)
- Simpler backend logic

**Cons**:
- More complex BAML schema
- All pitches generated together (less streaming granularity)

### Option B: Separate BAML Calls per Criteria
- Multiple generation calls, one per criteria
- Each call optimized for that specific constraint
- Results streamed separately per criteria

**Pros**:
- Simpler BAML schema
- Can stream results per criteria
- Easy to add/remove criteria dynamically

**Cons**:
- Multiple LLM calls = slower, more expensive
- LLM doesn't see full context across criteria

### Option C: Hybrid Approach
- Single call for related criteria (e.g., weeknight meals together)
- Separate calls for distinct types (weekend vs weeknight)
- Balance cost/speed with context awareness

## Architectural Implications

**BAML Schema**:
- Need to model criteria as part of request/response
- Potentially new RecipePitchWithCriteria class

**Generation Flow**:
- How to balance inventory claiming across criteria?
- If "weekend meal" claims all the beef, what happens to "guest meal"?
- Need claiming strategy that reserves ingredients per criteria?

**UI Layout**:
- Pitches grouped by criteria (tabs? sections? columns?)
- Selection interaction: one from each category? Or flexible?
- Visual feedback on criteria fulfillment ("2/3 weekend meals selected")

**Validation**:
- Ensure generated pitches actually match criteria
- Judge could validate: "Is this really a quick weeknight meal?"

## Related Workflows

From LEARNINGS.md:
> **Structured meal planning workflow**: Specs upfront, systematic filling
> - User provides meal needs with constraints: "quick weeknight x2", "guest meal that cooks while I work", "leftovers meal"
> - System generates pitches per category/spec
> - User selects from each category

This is about making that workflow concrete.

## Next Steps to Explore

1. **Prototype keyed generation**: Update BAML to output criteria with each pitch
2. **Test UI layout**: Show pitches grouped by criteria, get user feedback
3. **Claiming across criteria**: How to prevent one criteria from monopolizing ingredients?
4. **Criteria validation**: Can judge check if pitch matches stated criteria?

## Current Decision

**Experiment with Option A** - Single BAML call with keyed output
- User leaning toward this: "Probably one BAML call"
- Lower cost/latency
- Can iterate on BAML schema in prototype
- Related to structured meal planning workflow already validated
