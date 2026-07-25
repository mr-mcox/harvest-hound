# Recipe Editing/Substitutions

**Status**: Next (phase: Recipe Memory & Trust — third spine strand, see
`phase-recipe-memory.md` Insight 4)
**Impact**: Critical - Essential cooking workflow
**Discovered**: 2025-12-21 (Week 3 production use)
**Related**: `phase-recipe-memory.md`, `pain-recipe-feedback.md`

**Framing**: Two distinct interactions. *Editing* (mutation) changes the recipe and folds
into durable recipe memory as the **final product only** — no edit history/changelog.
*Asking* (conversation) is context-aware guidance that changes nothing; it has no
persistence dependency and can ship independently.

## The Pain

Real cooking involves on-the-fly decisions that the current system doesn't support. Users need to make substitutions during prep and cooking, but can't modify recipes or get context-aware guidance.

### User Examples

> "We don't have white wine - rice wine gonna be ok (since it's only 1/4 cup)?"

> "Whoops - I accidentally roasted broccoli. What might I substitute instead - I'm thinking spinach."

> "There was creme fraiche called for and I wanted to know the best way to substitute sour cream for that dish."

## Why It Matters

1. **Shopping list accuracy**: If user doesn't actually use listed ingredients, shopping list becomes inaccurate for future reference
2. **Recipe-specific guidance**: Generic substitution knowledge isn't enough - need context-aware advice for specific dishes
3. **Missing dialogue**: Can't "chat with" the recipe to ask questions or get clarification

## Solution Direction

"Chat with recipe" capability that allows:
- Simple ingredient substitutions (swap ingredient A for B)
- Context-aware substitution guidance (what's the best way to sub in THIS dish?)
- Shopping list sync (recipe changes reflected in shopping list)

## Potential Breakdown

This is multi-faceted - unpack piece by piece:
- [ ] Basic ingredient swap UI (simplest value)
- [ ] LLM-powered substitution guidance (recipe-specific advice)
- [ ] Shopping list update on recipe changes (accuracy)

## Notes

User preference: "Unpack piece by piece" - this is complex, start with highest-value slice.

Key question: What's the 20% that gives 80% value? Likely the substitution guidance rather than full editing.
