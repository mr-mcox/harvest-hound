# Capture Learning Command

Document insights from: $ARGUMENTS

## Purpose

Extract and preserve domain discoveries from implementation experiments. Focus on insights, not code.

**Key Principle**: Learnings accumulate in `docs/LEARNINGS.md`. This is our discovery journal during prototype phase.

---

## Target Files

**Primary Output**:
- `docs/LEARNINGS.md` - Accumulated prototype discoveries

**Context Sources**:
- `.scratch/pain-[topic].md` - The pain analysis that drove this experiment
- `docs/domain-model-reference.md` - Domain vocabulary for connecting insights

---

## Process

### Step 1: Gather Context

Read the pain analysis document (if exists):
```
Read .scratch/pain-[topic].md
```

Read current learnings state:
```
Read docs/LEARNINGS.md
```

"Let's capture what we learned from the [topic] experiment.

**Original Pain**: [from pain analysis]
**Experiment**: [what we tried]
**Current LEARNINGS.md sections with content**: [list non-empty sections]"

### Step 2: Gather User Insights

Ask targeted questions based on what was tested:

**About the Domain:**
- Did this reveal new domain concepts?
- What relationships became clearer?
- What complexity was real vs imagined?

**About the Workflow:**
- What felt natural vs forced?
- Where did you want more/less control?
- What surprised you?

**About Technical Needs:**
- Was streaming/real-time important here?
- What state needed to persist?
- What could be ephemeral?

Then WAIT for user responses.

### Step 3: Connect to Domain Model

Optionally read domain model for vocabulary:
```
Read docs/domain-model-reference.md (relevant sections only)
```

Map insights to domain concepts:
- Which existing concepts does this clarify?
- Does this suggest new concepts?
- Does this challenge current assumptions?

**Note**: The domain-model-reference.md might be WRONG. Prototype learnings can reveal that our domain model needs to change.

### Step 4: Categorize Insights

Organize discoveries into LEARNINGS.md sections:

**Domain Model Discoveries** (Core Concepts, Workflows, Complexities):
- Recipe states, Store types, Ingredient handling
- Natural workflows discovered
- Surprising complexities or simplicities

**Technical Discoveries** (BAML, APIs, Performance):
- Prompt patterns that worked
- API shapes that felt right
- Performance observations

**Use Cases** (Essential, Nice to Have, Not Needed):
- Validated essential use cases
- Downgraded assumptions
- Things we can skip

**Architecture Decisions** (Keep Simple, Don't Need, Consider Adding):
- What we learned about needed complexity
- What we can definitively skip
- What might be worth adding

### Step 5: Update LEARNINGS.md

Make specific updates to `docs/LEARNINGS.md`:

```markdown
## Domain Model Discoveries

### Core Concepts
- [x] Recipe states needed: [specific insight from experiment]
- [x] Store types that matter: [specific insight]

### Workflows That Feel Natural
1. [x] [Specific workflow discovered]

### Surprising Complexities
- [x] [Complexity we didn't expect]

### Things Simpler Than Expected
- [x] [Simplicity we discovered]

## Technical Discoveries

### BAML Prompts That Work
- [x] Recipe generation: [what we learned]

### API Shapes That Feel Right
- [x] [Specific API pattern that worked]

## Use Cases (Keep Lean!)

### Essential (Must Have)
1. [x] [Validated use case]

### Not Needed
- [x] [Use case we can skip]
```

**Format Notes**:
- Mark discovered items with `[x]`
- Keep original template items with `[ ]` for future discoveries
- Add specific, concrete insights - not vague notes
- Include context ("discovered during recipe overload experiment")

### Step 6: Identify Patterns

Look for emerging patterns across learnings:
- Repeated pain points → fundamental domain need
- Consistent preferences → design principle
- Domain boundaries → context separation

### Step 7: Clean Up (Optional)

Ask user about ephemeral files:

"Would you like me to delete the pain analysis file?
`.scratch/pain-[topic].md` - No longer needed now that learning is captured.

[Delete / Keep for reference]"

### Step 8: Next Experiment

Based on learnings, suggest:

"Given what we discovered, we might want to explore [next pain point] next.

Or we could deepen our understanding of [current area] by trying [variation].

Use `/discover-pain [topic]` when ready for the next cycle."

---

## Example Update

### After Testing Recipe Summaries

**Updates to LEARNINGS.md:**

```markdown
## Domain Model Discoveries

### Core Concepts
- [x] Recipe states needed: Summary → Full → Cooking (progressive disclosure)
  - Summary = name + 3 key ingredients + time estimate
  - Full = all details for cooking decision
  - Cooking = step-by-step active mode
  (discovered: recipe-overload experiment, 2024-01-15)

### Workflows That Feel Natural
1. [x] Scan summaries → Pick 3-4 interesting → Deep dive → Commit to cook
   - Users want to browse before committing mental energy
   (discovered: recipe-overload experiment)

## Technical Discoveries

### Performance Observations
- [x] Streaming value: Not needed for summaries (batch fine), valuable for full recipe generation
  (discovered: recipe-overload experiment)

## Use Cases (Keep Lean!)

### Essential (Must Have)
1. [x] Quick recipe scanning without overwhelm
   - Validated: users light up when they see summary view

### Not Needed
- [x] Detailed nutrition info in summary view
  - Users don't look at it during selection phase
```

---

## Documentation Guidelines

### DO Document
- Actual user reactions ("she said 'oh, that's nice!'")
- Surprise discoveries (expected X, got Y)
- Workflow preferences (natural vs forced)
- Complexity assessments (simpler/harder than expected)
- Domain boundaries that emerged

### DON'T Document
- Code structure details
- Implementation specifics
- Technical debt
- Future architecture plans
- Speculative improvements

---

## Success Metrics

Good learning capture:
- Specific, not generic ("users want summary view" not "progressive disclosure good")
- About domain, not code
- Reveals user preferences
- Challenges or confirms assumptions
- Guides next experiment

---

## Handoff

"Learning captured in `docs/LEARNINGS.md`:
- [Section]: [Key insight]
- [Section]: [Key insight]

This suggests our domain model should [implication].

Ready for next pain point? Use `/discover-pain [topic]` to continue discovery cycle."
