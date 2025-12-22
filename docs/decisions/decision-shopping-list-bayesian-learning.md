# Decision: Shopping List Bayesian Learning with Query-Time Stats

**Date**: 2025-12-20
**Context**: Shopping List Selection & Pantry Learning feature implementation
**Status**: Accepted

## Decision

Use Bayesian likelihood refinement to learn which ingredients are actually pantry staples from user shopping selections. Derive purchase statistics at query time from reviewed selections (no separate stats table). Require explicit "Mark as Reviewed" engagement signal to distinguish valid feedback from ambiguous absence.

## Rationale

### The Learning Problem
LLM-generated purchase_likelihood predictions were less accurate than expected in production. Examples:
- Onions predicted 0.8 likelihood (definitely buy) but user skipped 10/11 times (had them)
- Goat cheese predicted 0.3 likelihood (maybe have) but user purchased 8/8 times (don't stock)

Without learning, every shopping list makes the same wrong guesses.

### Bayesian Approach
Combine LLM prior (initial guess) with empirical evidence (historical purchases):

```python
# Weight function: favor evidence as data accumulates
w_prior = max(5, 10 - sessions_observed)  # Starts at 10, drops to 5
w_evidence = sessions_observed  # Grows linearly

# Weighted average
posterior = (prior * w_prior + empirical * w_evidence) / (w_prior + w_evidence)
```

Early sessions: Trust LLM (has domain knowledge)
Later sessions: Trust user data (personalized behavior)

### Query-Time Stats (No Separate Table)
Derive stats from `ShoppingListSelection` records at query time:
```sql
SELECT
  ingredient_name,
  COUNT(*) as sessions_observed,
  SUM(CASE WHEN checked THEN 1 ELSE 0 END) as times_purchased
FROM shoppinglistselection
WHERE reviewed_at IS NOT NULL
GROUP BY ingredient_name
```

**Why no separate stats table**:
- Single source of truth (selections table)
- No data drift risk (stats always reflect current selections)
- No background jobs or update logic needed
- Query performance acceptable for current scale (hobby project)

### Engagement Tracking
"Mark as Reviewed" button explicitly signals user engaged with list:
- Reviewed with NO items checked = valid signal (had everything in pantry)
- Reviewed with SOME items checked = valid signal (purchased those, skipped rest)
- Not reviewed = no stats recorded (ambiguous - didn't shop? didn't look at list?)

Without engagement tracking, absence is ambiguous (can't tell "had it" from "didn't review").

## Alternatives Considered

- **Separate PurchaseStats table**: Extra maintenance, risk of data drift
  - Would need update triggers or background jobs
  - Stats could desync from selections if bugs exist
  - Not worth complexity for current scale

- **Auto-update pantry config**: Too aggressive, removes user control
  - Learning informs decisions, doesn't override user preferences
  - User should see stats and choose to update pantry definitions
  - Deferred to post-MVP

- **Implicit review (any checkbox = engagement)**: Ambiguous negative signal
  - User unchecks everything = "had everything" OR "gave up reviewing"
  - Can't distinguish without explicit review action

- **Separate WHY tracking**: Too much cognitive load for user
  - Would need "skip because pantry" vs "skip because changed mind" distinction
  - Binary checked/unchecked + review timestamp is simpler
  - Can infer "skip because pantry" from repeated skips

- **Per-household LLM fine-tuning**: Too expensive and slow
  - Bayesian approach gives similar benefits with zero training cost
  - Results available immediately (no training wait)
  - Can explain reasoning (weighted average, not black box)

## Trade-offs Accepted

**Limitations**:
- Exact ingredient name matching (no normalization)
  - "Yellow Onion" vs "Onion" tracked separately
  - Accepted: May fragment learning, but keeps logic simple
  - Can add grouping later if fragmentation becomes painful

- Cold start problem (first few sessions)
  - Bayesian weighting favors LLM prior when data is sparse
  - Takes 5-10 sessions to build reliable stats
  - Accepted: Gradual improvement is fine, better than never learning

- Query-time computation overhead
  - Stats aggregation runs on every shopping list generation
  - Accepted: Small data volume (hobby project), can cache later if needed

**Constraints**:
- Users must remember to "Mark as Reviewed" for learning to work
  - Requires UX to make this clear
  - Risk: Low engagement = no learning
  - Mitigation: Clear button label, success feedback, consider onboarding hint

## Consequences

**Enables**:
- Shopping lists get smarter over time (personalized to household)
- High-confidence items sorted first (less decision fatigue)
- Visible improvement from user perspective (see wrong guesses correct)
- Foundation for future pantry config suggestions

**Constrains**:
- Learning only works for reviewed sessions (requires user discipline)
- Stats are ingredient-name based (no recipe context)
- No "why" explanations (just binary purchased/skipped)

**Technical Debt**:
- No ingredient name normalization (may fragment stats)
- No stats visibility UI (learning is invisible to user)
- No automatic pantry updates (just data collection for MVP)

## Implementation Notes

**Bayesian Formula Details**:
- Prior: `purchase_likelihood` from recipe ingredient (LLM-generated)
- Empirical: `times_purchased / sessions_observed`
- Weighting: Favor LLM when data sparse, favor user data when abundant
- Threshold: 0.3 for grocery/pantry split (unchanged)

**Performance Considerations**:
- Stats aggregation: Single SQL query with GROUP BY
- Applied per ingredient during shopping list computation
- Acceptable for current scale (~50 ingredients per session)

## References

- Implemented in: PR #43 (feat: Shopping list selection)
- Original TIP: `docs/implementation/tip-shopping-list-selection.md` (deleted 2025-12-22)
- Related pain point: `docs/roadmap/pain-pantry-accuracy.md` (if exists)
- Related learnings:
  - `learnings/workflows.md`: Shopping list fills planning → shop → cook workflow
  - `learnings/technical.md`: Likelihood-based ingredient sourcing (≥0.3 = grocery, <0.3 = pantry)
  - `learnings/domain.md`: Pantry accuracy gap identified in production
