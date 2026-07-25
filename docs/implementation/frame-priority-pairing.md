# Feature Frame: Priority Pairing

**Date**: 2025-12-31
**Status**: Draft - Awaiting Alignment

---

## Problem Statement

The current recipe generation prioritizes high-priority ingredients but tends to ignore low-priority inventory items, creating pantry accumulation over time. The goal is **session-level coverage across priority tiers**: use most/all urgent+high priority items within a planning session while also making meaningful progress on medium+low priority items.

**The Invariant**: A successful planning session should use most (if not all) urgent/high items AND make a dent in medium/low items.

**From Pain Point** (`roadmap/pain-priority-pairing.md`):
- "I've got quite a few dried beans and while, yeah, they'll last a while, I've also had them sitting around for a year. They're technically low priority, but I want them worked in."
- "I don't want to pick a particular ingredient and artificially bump it in priority just to make it happen that week"
- User has "five types of dried beans - want system to work them in naturally with higher-priority ingredients"

**From Learnings** (`learnings/`):
- Priority system gap (domain.md:218-224): Time-to-spoil model is correct for urgency but incomplete for overall ingredient utilization
- Technique diversity prompting (technical.md:71-79): Prompt refinements successfully changed LLM behavior for ingredient variety
- Structured meal planning workflow (workflows.md:37-44): Sessions generate pitches per criterion, user selects from categories

---

## User Stories

### Story 1: Session-level priority coverage
**As a** meal planner
**I want** each planning session to use most/all urgent+high priority items AND make progress on medium+low priority items
**So that** I prevent CSA waste (urgent items) while also working through pantry accumulation (low items)

**Acceptance Criteria**:
- [ ] After a planning session (e.g., 5 recipes selected), most urgent+high priority items should be claimed/used
- [ ] At least some medium+low priority items should also be incorporated (not ignored completely)
- [ ] Example: If inventory has 3 urgent CSA items, 5 high-priority items, and 8 low-priority pantry items → session should use ~3 urgent, ~4 high, ~2-3 low items
- [ ] Coverage feels balanced, not skewed entirely toward high-priority

