# Workflow Learnings

_Validated discoveries about user behavior patterns and what works/doesn't work._

### Workflows That Feel Natural
1. [x] **Zero-click recipe generation**: Auto-loading all ingredient sources, optional context field
   - Big win: just click "Generate" without manual entry
   - Optional context useful when needed, ignorable when not
   - (discovered: recipe-generation experiment, 2025-11-29)

2. [x] **Bulk inventory entry via free text**: Single textarea replacing 3-field form
   - User reaction: "soooo much easier. I love it."
   - Real CSA delivery list pasted and parsed accurately
   - One action: paste → parse → all ingredients added
   - (discovered: inventory-management experiment, 2025-11-29)

3. [x] **Inline inventory editing**: Delete and update quantity per item
   - Delete works great, heavily used for cleanup
   - Update quantity works but feels "janky" for count-based items (3 roasts → 2 roasts)
   - Suggests portioning awareness could improve UX
   - (discovered: inventory-management experiment, 2025-11-29)

4. [x] **Two-phase recipe browsing**: Pitches → selection → flesh out
   - Pitch browsing feels right for exploring options
   - Click-to-select interaction works well (reduced UI clutter vs checkboxes)
   - Fleshing out selected recipes feels right
   - User reaction: "This is what I hoped for from the system"
   - Pitch quality ~80% there for decision-making
   - (discovered: recipe-pitch-selection experiment, 2025-11-29)

5. [x] **Iterative recipe generation in waves**: Pick some → generate more → pick rest
   - Workflow confirmed: "Pick 3 → regenerate → pick 2 more → have 5 for the week"
   - BROKEN without ingredient claiming: second wave reuses already-claimed ingredients
   - Adaptive generation count needed: If picked N, don't need full 10 in next wave
   - (discovered: recipe-pitch-selection experiment, 2025-11-29)

6. [x] **Structured meal planning workflow**: Specs upfront, systematic filling
   - User provides meal needs with constraints: "quick weeknight x2", "guest meal that cooks while I work", "leftovers meal"
   - System generates pitches per category/spec
   - User selects from each category
   - Next wave fills remaining slots with remaining ingredients
   - Different from ad-hoc "generate 10 pitches" - this is purposeful, constraint-driven planning
   - Wave sizing: 3x the number of unfilled meal slots (if need 2 more meals, generate 6 pitches)
   - (discovered: ingredient-claiming experiment, 2025-11-30)

7. [x] **Pitch lifecycle management**: Invalid pitches should be removed automatically
   - Pitches using claimed ingredients become invalid (insufficient inventory)
   - Initially tried graying out invalid pitches for visibility
   - User feedback: "I'd like them removed" - don't want to see unavailable options
   - Suggests pitch pool maintenance: remove invalid, optionally backfill with new pitches
   - (discovered: ingredient-claiming experiment, ingredient-claiming-cognitive-load experiment, 2025-11-30/12-01)

8. [x] **Pitch pool self-healing**: Generate to maintain availability threshold
   - After claiming ingredients, some pitches become invalid (removed)
   - Want to maintain consistent pool of available options
   - Automatic backfill: when available pitches drop below threshold, generate more
   - Decision: Defer automatic backfill, manual "Generate More" works for now
   - (discovered: ingredient-claiming-cognitive-load experiment, 2025-12-01)

9. [x] **Recipe persistence workflow**: Auto-save on flesh-out → cook/abandon lifecycle
   - Fleshing out automatically saves recipe to "My Planned Recipes" (no separate accept step)
   - Planned recipes visible at top of page (compact view) as weekly hub
   - Cook action: consumes claims, decrements inventory, marks recipe complete
   - Abandon action: releases claims without consuming inventory, marks recipe abandoned
   - Low-friction abandoning makes auto-save acceptable (no "don't save this" needed)
   - Page becomes central hub to return to throughout week
   - User reaction: "Feels a lot more authentic"
   - (discovered: recipe-persistence experiment, 2025-12-01)

10. [x] **Flat ingredient view with priority**: Single list sorted by priority
    - Reduces cognitive load vs store-centric organization
    - User doesn't think about "which store?" when adding ingredients
    - Auto-creates default store invisibly when needed
    - Priority sorting surfaces urgent items at top
    - User reaction: "Reduced cognitive load and number of steps"
    - (discovered: ingredient-priority experiment, 2025-12-01)

11. [x] **LLM-suggested priorities mostly right**: AI guesses are accurate
    - LLM considers perishability when suggesting priority (frozen → low, fridge → high)
    - Mostly accepts suggested priorities without adjustment
    - Normal distribution (lots in medium) is healthy, not a problem
    - Validates AI-assisted data entry approach
    - (discovered: ingredient-priority experiment, 2025-12-01)

