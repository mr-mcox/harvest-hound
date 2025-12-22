# Feature Frame: Shopping List Selection & Pantry Learning

**Date**: 2025-12-20
**Status**: Draft - Awaiting Alignment

---

## Problem Statement

The shopping list currently shows what to buy but doesn't support the actual shopping workflow: checking off what you need, filtering to just those items, and copying only what's relevant. More critically, we're missing an opportunity to learn from these selections - every shopping trip reveals which "pantry staples" assumptions were wrong, but we're not capturing that feedback to improve future grocery lists and recipe generation.

**From Prototype Discovery**:
- Shopping list view works great for planning → shopping workflow (LEARNINGS.md:342)
- **Pantry guesses NOT as accurate as expected** - affects both grocery list ranking AND recipe generation (LEARNINGS.md:232)
- Feedback loop opportunity identified: grocery selections could inform pantry definitions (LEARNINGS.md:233)
- Production validation: copy-paste to shopping apps works, but manual filtering is tedious

---

## User Stories

### Story 1: Interactive Shopping List Selection
**As a** meal planner
**I want** to check off the grocery items I actually need to buy
**So that** I can focus on what's missing from my pantry and ignore what I already have

**Acceptance Criteria**:
- [ ] Each grocery item and pantry staple has a checkbox
- [ ] Checked items are visually distinct from unchecked items
- [ ] Filter toggle shows "Items to Buy" (checked only) vs "All Items" (default)
- [ ] Item check state persists during the session (survives page refresh)
- [ ] Unchecking an item removes it from the filtered view

**From LEARNINGS.md**: Shopping list fills planning → shop → cook workflow (line 342-349), but missing active selection capability

---

### Story 2: Copy Checked Items Only
**As a** meal planner
**I want** to copy only the items I've checked off
**So that** I can paste a clean list into my shopping app (Mealboard, Out of Milk, etc.)

**Acceptance Criteria**:
- [ ] "Copy Checked Items" button appears when at least one item is checked
- [ ] Button copies checked items in paste-friendly format (ingredient + quantity, one per line)
- [ ] Copied format excludes confidence %, recipe context (clean for external apps)
- [ ] Visual feedback confirms successful copy (toast/checkmark)
- [ ] Works alongside existing "Copy All" functionality (don't break current workflow)

**From LEARNINGS.md**: Copy-paste to shopping app already works (line 346), but copying all items when you only need some is wasteful

---

### Story 3: Global Ingredient Purchase Statistics
**As a** system
**I want** to track which ingredients are purchased vs skipped across sessions
**So that** I can learn each household's actual pantry staples over time

**Acceptance Criteria**:
- [ ] When user checks items in shopping list, system records ingredient-level stats
- [ ] Track per ingredient (lowercase normalized): sessions observed, times purchased, times skipped
- [ ] Only record stats when user explicitly "marks list reviewed" (positive engagement signal)
- [ ] Stats persist globally across all sessions (not session-scoped)
- [ ] Stats are ingredient-name based (not recipe-specific)
- [ ] Initial implementation: collect data only, don't use it yet (foundation for Story 5)

**From LEARNINGS.md**: "How does system learn what user considers Pantry Staples?" (line 231) - this story answers that question

---

### Story 4: Engagement Tracking for Valid Feedback
**As a** system
**I want** to distinguish "user had everything in stock" from "user didn't review the list"
**So that** absence of purchases doesn't incorrectly signal "everything is a pantry staple"

**Acceptance Criteria**:
- [ ] "Mark as Reviewed" action explicitly signals user engaged with list
- [ ] Reviewing with NO items checked = valid signal (had everything)
- [ ] Reviewing with SOME items checked = valid signal (purchased those, skipped rest)
- [ ] Not reviewing = no stats recorded (ambiguous data rejected)
- [ ] User can review list multiple times (e.g., checking off as they shop)
- [ ] Review status persists with session (can see "Reviewed on Dec 20")

**From LEARNINGS.md**: Need positive signal that user engaged to distinguish valid "skip" from "didn't check list" (user request, question 6)

---

### Story 5: Bayesian Likelihood Refinement (Nice-to-Have)
**As a** meal planner
**I want** the system to learn from my past shopping selections
**So that** grocery lists get smarter over time and pantry guesses improve

**Acceptance Criteria**:
- [ ] When generating shopping list, use historical stats to refine purchase_likelihood
- [ ] Bayesian update: LLM prior (current likelihood) + historical data → posterior likelihood
- [ ] Example: Onions had 0.8 prior, but skipped 10/11 times → posterior drops to ~0.2
- [ ] Example: Goat cheese had 0.3 prior, but purchased 8/8 times → posterior rises to ~0.9
- [ ] Updated likelihoods affect grocery/pantry split (threshold still 0.3)
- [ ] Updated likelihoods affect sort order (high confidence items first)
- [ ] Historical data also improves recipe generation (pantry staples list refinement)

**From LEARNINGS.md**:
- Likelihood-based ingredient sourcing enables this (line 251-258)
- Feedback loop opportunity to improve pantry accuracy (line 233)
- User vision: "Bayesian approach - priors from LLM, updated by historical data" (user request, question 5)

---

## Prototype Contrast

| Aspect | Prototype | MVP | Why Change |
|--------|-----------|-----|------------|
| **Interaction** | Passive display | Active selection (checkboxes) | Shopping workflow needs "check off what I need" |
| **Filtering** | Show all items | Toggle "Items to Buy" filter | Focus on what's missing from pantry |
| **Copy behavior** | Copy all items | Copy checked items only | Clean paste into shopping apps (no manual filtering) |
| **Data capture** | None | Track purchase vs skip per ingredient | Foundation for learning pantry staples |
| **Likelihood source** | LLM only | LLM prior + historical data (Story 5) | Learn from user's actual pantry over time |
| **Selection persistence** | N/A | Session-scoped | Survives page refresh, cleared after shopping trip |
| **Stats persistence** | N/A | Global across sessions | Accumulate pantry knowledge over weeks/months |

**Preserve from Prototype**:
- Likelihood-based Grocery/Pantry split (≥0.3 threshold)
- Recipe context ("used in: Recipe A, Recipe B") - helpful for decision-making
- Confidence % display - useful for judging LLM accuracy
- Intelligent quantity aggregation - already works well
- Sort by likelihood DESC (high confidence first)

**Add to Prototype**:
- Checkboxes for active selection
- Filter toggle (checked only vs all)
- Copy-checked-only button
- "Mark as Reviewed" engagement signal
- Global ingredient purchase statistics table
- Bayesian likelihood refinement (nice-to-have)

**Don't Change**:
- Grocery items vs Pantry staples structure (already validated)
- Display format (ingredient, quantity, confidence, recipes) - works well

---

## Out of Scope (Deferred)

Explicitly NOT part of this feature:

- **External app integrations**: Direct export to Mealboard, Out of Milk, etc. - Deferred because copy-paste already works and integration APIs add complexity
- **WHY tracking**: Recording reasons for skipping (already have it, substituting, etc.) - Deferred because simple buy/skip is sufficient for Bayesian learning
- **Automatic pantry updates**: Immediately updating household Pantry Staples definition - Deferred because data collection must come first, premature updates risk bad data
- **Multi-store selection tracking**: Which items to buy from which store - Deferred because out of scope for MVP (MVP-CHARTER.md line 91: multiple stores explicitly out of scope)
- **Ingredient substitution preferences**: "Don't like dill" tracking - Deferred to separate feature (LEARNINGS.md:179, Priority 3 in MVP-CHARTER)
- **Recipe-level feedback**: "Made this recipe, didn't use X ingredient" - Different feature domain

**Future Features This Enables**:
- Automatic pantry staples refinement (LLM prompt updates based on stats)
- Recipe generation improvements (better ingredient source assumptions)
- Shopping list pre-filtering ("Hide items I always have")
- Household pantry profile page (view/edit learned staples)

---

## Open Risks

**Risk: Data quality in early sessions**
- Problem: First few sessions have no historical data, Bayesian updates won't help yet
- Impact: Feature value delayed until ~5-10 sessions accumulate
- Mitigation: Story 1-4 deliver immediate value (interactive list), Story 5 (Bayesian) delivers future value. Progressive enhancement, not regression.

**Risk: Seasonal pantry changes**
- Problem: Holiday baking adds flour/sugar to pantry temporarily, then they're gone
- Impact: Stats might over-rotate to recent behavior
- Options:
  - A) Simple: Ignore seasonality for MVP (acceptable for hobby project)
  - B) Time-decay weighting (recent sessions weighted higher)
  - C) Manual override ("Mark as pantry staple" / "Remove from pantry")
