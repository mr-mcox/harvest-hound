# Recipe Context Sources (Magazine Clips, Past Recipes)

**Discovered**: recipe-pitch-selection experiment, 2025-11-29
**Priority**: Low (enhancement for later)

## Observation

User mentioned: "Diversity will get even better once the system contains recipes that I've clipped from my cooking magazines."

This suggests the system should eventually incorporate user's existing recipe collection as context for generation.

## Questions

**What recipe sources should influence generation?**
- Clipped magazine recipes (photos + text)?
- Previously cooked recipes from the system?
- Favorite recipes from other sources (websites, cookbooks)?
- Recipes user has rejected (learn what NOT to suggest)?

**How is this context used?**
- Style/technique inspiration?
- Flavor profile preferences?
- Complexity level calibration?
- Ingredient combination patterns?

**Storage & representation:**
- OCR from magazine photos?
- Manual entry?
- URL imports from recipe sites?
- Just titles + tags vs full recipes?

**When does this become valuable?**
- After first week of use (learn preferences)?
- After month of cooking history?
- Immediately with imported collection?

**Integration with generation:**
- "More like this recipe" feature?
- Automatic style inference from collection?
- Explicit "inspired by" selections?

## Hypothesis

**Not needed for MVP.** This is enhancement after core workflow is solid.

**Possible phasing:**
1. MVP: No recipe context, just inventory + household profile
2. V2: Track cooked recipes, learn preferences passively
3. V3: Import/clip external recipes, use as inspiration context

**Quick win:** Simple "inspiration recipe" field in pitch generation UI - paste a recipe URL or description, system generates variations using current inventory.

## Deferred Until

- Core pitch → flesh out → cook workflow is solid
- User has meaningful cooking history in system
- Clear signal that current suggestions lack desired variety

## Related

- Could connect to ingredient claiming (recipes user cooks frequently = preferred ingredients)
- Could inform household profile refinement (pasta recipes dominate = strong pasta preference)
