# Capture Learning Command

Document insights from: $ARGUMENTS

## Purpose

Extract and preserve domain discoveries from implementation experiments. Focus on insights, not code.

## Process

### Step 1: Reflect on the Experiment

"Let's capture what we learned from [experiment description].

Based on your experience, let's document:"

### Step 2: Gather Insights

Ask targeted questions:

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

### Step 3: Update LEARNINGS.md

Add discoveries to appropriate sections:

```markdown
## Domain Model Discoveries
- Recipe states needed: [new insight]
- Store complexity: [simpler than expected]

## Workflows That Feel Natural
- [New workflow discovered]

## Technical Discoveries
- [Performance observation]
- [State management need]

## Use Cases
Essential:
- [Newly validated use case]

Not Needed:
- [Complexity we can skip]
```

### Step 4: Identify Patterns

Look for emerging patterns:
- Repeated pain points
- Consistent preferences
- Domain boundaries

### Step 5: Next Experiment

Based on learnings, suggest:
"Given what we discovered, we might want to explore [next pain point] next. 

Or we could deepen our understanding of [current area] by trying [variation]."

## Example Documentation

### After Testing Recipe Summaries

**Learning Captured:**
```markdown
## Domain Model Discoveries
- Recipe states needed: Summary → Full → Cooking
  - Users want progressive disclosure
  - Summary = name + 3 key ingredients + time
  - Full = all details for decision
  - Cooking = step-by-step mode

## Workflows That Feel Natural  
- Scan summaries → Pick 3-4 interesting → Deep dive on those → Commit to cook

## Technical Discoveries
- Streaming not needed for summaries (batch is fine)
- But streaming valuable for full recipe generation
- State: Need to track "considering" vs "committed" recipes

## Use Cases
Essential:
- Quick recipe scanning without overwhelm

Not Needed:
- Detailed nutrition info in summary
```

## Documentation Guidelines

### DO Document
✅ Actual user reactions
✅ Surprise discoveries
✅ Workflow preferences
✅ Complexity assessments
✅ Domain boundaries

### DON'T Document
❌ Code structure
❌ Implementation details
❌ TODOs
❌ Technical debt
❌ Future architecture

## Success Metrics

Good learning capture:
- Specific, not generic
- About domain, not code
- Reveals user preferences
- Challenges assumptions
- Guides next experiment

## Transition

"We've captured [key insight]. This suggests our domain model should [implication].

Ready to tackle the next pain point? Or should we explore this area deeper?"

Return to `discover-pain` for next cycle or suggest ending session if patterns are clear.