- Suggest: Option A for MVP, revisit if it becomes painful in production

**Risk: Ingredient name normalization**
- Problem: "yellow onion" vs "onion" vs "sweet onion" - should these share stats?
- Impact: Stats fragmented across variations, Bayesian learning less effective
- Options:
  - A) Exact match only (simple but lossy)
  - B) LLM-based ingredient normalization (e.g., all onions → "onion")
  - C) Manual grouping UI ("Merge these ingredients")
- Suggest: Start with A (exact match), add normalization if fragmentation becomes painful

---

## Questions for Alignment

Before proceeding to technical planning:

1. **Story priority**: Are Stories 1-4 all essential for MVP, or should any be deferred?
2. **Story 5 timing**: Should Bayesian refinement be in initial implementation, or added after collecting ~10 sessions of data?
3. **Review workflow**: Is "Mark as Reviewed" button the right UX, or would auto-review on any checkbox interaction be simpler?
4. **Data visibility**: Should users see the stats being collected (transparency), or keep it invisible (avoid cognitive load)?
5. **Risk acceptance**: Are the identified risks (early session data quality, seasonal changes, ingredient normalization) acceptable for MVP?

---

## Technical Notes (For Future TIP)

**Database additions needed**:
- `ShoppingListSelection` table: session_id, ingredient_name, checked (boolean), reviewed_at (timestamp)
- `IngredientPurchaseStats` table: ingredient_name (PK), sessions_observed, times_purchased, times_skipped, last_updated

**API additions needed**:
- `PATCH /api/sessions/{id}/shopping-list/selections` - Update checkbox state
- `POST /api/sessions/{id}/shopping-list/review` - Mark as reviewed (records stats)
- `GET /api/stats/ingredients/{name}` - View stats for debugging (optional)

**Frontend state**:
- Session-scoped selection state (checkboxes)
- Filter toggle state (show all vs checked only)
- Copy button visibility (appears when checked items exist)

**Bayesian implementation (Story 5)**:
- Prior: LLM-generated purchase_likelihood (current behavior)
- Evidence: (times_purchased / sessions_observed) when sessions_observed ≥ 5
- Posterior: Weighted average favoring evidence as sessions accumulate
- Formula: `posterior = (prior * w_prior + empirical * w_evidence) / (w_prior + w_evidence)`
  where `w_evidence` grows with sessions_observed
