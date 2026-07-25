---
date: 2025-12-31
feature: priority-pairing
status: draft
frame: docs/implementation/frame-priority-pairing.md
estimated_effort: M
confidence: Medium
tags: [baml, prompts, experimentation, testing]
---

# Technical Implementation Plan: Priority Pairing Test Harness

## Context

**Problem**: Current recipe generation prioritizes high-priority ingredients but tends to ignore low-priority inventory items, creating pantry accumulation. Goal is **session-level coverage**: use most/all urgent+high priority items within a planning session while making meaningful progress on medium+low priority items.

**The Invariant**: A successful planning session should use most (if not all) urgent/high items AND make a dent in medium/low items.

**From Feature Frame** (`frame-priority-pairing.md`):
- **Story 1**: Session-level priority coverage - After 5-recipe session, use ~3 urgent, ~4 high, ~2-3 low items
- **Story 2**: Natural ingredient pairing - Culinarily sound, not forced
- **Four approaches to test**:
  - A: Prompting Enhancement (guide LLM to balance coverage)
  - B: Secondary Workflow (pre-generation ingredient pairing/bundling)
  - C: Randomized Promotion (algorithmic boost/knockout of ingredients)
  - D: Multi-wave Generation (separate urgent-focused and pantry-focused pitch waves)

**Strategy**: Build test harness to compare all 4 approaches quantitatively (priority coverage %) and qualitatively (sample pitches for human review), using live production data snapshot.

**Current Implementation Patterns**:
- BAML prompt at `recipes.baml:32-89` - current single-dimensional priority guidance
- BAML tests at `recipes.baml:91-137` - assertion-based validation pattern
- Python tests at `test_pitch_generation.py` - comprehensive fixture-based approach
- Priority field on InventoryItem at `models.py:82` - low/medium/high/urgent values

**From Learnings**:
- Technique diversity prompting (technical.md:71-79) - prompt refinements successfully changed LLM behavior
- Structured meal planning workflow (workflows.md:37-44) - sessions organize by criteria
- LLM/code separation (technical.md:60-69) - LLM good at culinary decisions, code manages state

---

## Implementation Phases

### Phase 1: Live Data Capture Infrastructure ✓

**Purpose**: Capture snapshot of production database (household profile, pantry, grocery stores, inventory with priorities) as fixed test data for comparing approaches

**Scope**:
- Script to export live harvest.db data to JSON/Python fixture
- Preserves: household profile, pantry staples, grocery stores, full inventory with priorities
- Enables: Repeatable testing with authentic real-world data

**TDD Focus**:
- Verify captured data includes all necessary fields (priority, quantity, unit)
- Validate data can be loaded for test execution
- Test approach: Unit tests for capture/load functions

**Key Considerations**:
- Use DATABASE_URL environment variable to safely target harvest.db
- Capture timestamp and metadata (when snapshot taken, inventory composition summary)
- Format should be easy to inspect (JSON or Python dict) and easy to load in tests
- Consider capturing multiple scenarios if user has different inventory states

**Dependencies**: None (first phase)

**Complexity**: XS (straightforward data export)

---

### Phase 2: Test Harness Foundation

**Purpose**: Framework for running multiple approaches against same input data, with metrics calculation and comparison infrastructure

**Scope**:
- Base test harness structure (load snapshot, run approach, calculate metrics, store results)
- Metrics calculation for priority coverage % (urgent/high/medium/low usage)
- Result aggregation for cross-approach comparison
- Sample pitch selection for qualitative review

**TDD Focus**:
- Priority coverage calculation accuracy (given inventory priorities and generated pitches, correctly compute %)
- Metrics aggregation works across approaches
- Test approach: Unit tests for metrics functions, integration test for harness flow

**Key Considerations**:
- Each approach gets same input: snapshot inventory, household profile, pantry, stores
- Metrics needed: % of each priority tier used, ingredient diversity count, session-level coverage
- Sample output: Top 3-5 pitches per approach for qualitative comparison
- Design for extensibility (easy to add new metrics or approaches)

