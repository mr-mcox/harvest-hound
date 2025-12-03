# Recipe Editing After Planning

**Discovered**: recipe-persistence experiment, 2025-12-01
**Uncertainty**: Medium (clear need, but scope and UX unclear)
**Architectural Impact**: Medium (affects recipe identity, claim updates, regeneration)
**One-Way Door**: No (can start simple and evolve)

## The Question

How should users modify planned recipes after they've been saved? Is it editing, regenerating, or something else?

## Context

User feedback after implementing recipe persistence:
> "I could see a 'that's close, but please do X' feedback, but that's future work."

> "Sometimes I do say - hmm, I planned this recipe earlier this week but now I'm wondering if we can take it in X direction instead or substitute Y ingredient"

**Current workaround**: Abandon recipe → generate new pitches → flesh out alternative
- Works, but loses recipe context
- Abandoning releases claims, might enable competing recipes
- Feels like starting over rather than refining

## Use Cases

**UC1: Ingredient substitution**
- User planned "Beef Pot Roast" but beef is now expired/frozen solid
- Wants: "Use pork instead"
- Current workaround: Abandon → regenerate pork roast

**UC2: Recipe refinement**
- User sees full recipe, likes it mostly but wants adjustment
- Examples: "Make it spicier", "Add a vegetable side", "Use fresh herbs not dried"
- Current workaround: Abandon → regenerate with different context

**UC3: Effort adjustment**
- Planned "3-hour braise" but now only have 30 min
- Wants: "Make this faster (pressure cooker? simpler version?)"
- Current workaround: Abandon → regenerate quick meal

## Options Considered

### Option A: Feedback + Regenerate
User provides feedback, system regenerates recipe:
```
[Honey-Butter Roasted Radishes]
  [Give Feedback]

  → Modal: "What would you like to change?"
  User: "Use pork chops instead of chicken"

  → System: Regenerates recipe with feedback
  → Claims updated to reflect new ingredients
  → Recipe name/description updated
```

**Pros**:
- Leverages LLM for creative refinement
- Maintains recipe identity (same slot in meal plan)
- Natural language feedback (low friction)

**Cons**:
- Regeneration might deviate too far
- Claims need careful updating (release old, reserve new)
- Might feel unpredictable

### Option B: Manual Editing
User edits recipe fields directly:
```
[Honey-Butter Roasted Radishes]
  [Edit Recipe]

  → Edit mode: Change ingredients, instructions, title
  → Save changes
  → System recalculates claims
```

**Pros**:
- Full control, predictable
- Good for small tweaks (quantities, methods)

**Cons**:
- High friction for significant changes
- Doesn't leverage LLM creativity
- Ingredient parsing/claiming logic complex

### Option C: Hybrid - Edit + AI Assist
Combine manual editing with AI suggestions:
```
[Honey-Butter Roasted Radishes]
  [Tweak Recipe]

  Quick adjustments:
  - Substitute ingredient → [Radishes ▼] for [Turnips ▼]
  - Adjust servings → [4 ▼] servings
  - Cooking method → [Roasted ▼] to [Grilled ▼]

  OR free-form feedback:
  - "Make it spicier and add vegetables"

  → System regenerates with constraints
```

**Pros**:
- Structured for common tweaks
- Flexibility for complex changes
- AI handles recipe coherence

**Cons**:
- UI complexity
- Might be overkill for MVP

### Option D: Defer - Just Use Abandon
Keep current workaround for MVP:
```
- Abandoning is low-friction
- Regeneration is cheap (pitches are fast)
- Editing needs unclear until more usage data
```

**Pros**:
- No development needed
- Learn more about editing patterns before building
- Works "well enough" for prototype

**Cons**:
- Loses recipe context (start from scratch)
- Might frustrate users for simple substitutions

## Architectural Implications

### Recipe Identity
- If regenerated: Is it the "same recipe" or a "new recipe"?
- Does recipe ID change, or does version increase?
- How to track evolution? (Recipe v1 → v2 → v3)

### Claim Management
If ingredients change:
1. Release old claims (butter, radishes)
2. Reserve new claims (turnips, olive oil)
3. Update available inventory mid-week
4. What if new ingredients unavailable?

### Regeneration Constraints
Feedback-based regeneration needs to maintain:
- Same meal slot (still a "quick weeknight")
- Available ingredients (can't suggest unavailable items)
- Core concept (pot roast → still a braise, not a stir-fry)

### Data Model Impact
- Recipe versioning? (`recipe_history` table?)
- Feedback tracking? (capture what users change for prompt improvement)
- Undo/redo? (probably overkill)

## Hypothesis

**Start with Option D (defer)**:
- Current abandon workflow is "good enough" for MVP
- Gather more usage data on editing patterns
- Common substitutions might inform structured UI later

**Next evolution** (if patterns emerge):
- If mostly ingredient swaps → build simple substitution UI (Option C lite)
- If mostly creative refinement → add feedback modal (Option A)
- If mostly manual tweaks → consider edit mode (Option B)

## Next Steps to Explore

1. **Track abandonment reasons** - add optional "Why abandon?" field
2. **Observe patterns** - do users re-generate similar recipes? specific substitutions?
3. **Build simplest version** that addresses most common pattern
4. **Iterate based on usage**

## Related Questions

- **Recipe identity** (`pitch-recipe-relationship.md`) - Editing affects recipe identity model
- **Ingredient claim visibility** - Need to show claim changes clearly when recipe is edited
