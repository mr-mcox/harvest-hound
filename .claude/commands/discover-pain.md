# Discover Pain Point Command

Express and explore a friction point in the current prototype: $ARGUMENTS

## Purpose

Help the user articulate and understand pain points in the meal planning workflow. This drives what to implement next.

## Process

### Step 1: Understand the Pain

"I hear you're experiencing friction with: [restate the pain point]

Let me ask some clarifying questions to understand better:"

Then ask 2-3 targeted questions like:
- When does this friction occur in your workflow?
- What would ideal behavior look like?
- How often does this come up?

### Step 2: Connect to Domain

Map the pain to domain concepts:
- Which domain objects are involved? (Recipe, Store, Ingredient, MealPlan)
- Is this about data, workflow, or interaction?
- Does this reveal missing concepts?

### Step 3: Propose Experiment

Suggest a minimal implementation to test:
"We could try [specific change] to see if that helps. This would let us test whether [hypothesis]."

### Step 4: Set Success Criteria

Define what success looks like:
- How will we know if this helps?
- What would we observe if it works?
- What might we learn even if it doesn't?

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

## Output

End with a clear next step:
"Should we implement [specific experiment] to test this? We can have something working in ~30 minutes."

Then transition to `implement-discovery` command if approved.