**Dependencies**: Phase 1 (needs captured data)

**Complexity**: S (straightforward framework, metrics calculation is simple math)

---

### Phase 3: Approach A - Prompting Enhancement

**Purpose**: Implement priority-balanced prompting approach - modify BAML prompt to guide LLM toward session-level coverage across priority tiers

**Scope**:
- Create variant of GenerateRecipePitches with enhanced prompt guidance
- Prompt modification: "Across all pitches, collectively use most urgent/high items AND incorporate some medium/low items"
- Add explicit pairing guidance: "Recipes combining urgent items with low-priority pantry items are encouraged"
- Keep technique diversity guidance intact

**TDD Focus**:
- BAML test with mixed-priority inventory validates prompt change
- Integration with test harness to measure coverage
- Test approach: BAML assertion tests + harness integration test

**Key Considerations**:
- Build on proven technique diversity prompting pattern (technical.md:71-79)
- Preserve existing priority system (time-to-spoil accuracy)
- LLM decides organically when pairing makes sense (no rigid rules)
- Monitor for quality degradation (forced awkward pairings)

**Dependencies**: Phase 2 (needs harness to measure effectiveness)

**Complexity**: S (prompt modification, proven pattern to follow)

---

### Phase 4: Approach B - Secondary Workflow (Pre-generation Pairing)

**Purpose**: Implement pairing workflow approach - analyze inventory before generation to create ingredient pairing suggestions/bundles

**Scope**:
- Pairing logic to identify "good pairing candidates" (urgent + low, high + medium)
- Could use LLM ("Which low-priority items pair well with these urgent items?") or heuristic logic
- Pass pairing hints to GenerateRecipePitches as additional context
- Generate recipes using suggested bundles

**TDD Focus**:
- Pairing logic produces sensible bundles (urgent herbs + low beans, high CSA + medium pantry)
- Bundles passed to BAML correctly influence generation
- Test approach: Unit tests for pairing logic, integration test with BAML

**Key Considerations**:
- Pairing logic complexity: Start simple (same category ingredients?), can use LLM if needed
- How to represent bundles in prompt context (list of suggested pairings?)
- Monitor for over-engineering - should feel lightweight
- Separation: pairing logic separate from recipe generation

**Dependencies**: Phase 2 (needs harness)

**Complexity**: M (new workflow step, potential LLM call for pairing, integration complexity)

---

### Phase 5: Approach C - Randomized Promotion/Knockout

**Purpose**: Implement algorithmic approach - randomly adjust which ingredients LLM sees to achieve statistical coverage over time

**Scope**:
- Strategy implementation (choose one or test multiple):
  - Promotion: Randomly boost some low-priority items to appear high-priority
  - Knockout: Randomly exclude some items to force consideration of others
  - Weighted sampling: Ensure LLM sees diverse priority mix in inventory
- Modify inventory input to GenerateRecipePitches based on strategy
- Maintain original priority data for metrics calculation

**TDD Focus**:
- Promotion/knockout logic correctly transforms inventory
- Randomization is deterministic for testing (seeded random)
- Coverage achieved statistically across multiple runs
- Test approach: Unit tests for transformation logic, statistical tests for coverage

**Key Considerations**:
- Randomization might frustrate user (unpredictable behavior)
- Need to test multiple runs to verify statistical coverage (not just single session)
- Which strategy performs best? May need to test all three
- Maintain traceability: which items were promoted/knocked out

**Dependencies**: Phase 2 (needs harness)

**Complexity**: S-M (algorithmic logic straightforward, but statistical validation adds complexity)

---

### Phase 6: Approach D - Multi-wave with Priority Filters

**Purpose**: Implement multi-wave approach - generate separate pitch waves with different priority emphasis, user selects from mixed pool

**Scope**:
- Wave 1: Current behavior (prioritize urgent/high)
- Wave 2: Promote medium/low items in prompt
- Each wave generates pitches independently with different priority guidance
- Combine waves for user selection (simulate user browsing both)
- For test harness: simulate user selecting from both waves proportionally