12. [x] **Shopping list view fills workflow gap**: Planning → Shop → Cook flow complete
    - Shopping list aggregates claims by ingredient source (Grocery vs Pantry Staples)
    - Format: "2 onions - used in: Recipe A, Recipe B"
    - Copy-paste button for transferring to shopping app
    - Pantry Staples verification checklist ("Check you have 2c polenta for Recipe X")
    - User reaction: "This works great"
    - Fills missing step between meal planning and actual shopping
    - (discovered: store-based-claiming experiment, 2025-12-01)

### Surprising Complexities
- [x] **Ingredient representation mixes shopping and preparation**: Blurry boundary
  - Problem: Shopping list shows "0.75 cup walnuts, roughly chopped"
  - User doesn't buy pre-chopped walnuts - preparation instruction leaked into ingredient
  - Reveals question: What fields are part of an ingredient?
  - Shopping needs: "walnuts" (the thing to buy)
  - Recipe needs: "walnuts, roughly chopped" (how to prepare)
  - May need separation: ingredient base + preparation modifier
  - (discovered: store-based-claiming experiment, 2025-12-01)

- [x] **Recipe editing/substitutions are essential cooking workflow**: Not post-MVP enhancement
  - **REFINED (2026-07-25)**: "chat with recipe" is two interactions, not one — *editing*
    (mutation, folds into durable recipe memory as final product only) and *asking*
    (conversation, no persistence). See `docs/roadmap/pain-recipe-editing.md`.
  - Real cooking involves on-the-fly decisions system must support
  - Examples: White wine → rice wine, accidental ingredient prep (roasted broccoli → need spinach sub)
  - Recipe-specific guidance needed: "Best way to sub sour cream for creme fraiche in THIS dish?"
  - Impact on shopping list: Changes to recipe make shopping list inaccurate
  - User needs "chat with recipe" capability for questions/modifications
  - Not a nice-to-have: essential for real cooking workflow
  - (discovered: production use week 3, 2025-12-21)

- [x] **Recipe metadata unreliable**: Time estimates can be significantly off
  - Example: Recipe showed "45 min active prep", reality was "70 min prep, 90 min to table"
  - Affects meal planning decisions (weeknight vs. weekend, dinner timing)
  - Creates trust issue with recipe generation
  - User quote: "Thai curry tasted great but 45 minutes active prep was a dirty rotten lie"
  - Opportunity: Capture actual time feedback to improve estimates and identify "greatest hits"
  - (discovered: production use week 3, 2025-12-21)


## Use Cases (Keep Lean!)

### Essential (Must Have)
1. [x] **Generate recipes from current inventory with zero friction**
   - Validated: Auto-loading stores, optional context works well
   - (discovered: recipe-generation experiment, 2025-11-29)

2. [x] **Bulk inventory entry**: Paste CSA delivery list and parse
   - Validated: Major workflow improvement, heavily used
   - Enables authentic testing with real inventory
   - (discovered: inventory-management experiment, 2025-11-29)

3. [x] **Basic inventory editing**: Delete and adjust quantities
   - Validated: Delete heavily used for cleanup
   - Update quantity works but could be better for count-based items
   - (discovered: inventory-management experiment, 2025-11-29)

4. [x] **Browse recipe pitches before committing token budget**
   - Validated: Two-phase generation (pitches → flesh out) feels right
   - Essential for exploring diverse options without expensive full generation
   - User reaction: "This is what I hoped for from the system"
   - (discovered: recipe-pitch-selection experiment, 2025-11-29)

5. [x] **Ingredient claiming for multi-wave generation**
   - Validated: CRITICAL for iterative workflow
   - Without it, second wave reuses already-allocated ingredients
   - Blocking issue for "pick 3 → generate more → pick 2 more" workflow
   - Implemented in Phases 1 & 2: Wave 2 claiming + greedy flesh-out
   - (discovered: recipe-pitch-selection experiment, ingredient-claiming experiment, 2025-11-29/30)

6. [x] **Recipe identity validation**: Prevent pivot from breaking pitch promise
   - Essential: User picks "Beef Pot Roast", system delivers "Pork Butt Pot Roast" - broken trust
   - Need judge/validator to check if pivot is too different
   - Three boundaries: ingredients unavailable, effort significantly different, family expectations broken
   - (discovered: ingredient-claiming experiment, 2025-11-30)

7. [x] **Ingredient claim visibility**: Need to see what's claimed vs available
   - Essential: "Why aren't I getting radish recipes? Oh, forgot about that planned meal that claimed them"
   - Need bidirectional lookup: which recipes → which ingredients, which ingredients → which recipes
   - Week-level view: "Oh we aren't using beets for anything this week? Maybe I'll roast them as a side"
   - Helps prevent ingredient waste and reveals meal planning gaps
   - Week-by-week operation means n is small, so detailed tracking is feasible
   - (discovered: recipe-persistence experiment, 2025-12-01)