**From learnings/**: Structured meal planning workflow (workflows.md:37-44) - sessions organize generation by criteria, systematic filling

### Story 2: Natural ingredient pairing
**As a** meal planner
**I want** recipes that elegantly combine different priority levels
**So that** pairing feels culinarily sound, not forced or awkward

**Acceptance Criteria**:
- [ ] When a recipe uses both urgent and low-priority items, pairing makes culinary sense (e.g., "White bean stew with fresh herbs" not "Canned beans with arbitrary CSA item")
- [ ] System doesn't force pairings that degrade recipe quality
- [ ] Individual recipes can focus on one priority level if that's what makes sense - coverage is session-level, not per-recipe requirement

**From learnings/**: LLM/code separation (technical.md:60-69) - LLM is good at culinary decisions, technique diversity prompting (technical.md:71-79) - prompt guidance shapes behavior

---

## Current State vs Target

| Aspect | Current | Target | Why Change |
|--------|---------|--------|------------|
| Priority guidance | "Prioritize higher-priority items" | "Prioritize higher-priority items BUT also look for pairing opportunities with lower-priority ingredients" | Low-priority items accumulate despite user wanting to use them |
| Recipe variety | Biased toward high-priority ingredients | Mix of high-priority-only AND mixed-priority recipes | Better overall inventory utilization |
| Prompt sophistication | Single-dimensional priority | Priority awareness with pairing guidance | Reflects two-dimensional user need (urgency + desire to use) |

**Build On**:
- Existing priority system (time-to-spoil remains accurate)
- BAML prompt structure (proven to respond well to guidance refinements)
- Technique diversity prompting pattern (similar prompt change that worked)

**Add**:
- Prompt guidance to encourage mixed-priority ingredient combinations
- Recognition that low-priority items still want utilization

**Change**:
- Shift from "prioritize high" to "prioritize high AND pair with low where natural"

---

## Out of Scope (Deferred)

Explicitly NOT part of this feature:
- **Separate 'want_to_use' database field**: Deferred - prompt solution is lower lift and sufficient
- **UI controls for pairing**: Deferred - always attempting pairing is acceptable, no toggle needed
- **Multi-dimensional priority model**: Deferred - keeping single priority (freshness) and solving via prompt
- **Rigid pairing rules**: Deferred - LLM organic decision-making preferred over coded logic

**Future Features This Enables**:
- User feedback on pairing quality could refine prompt further
- Analytics on which low-priority items get used vs accumulate

---

## Solution Approach: Open Question

**The challenge**: Session-level coverage across priority tiers is a goal, but the mechanism to achieve it is uncertain.

### Approach A: Prompting Enhancement
**Concept**: Update BAML prompt to guide LLM toward balanced priority coverage

**How it works**:
- Prompt instructs: "Across all pitches, collectively use most urgent/high items AND incorporate some medium/low items"
- LLM naturally balances coverage when generating multiple pitches
- No workflow or algorithmic changes

**Pros**:
- Simplest implementation (prompt-only change)
- Builds on proven technique diversity prompting pattern
- LLM can make culinary decisions about natural pairings

**Cons**:
- Less control over actual coverage (LLM might not achieve invariant consistently)
- Harder to guarantee "most urgent/high used"

**Risk level**: Low effort, but effectiveness uncertain

---

### Approach B: Secondary Workflow (Pre-generation Pairing)
**Concept**: Before generating pitches, analyze inventory and create ingredient pairing suggestions/bundles

**How it works**:
- Code identifies "good pairing candidates" (e.g., urgent herbs + low beans, high CSA veggies + medium canned goods)
- Pass these pairing hints to LLM as generation context
- LLM generates recipes using suggested bundles
- Could use LLM to identify pairings ("Which low-priority items pair well with these urgent items?")

**Pros**:
- More control over priority coverage
- Can explicitly target "use this urgent item WITH this low item"
- Pairing logic separated from recipe generation

**Cons**:
- More complex (new workflow step)
- Requires culinary knowledge (in code or separate LLM call)
- Might feel over-engineered for the problem

**Risk level**: Medium complexity, higher confidence in coverage

---

### Approach C: Randomized Promotion/Knockout
**Concept**: Algorithmically adjust which ingredients the LLM "sees" to achieve coverage

**How it works**:
- Strategy 1 - Promotion: Randomly boost some low-priority items to appear high-priority to LLM
- Strategy 2 - Knockout: Randomly exclude some items to force consideration of others
- Strategy 3 - Weighted sampling: Ensure LLM sees diverse priority mix in inventory input

**Pros**:
- Statistical coverage over time
- Simple algorithmic intervention
- No prompt complexity

**Cons**:
- Less predictable (randomness might frustrate user)
- Doesn't guarantee session-level invariant (just long-term balance)
- Might feel arbitrary ("why did it use THIS dried bean and not THAT one?")

**Risk level**: Medium complexity, coverage probabilistic not deterministic

---

### Approach D: Multi-wave Generation with Priority Filters
**Concept**: Generate pitches in multiple waves with different priority emphasis

**How it works**:
- Wave 1: Prioritize urgent/high items (current behavior)
- Wave 2: Promote medium/low items, generate pitches featuring them
- User browses/selects from both waves
- Session coverage emerges from mixed selection

**Pros**:
- User control (can see urgent-focused vs pantry-focused options)
- Clean separation of concerns
- Leverages existing multi-wave generation pattern (workflows.md:31-35)

**Cons**:
- More waves = more clicking/cognitive load
- User might skip wave 2 if wave 1 satisfies meal needs
- Doesn't enforce invariant, just offers options

**Risk level**: Medium complexity, relies on user behavior

---

### Recommendation for Exploration

**Suggest starting with Approach A (Prompting)** because:
1. Lowest implementation effort (aligns with "lower lift" assessment)
2. Can test quickly with production inventory
3. If insufficient, can layer on Approach B or D

**Then measure**: After prompt change, do you feel like sessions achieve the invariant? If not, which approach resonates for next iteration?

---

## Open Risks

**Risk: Approach uncertainty**
- We don't know which solution approach will best achieve the invariant
- Starting with prompting (Approach A) has lowest risk, but might not be sufficient
- May need to pivot to Approach B (pairing workflow) or D (multi-wave) if prompting insufficient
- **Resolution**: Start with Approach A, measure with production use, iterate if needed

**Risk: Coverage definition is fuzzy**
- "Most/all urgent+high" and "make a dent in medium/low" aren't precise
- Hard to test/validate without clearer metrics
- **Resolution**: Clarify in alignment questions - what does "success" look like quantitatively?

**Risk: Session size variability**
- A 3-recipe session has different coverage constraints than a 7-recipe session
- Invariant might need to be session-size-aware
- **Resolution**: Define expectations for typical session size (5 recipes?)

**Risk: Quality vs coverage tradeoff**
- Forcing coverage might degrade recipe quality (awkward pairings)
- Need balance between "use low-priority items" and "recipes should still be appealing"
- **Resolution**: Acceptance criteria require natural pairing, user can reject poor pitches

---

## Questions for Alignment

Before proceeding to technical planning:

1. **Solution approach preference**: Which approach resonates most? Start with Approach A (prompting) and iterate, or jump to Approach B/D for more control?

2. **Coverage definition**: What does "success" look like quantitatively for a typical 5-recipe session?
   - Example: "Use ≥80% of urgent/high items AND ≥20% of medium/low items"
   - Or qualitative: "Feel like I'm making progress on pantry, not just CSA"

3. **Session size**: What's a typical planning session size for setting expectations? (3 recipes? 5? 7?)

4. **Measurement approach**: How will we know if the solution works?
   - Option A: Subjective feel ("This session felt balanced")
   - Option B: Track coverage metrics (% of each priority tier used)
   - Option C: Track pantry accumulation over time (do low-priority items get used within N weeks?)

5. **Iteration tolerance**: If Approach A (prompting) doesn't achieve invariant, acceptable to try Approach B or D? Or prefer to get it right with one approach?