**TDD Focus**:
- Wave 1 and Wave 2 generate different priority distributions
- Combined pool offers session-level coverage
- Simulated selection achieves invariant (use urgent/high + some medium/low)
- Test approach: BAML tests per wave, integration test for combined coverage

**Key Considerations**:
- Builds on existing multi-wave pattern (workflows.md:31-35)
- Simulating user selection: how to model realistic behavior? (pick appealing pitches that balance coverage)
- UI impact: more waves = more cognitive load (but out of scope for test harness)
- Coverage emerges from mixed selection, not enforced per wave

**Dependencies**: Phase 2 (needs harness)

**Complexity**: M (multiple BAML variants, wave coordination, selection simulation)

---

### Phase 7: Metrics Calculation & Analysis

**Purpose**: Calculate comprehensive priority coverage metrics and ingredient diversity for all approaches

**Scope**:
- Priority coverage %: For each tier (urgent/high/medium/low), what % of items were used?
- Session-level coverage: Did session use most urgent/high AND some medium/low? (invariant check)
- Ingredient diversity: How many unique low-priority items incorporated?
- Recipe quality proxy: Avg blurb length, ingredient count distribution (detect degradation)

**TDD Focus**:
- Metrics calculation accuracy (given test inventory + pitches, correct %)
- Invariant detection ("passing" vs "failing" session coverage)
- Test approach: Unit tests with known input/output scenarios

**Key Considerations**:
- Primary metric: Priority coverage % (user specified)
- Secondary metrics: Diversity, quality proxies
- Thresholds for "success": e.g., ≥80% urgent/high used, ≥20% medium/low used
- Cross-approach comparison: Which approach best achieves invariant?

**Dependencies**: Phases 3-6 (needs approach results)

**Complexity**: S (metrics are straightforward calculations)

---

### Phase 8: Comparison Reporting

**Purpose**: Generate side-by-side comparison report with quantitative metrics AND sample pitches for qualitative human review

**Scope**:
- Comparison table: Approach A vs B vs C vs D with priority coverage %, diversity metrics
- Sample pitches: 3-5 representative pitches per approach showing ingredient usage
- Qualitative review prompts: "Which pitches feel natural?", "Which approach achieves invariant?"
- Output format: Markdown report for easy reading, JSON for potential automation

**TDD Focus**:
- Report generation produces valid output
- Sample selection is representative (diverse priority mixes)
- Test approach: Integration test for report generation

**Key Considerations**:
- Both quantitative (metrics table) AND qualitative (sample pitches) needed for decision
- Highlight invariant achievement: Does approach use most urgent/high + some medium/low?
- Make comparison easy: Side-by-side, clear winners/losers
- Include caveats: Approach C statistical (needs multiple runs), Approach D assumes user behavior

**Dependencies**: Phase 7 (needs metrics)

**Complexity**: S (report generation straightforward)

---

## Sequencing Logic

**Why this order**:
1. **Data first** (Phase 1): Need real production data to test against
2. **Framework second** (Phase 2): Infrastructure to run all approaches consistently
3. **Approaches in parallel** (Phases 3-6): Can be implemented independently once harness ready
4. **Metrics & reporting last** (Phases 7-8): Requires approach results

**Parallel work opportunity**: Phases 3-6 can be done in any order (independent implementations)

**Risk minimization**: Start with simplest approach (Phase 3: Prompting) to validate harness works, then add more complex approaches

---

## High-Level Test Strategy

**TDD throughout**:
- Phase 1: Unit tests for data capture/load
- Phase 2: Unit tests for metrics, integration test for harness
- Phases 3-6: BAML assertion tests + harness integration tests per approach
- Phase 7: Unit tests for metrics calculation
- Phase 8: Integration test for report generation

**Key scenarios to validate**:
- Live data capture preserves all necessary fields (priority, quantity, unit, household context)
- Each approach generates pitches using same input data
- Priority coverage metrics correctly calculate % usage per tier
- Sample pitches representative of approach behavior
- Report clearly compares approaches for decision-making