8. [x] **Recipe editing/tweaking after planning**: Substitute ingredients in saved recipes
   - Nice to have: "I planned this earlier but now want to substitute Y ingredient"
   - Feedback option: "That's close, but please do X" to refine recipe
   - Not blocking for MVP, abandoning is low-effort workaround
   - (discovered: recipe-persistence experiment, 2025-12-01)

9. [x] **Shopping list generation from claims**: Aggregated view by store
   - Essential: Can't go shopping without knowing what to buy
   - Validated: Fills workflow gap (plan → shop → cook)
   - Format works: "2 onions - used in: Recipe A, Recipe B"
   - Copy-paste to shopping app successful
   - Pantry verification checklist reduces anxiety
   - User reaction: "This works great"
   - (discovered: store-based-claiming experiment, 2025-12-01)

### Nice to Have
- [x] **Week-level planning criteria**: Structured constraints for balanced variety
  - Example: "1 weekend meal, 1 guest meal (weeknight), 2 quick meals, 1 leftovers meal"
  - Different from ad-hoc context, helps generate balanced week
  - Evolved to: Structured meal planning workflow (specs upfront, systematic filling)
  - (discovered: recipe-pitch-selection experiment, ingredient-claiming experiment, 2025-11-29/30)

- [x] **Adaptive generation count**: Generate fewer pitches in subsequent waves
  - If already picked 3, don't need full 10 in next wave (just 2-3 more)
  - Efficiency + reduced cognitive load
  - Evolved to: 3x unfilled meal slots (need 2 meals → generate 6 pitches)
  - (discovered: recipe-pitch-selection experiment, ingredient-claiming experiment, 2025-11-29/30)

- [x] **Time diversity in pitches**: Mix quick weeknight + leisurely weekend
  - Not quite enough diversity yet in time commitments
  - Want both active AND total time visible
  - Future: Quadrant visualization (total vs passive time)
  - (discovered: recipe-pitch-selection experiment, 2025-11-29)

- [x] **Pitch disabling when ingredients claimed**: Visual conflict indication
  - Pitches using claimed ingredients should be grayed out/disabled
  - Better UX than status messages showing "avoiding X, Y, Z"
  - Reveals conflicts immediately, prevents impossible selections
  - (discovered: ingredient-claiming experiment, 2025-11-30)

- [x] **Grocery list view with optional ingredients**: Essential vs nice-to-have
  - Show what's required vs what would enhance meals
  - User decides which optional items to add to grocery run
  - Two sections: Essential (must buy), Optional (user choice)
  - (discovered: ingredient-claiming experiment, 2025-11-30)

- [x] **Recipe prioritization by uncommon ingredients**: Flesh out CSA items first
  - Prevents common ingredients getting claimed before exotic CSA produce
  - Nice to have, not blocking (auto-pivot works well enough)
  - (discovered: ingredient-claiming experiment, 2025-11-30)

- [ ] **Quick generation for unclaimed ingredients**: One-click side dish generation
  - When viewing unclaimed ingredients ("beets not being used this week"), offer quick action to generate side dish recipes
  - Workflow: Filter to unclaimed → see beets → click "Generate side dishes" → pitches using unclaimed ingredients
  - Reduces friction for "oh I should use these" moments
  - Different from main meal planning (opportunistic vs structured)
  - (discovered: inventory-claims-visibility feature framing, 2025-12-13)

- [ ] **5 recipes per week** (vs current 3) - easy parameter tweak, not blocking
- [ ] **Prioritize expiring ingredients** - could be solved via context field

### Not Needed
- [x] **Per-generation store selection** - Auto-including all stores works fine
  - (discovered: recipe-generation experiment, 2025-11-29)

- [x] **Bulk operations on recipes**: Week-by-week n is small enough
  - No need for "abandon all", "reorder", or other batch operations
  - Individual recipe management sufficient for 5-7 planned recipes per week
  - (discovered: recipe-persistence experiment, 2025-12-01)

- [x] **POINTER vs GENERATIVE pitch distinction**: Too complex for prototype/MVP
  - **SUPERSEDED (2026-07-25)**: MVP complete; durable recipes with provenance are now the
    spine of the current phase (`docs/roadmap/phase-recipe-memory.md`). The distinction
    dissolves — pitches reference recipes; some recipes exist before the session.
    Historical rationale kept below.
  - Mixed workflow (clipped recipes + generated recipes) is overengineered
  - Clipped recipe storage and retrieval adds complexity without validating core hypothesis
  - MVP: Focus only on GENERATIVE pitches from inventory
  - Post-MVP consideration: Recipe library + reuse workflow could be valuable later
  - (discovered: pitch-recipe-identity experiment, 2025-12-02)

- [x] **Character preservation in fidelity**: Doesn't matter for recipe quality
  - Character/tone/writing style can adapt freely
  - User cares about functional fidelity (will recipe work?), not prose quality
  - Kid-friendly adaptations and pantry substitutions improve usability
  - Technique preservation is what matters, not character consistency
  - (discovered: pitch-recipe-identity experiment, 2025-12-02)

