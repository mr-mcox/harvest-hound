# Discover Pain Point Command

Express and explore a friction point in the current prototype: $ARGUMENTS

## Purpose

Help the user articulate and understand pain points in the meal planning workflow. This drives what to implement next.

**Key Principle**: User input takes priority. The domain model is background vocabulary, not constraints. We're discovering what the domain SHOULD be.

---

## Background Context

When relevant, reference these for domain vocabulary (not as constraints):
- `docs/domain-model-reference.md` - Domain concepts and terminology
- `docs/LEARNINGS.md` - Previous discoveries (check for related insights)

---

## Process

### Step 1: Acknowledge and Explore Prototype

"I hear you're experiencing friction with: [restate the pain point]

Let me explore the current prototype to understand the context..."

**Use the `prototype-explorer` agent**:
- Topic: [pain point topic]
- Scope: Surface scan (enough to understand current behavior)
- Stop when: Can describe what the prototype currently does for this topic

### Step 2: Check for Related Open Questions

Use the `thoughts-locator` agent to search for related open questions:

**Agent Task**: "Search `docs/open-questions/` for questions related to: [pain point topic]

Return relevant question files with brief summaries."

If related questions found, inform user:

"I found related open questions we're already tracking:
- [question file]: [summary]

I'll read these for context and reference them in the pain analysis.
After we implement and test, `/capture-learning` will update or close
these questions based on what we discover."

Then READ the related question files for context to inform the pain analysis.

### Step 3: Understand the Pain

After exploration completes, ask 2-3 targeted questions:

"Based on what I see in the prototype, let me ask some clarifying questions:"

- When does this friction occur in your workflow?
- What would ideal behavior look like?
- How often does this come up?

Then WAIT for user responses.

### Step 4: Connect to Domain (Light Touch)

After user responds, map the pain to domain concepts (using domain-model-reference.md vocabulary if helpful):

- Which domain objects might be involved? (Recipe, Store, Ingredient, MealPlan, etc.)
- Is this about data, workflow, or interaction?
- Does this reveal something missing from our understanding?

**Note**: Don't force-fit into existing domain model. New concepts are valid discoveries!

### Step 5: Propose Experiment

Suggest a minimal implementation to test:

"We could try [specific change] to see if that helps. This would let us test whether [hypothesis]."

**Scope guidance for experiment**:
- Single behavior change (not a feature set)
- Minimal files touched (ideally 1-2)
- Observable outcome for user to evaluate

### Step 6: Set Success Criteria

Define what success looks like:
- How will we know if this helps?
- What would we observe if it works?
- What might we learn even if it doesn't?

### Step 7: Create Pain Analysis Document

Save structured analysis to `.scratch/pain-[sanitized-topic].md`:

```markdown
# Pain Analysis: [Topic]

**Date**: [YYYY-MM-DD]
**Status**: Ready for implementation

## Pain Point
[User's description in their words]

## Current Experience
[What the prototype does now - from exploration]

## Ideal Experience
[What user wants - from discussion]

## Domain Connections
[Which domain concepts are involved - light touch]
- Concepts: [list]
- Type: [data / workflow / interaction]
- New concept needed? [yes/no - if yes, describe]

## Proposed Experiment
**Change**: [specific implementation]
**Hypothesis**: [what we're testing]
**Scope**: [single behavior / minimal files]

## Success Criteria
- Observable outcome: [what user will see/do]
- Learning opportunity: [what we'll discover either way]

## Related Open Questions
(Optional - if this exploration relates to existing questions)

**This exploration extends/relates to**:
- `docs/open-questions/[relevant-question].md` - [brief context of how they relate]

**Workflow**: After implementing this experiment, use `/capture-learning [topic]` to:
- Update open questions with new insights
- Close questions that are fully answered
- Create new questions for uncertainties that surface

## Notes
[Any additional context]
```

### Step 8: Handoff

"I've saved the pain analysis to `.scratch/pain-[topic].md`.

Should we implement this experiment now? Use `/implement-discovery [topic]` when ready.

After implementation, use `/capture-learning [topic]` to document what we learned."

---

## Examples

### Example 1: Recipe Overload
**Pain**: "I get overwhelmed seeing full recipes immediately"
**Questions**:
- Would you prefer titles first, then expand?
- Or ingredients first to check availability?
**Experiment**: Show recipe names + key ingredients, click for details
**Success**: User feels in control, not overwhelmed

### Example 2: Inventory Tracking
**Pain**: "Marking ingredients as used is tedious"
**Questions**:
- Bulk operations or one at a time?
- When do you mark things used?
**Experiment**: "Cook this recipe" button that claims all ingredients
**Success**: One click instead of many

### Example 3: Substitution Confusion
**Pain**: "I don't know what I can substitute"
**Questions**:
- Common substitutions or everything?
- Automatic or manual approval?
**Experiment**: Show "could use X instead" suggestions
**Success**: User confidently makes swaps

---

## Quality Guidelines

**Good Pain Discovery**:
- User's words preserved, not reinterpreted
- Current behavior understood from prototype exploration
- Domain connections are suggestive, not constraining
- Experiment is minimal and testable
- Success criteria are observable

**Anti-patterns**:
- Forcing pain into existing domain model
- Over-scoping the experiment (multiple changes)
- Skipping user input to rely on assumptions
- Creating abstract solutions before understanding concrete pain