**Test data**:
- Primary: Live snapshot from harvest.db (authentic real-world data)
- Fallback: Synthetic but realistic mixed-priority inventory if live capture fails

---

## Integration Points

**Backend**:
- Models: InventoryItem (priority field), existing BAML client types
- Services: Existing inventory calculation patterns
- BAML: New function variants for different approaches, prompt modifications

**Script**:
- Standalone `scripts/test_priority_approaches.py`
- Database access: Read-only from harvest.db for capture
- No frontend changes (test harness only)

**Output**:
- Markdown report: `scripts/priority_approaches_comparison.md`
- JSON metrics: `scripts/priority_approaches_metrics.json` (optional)

---

## Risk Assessment

**High risk: Approach effectiveness uncertainty**
- Risk: None of the 4 approaches may achieve invariant consistently
- Mitigation: Test harness will reveal this quickly, can iterate prompts or combine approaches
- Contingency: If all fail, may need hybrid approach or different strategy

**Medium risk: Live data capture complexity**
- Risk: harvest.db schema mismatch, missing data, or capture errors
- Mitigation: Validate captured data completeness, fallback to synthetic data if needed
- Contingency: Manual data export or simplified capture

**Medium risk: Quality degradation from coverage pressure**
- Risk: Forcing coverage might create awkward/unappealing recipes
- Mitigation: Qualitative review catches this, metrics include quality proxies
- Contingency: Prioritize quality over coverage (accept lower coverage if quality suffers)

**Low risk: BAML prompt changes break existing tests**
- Risk: New prompt variants might fail existing assertions
- Mitigation: Create new function variants, don't modify existing GenerateRecipePitches
- Contingency: Revert prompt changes, iterate more carefully

**Steering likelihood: Medium-High**
- Prompt tuning (Phase 3) may need iteration based on results
- Pairing logic (Phase 4) may need refinement for good bundles
- Metrics thresholds (Phase 7) may need adjustment for "success" definition
- Human judgment needed to evaluate which approach feels best qualitatively

---

## Implementation Notes

**TDD**: Test-Driven Development throughout all phases - write tests first, especially for metrics calculation

**BAML Patterns to follow**:
- Function variants: Create new functions (GenerateRecipePitchesBalanced, GenerateRecipePitchesPairing, etc.) rather than modifying existing
- Test assertions: Use BAML `@@assert` for output validation (recipes.baml:115-119)
- Client configuration: Use existing AnthropicCreative client

**Database Safety**:
- Read-only access to harvest.db for capture (no writes)
- Use DATABASE_URL environment variable for safe targeting
- Validate before capture: Confirm harvest.db exists and has expected schema

**Experimentation mindset**:
- This is research/exploration, not feature delivery
- Goal is to identify best approach, not implement all 4 for production
- Expect iteration: First results inform refinements
- Document surprises: What worked/didn't work informs final implementation

**Quality gates**:
- All approaches use same input data (fair comparison)
- Metrics calculation validated with known test cases
- Sample pitches reviewed qualitatively (not just metrics)
- Report clearly communicates findings for decision-making

---

## Overall Complexity Estimate

**Overall**: M (Moderate)

**Confidence**: Medium

**Justification**:
- **Novel patterns**: Test harness is new (not in codebase), experimentation workflow unfamiliar
- **Decision density**: Multiple approaches to implement, metrics to define, thresholds to set
- **Integration complexity**: BAML variants, live data capture, cross-approach comparison
- **Steering needs**: Prompt tuning, pairing logic refinement, metrics interpretation require human judgment
- **Scope clarity**: Well-defined goal (compare 4 approaches) but implementation details fuzzy (what makes "good pairing"?)

**Complexity drivers**:
- Phases 1-2, 7-8: Simple (XS-S) - straightforward data/metrics/reporting
- Phase 3: Simple (S) - proven prompt pattern
- Phases 4-6: Moderate (M) - novel workflow, algorithm, or multi-wave coordination
- Overall: Moderate due to experimentation nature, multiple approaches, and steering needs
