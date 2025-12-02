# Create Technical Implementation Plan Command

Generate a Technical Implementation Plan (TIP) for: $ARGUMENTS

This command creates a strategic implementation plan focused on sequencing, integration, and risk management. Use this when:
- You have a feature frame from `frame-feature` (recommended for MVP)
- You have a domain design proposal from `explore-domain-design`
- Or you have a clear, small feature that doesn't need framing (quick feature mode)

**Purpose**: Establish strategic direction for implementation. The TIP provides high-level phases and integration awareness - detailed file changes and specific tests come later in `plan-tasks`.

---

## Available Agents

**For focused context gathering:**
- `prototype-explorer` - Explores prototype code for patterns and current implementation
- `code-locator` - Finds implementation patterns and tests (if you need more examples)
- `code-analyzer` - Explains current implementation (if you need to understand existing code)
- `thoughts-locator` - Finds related past work (if context is needed)

**For MVP**: Primary context comes from `docs/LEARNINGS.md` and `prototype/` code. Use agents to explore prototype patterns worth preserving.

---

## Input Sources (Check in Order)

1. `.scratch/frame-[feature-name].md` - Feature frame from `frame-feature` (preferred for MVP)
2. `docs/development/design-decisions/decision-[name].md` - Domain design from `explore-domain-design`
3. `docs/LEARNINGS.md` + `prototype/` - Direct context for quick features

---

## Process

### Step 1: Initial Message

I'll help you create an implementation plan for: [topic from $ARGUMENTS]

Let me check for existing context...

Then continue immediately...

### Step 2: Check for Existing Context

**Check for feature frame first**:
- Look for `.scratch/frame-[feature-name].md`
- If found: "Found feature frame. I'll use this for user stories, acceptance criteria, and scope boundaries."

**Check for design decision**:
- Look for `docs/development/design-decisions/decision-[name].md`
- If found: "Found design decision. I'll use this for domain changes and integration points."

**If neither exists** (quick feature mode):
- "No frame or design decision found. This works for quick features."
- "Let me gather context from LEARNINGS.md and the prototype..."

Read the relevant input document(s) fully.

### Step 3: Build Focused Context

**If using feature frame**:
Extract from frame:
- Problem statement
- User stories (essential vs nice-to-have)
- Acceptance criteria (these become TDD seeds)
- Prototype contrast (what to preserve/change)
- Scope boundaries (in/out of scope)
- Open risks

**If using design decision**:
Extract from design decision:
- Design decision and rationale
- Domain changes (new/modified/removed concepts)
- Integration points
- Pain points to monitor

**For all cases**, explore prototype for context:

Use `prototype-explorer` or direct exploration to find:
- Current implementation patterns worth preserving
- Code examples to reference for similar features
- Test patterns to follow

**Context Budget Target**: ~800-2000 tokens of focused references

### Step 4: Optional Deep Dives

[Only if initial exploration flags areas needing deeper understanding]

If you need deeper analysis:
- Use `code-analyzer` on specific prototype files to understand current approach
- Use `thoughts-locator` for historical context on design decisions
- Read specific sections of `docs/LEARNINGS.md` for validated discoveries

### Step 5: Synthesize Understanding

Based on my research:

**From Feature Frame** (if applicable):
- Problem: [problem statement]
- Stories: [list with essential/nice-to-have]
- Key acceptance criteria: [these seed TDD]
- Scope: [in/out]

**From Design Decision** (if applicable):
- Design decision: [brief summary of chosen approach]
- Domain changes: [new/modified/removed concepts]
- Integration points: [systems affected]
- Pain points to monitor: [known complexity areas]

**From Prototype Exploration**:
- Implementation pattern to follow: `[file:line]` - [pattern name]
- Test pattern to follow: `[test file:line]` - [approach]
- Similar feature for reference: `[file:line]` - [what's relevant]

**From LEARNINGS.md**:
- Relevant validated discoveries: [list]
- Workflows that feel natural: [list]

### Step 6: Ask Clarifying Questions

Questions that research and context couldn't answer:

**Implementation Approach**:
- [Question about technical approach or sequencing]
- [Question about specific integration points]

**Testing Strategy**:
- [Question about test coverage needs]
- [Question about test data or scenarios]

**Scope Boundaries** (if no frame):
- [Question about what's in/out of scope]
- [Question about phasing decisions]

**Technical Details**:
- [Question requiring human judgment]
- [Question about non-functional requirements]

Only ask questions you genuinely cannot answer from the context.

Then WAIT for user responses before proceeding.

### Step 7: After User Responses

Thank you. Based on your input and the context, I'll create the strategic implementation plan.

### Step 8: Generate Strategic Implementation Plan

Create a TIP at `docs/development/tips/tip-[feature-name].md`.

**IMPORTANT - What belongs in the TIP**:
- ✅ Strategic phase groupings
- ✅ Sequencing rationale (why this order, dependencies)
- ✅ Integration points awareness (what systems are affected)
- ✅ Risk assessment and mitigation strategies
- ✅ High-level test strategy direction (TDD seeds from acceptance criteria)
- ✅ Effort estimates per phase

**What does NOT belong in the TIP** (plan-tasks will add these):
- ❌ Specific file:line references for code changes
- ❌ Specific test names or test case details
- ❌ Detailed code modification lists
- ❌ Granular success criteria checklists
- ❌ Step-by-step implementation instructions

The TIP should include:

**Metadata**:
```yaml
---
date: YYYY-MM-DD
feature: [feature-name]
status: draft
frame: .scratch/frame-[feature-name].md  # or "none"
estimated_effort: [XS/S/M/L/XL]
confidence: [High/Medium/Low]
tags: [relevant, tags]
---
```

**Context Section**:
- Problem statement (from frame or LEARNINGS.md)
- User stories if from frame (essential vs nice-to-have)
- Key acceptance criteria (TDD seeds)
- Scope boundaries (in/out of scope)
- Relevant prototype patterns to follow
- Key learnings that inform this feature

**Implementation Phases** (Use as many as needed - could be 2, could be 10):
For each phase:
```markdown
### Phase N: [Descriptive Name]

**Purpose**: [What this accomplishes and why it's sequenced here]

**Scope**: [High-level areas of work - domain model, API, UI, BAML, etc.]

**TDD Focus**:
- [Acceptance criterion this phase addresses]
- Test approach: [Unit/Integration/E2E]

**Key Considerations**:
- [Important design decision or constraint]
- [Integration point to be aware of]
- [Technical challenge to address]

**Dependencies**: [What must complete first, if any]

**Complexity**: [XS/S/M/L]
```

**Sequencing Logic**:
- Why this order minimizes risk
- Where parallel work is possible
- Where dependencies constrain sequencing
- How phases build on each other

**High-Level Test Strategy** (TDD throughout):
- Test-driven approach with red-green-refactor cycle per phase
- What kinds of tests are needed (unit, integration, e2e)
- Key scenarios to validate (from acceptance criteria)
- Testing approach per phase
- **Do NOT specify exact test names or assertions**

**Integration Points**:
- Backend: [General areas - API, models, services]
- Frontend: [General areas - components, state, UI flows]
- BAML: [Prompt changes if applicable]
- **Identify WHAT will be affected, not HOW to change it**

**Library Research** (only if needed):
- What needs investigation
- Why investigation is needed
- Decision criteria

**Risk Assessment**:
- High risks with mitigation strategies
- Medium risks to watch
- Contingency plans if risks materialize
- **Steering likelihood**: Areas that may need human decisions or course correction

**Implementation Notes**:
- **TDD**: Test-Driven Development throughout all phases
- Prototype patterns to follow (with file references)
- Prototype patterns to change (with rationale)
- Quality gates
- **General guidance, not specific code examples**

**Overall Complexity Estimate**:
- Overall t-shirt size (XS/S/M/L/XL)
- Confidence level (High/Medium/Low)
- Justification: What drives complexity (novel patterns, integration points, decision density, steering needs)

### Step 9: Present for Review

I've created the strategic implementation plan at:
`docs/development/tips/tip-[feature-name].md`

**Plan Overview**:
- **Phases**: [Number] phases
- **Complexity**: [T-shirt size] ([Confidence])
- **Key Risks**: [1-2 main risks]

**Phase Summary**:
1. Phase 1: [Name] - [Complexity] - [Brief purpose]
2. Phase 2: [Name] - [Complexity] - [Brief purpose]
3. Phase 3: [Name] - [Complexity] - [Brief purpose]
[etc.]

**Strategic Direction**:
- Sequencing rationale: [Why this order]
- Key integration points: [What systems affected]
- Risk mitigation: [Main strategy]

Please review the plan and let me know:
- Does the phasing make strategic sense?
- Are the integration points correctly identified?
- Do the risks and mitigations look right?
- Is the complexity estimate realistic?
- Should any phases be combined or split?

Then WAIT for user feedback and approval.

### Step 10: After Approval

Great! The strategic plan is approved and ready for detailed task breakdown.

**Next steps**:
- Use `plan-tasks "docs/development/tips/tip-[feature-name].md"` to add detailed task breakdown
- `plan-tasks` will interpret this strategic direction and add specific file changes, test cases, and deliverables
- The TIP will be updated in place with the tactical details

---

## Quick Feature Mode

For small, obvious features without a frame:

**When to skip frame-feature**:
- Feature is straightforward (e.g., "fix quantity editing regression")
- Scope is clear from LEARNINGS.md
- No user story ambiguity
- Single pain point with obvious solution

**Process adjustments**:
- Read LEARNINGS.md directly for context
- Explore prototype for current implementation
- Include brief problem statement in TIP (from learnings)
- Implicit acceptance criteria (what "done" looks like)
- Same phase structure, just lighter context section

---

## Quality Guidelines

**Good TIPs Focus On**:
- Strategic sequencing (why this order)
- Integration awareness (what's affected)
- Risk management (what could go wrong)
- Test strategy direction (TDD seeds from acceptance criteria)
- Effort estimates (how much work)

**Good TIPs Avoid**:
- Specific file paths and line numbers
- Exact test names and assertions
- Detailed code modification instructions
- Step-by-step implementation guides
- Granular checklists (those come in plan-tasks)

**Phase Scoping**:
- Use as many phases as needed - no magic number
- Small feature: might be 2-3 phases
- Complex feature: might be 7-10 phases
- Each phase should:
  - Have clear purpose
  - Enable subsequent phases
  - Be independently valuable where possible
  - Minimize coordination overhead

**Context Efficiency**:
- Feature frame is your primary context source when available
- Use prototype exploration to find patterns worth preserving
- Only use specific analyzers if you need to go deeper
- Don't gather context you won't use in the plan
- Quality over quantity - focused context beats comprehensive

**Agent Usage Tips**:
- For MVP: LEARNINGS.md + prototype exploration covers most needs
- Use code-analyzer for understanding complex prototype implementations
- Use thoughts-locator rarely (for historical context on past decisions)

**Complexity Estimate Guidance**:

*Note: This is spec-based development where Claude implements with human oversight. Estimates reflect cognitive complexity, decision density, and steering needs - not raw coding time.*

- **XS (Trivial)**: Clear pattern to follow, minimal decisions, Claude executes independently
  - Example: Add field to existing model following established pattern

- **S (Simple)**: Established patterns, few decision points, occasional steering
  - Example: Create new endpoint using existing endpoint as template

- **M (Moderate)**: Some novel patterns, multiple integration points, regular oversight needed
  - Example: New feature with multiple components but clear prototype patterns

- **L (Complex)**: Novel approach, many architectural decisions, frequent steering required
  - Example: Feature requiring new patterns not in prototype

- **XL (Very Complex)**: Unclear patterns, extensive decision-making, continuous collaboration
  - Example: Major refactor affecting multiple systems with new architectural patterns

**Complexity Factors**:
- Pattern novelty: Can Claude follow existing prototype examples or forge new ground?
- Decision density: How many judgment calls required?
- Context coordination: How much context must be held across files/systems?
- Integration points: How many systems must coordinate?
- Steering likelihood: How much human course-correction expected?

Complexity is per-phase; overall complexity considers how phases build on each other.

---

## Integration with Other Commands

**Input from**:
- `frame-feature` (`.scratch/frame-[feature-name].md`) - preferred for MVP
- `explore-domain-design` (`docs/development/design-decisions/decision-[name].md`) - for architectural decisions
- Direct (LEARNINGS.md + prototype) - for quick features

**Output to**: `plan-tasks` reads TIP and adds detailed tasks

**If architectural uncertainty surfaces**: Use `explore-domain-design` before continuing

**After implementation**: Delete TIP (code becomes source of truth)

---

## Remember: Strategic Direction, Not Tactical Details

**The TIP answers**:
- WHAT phases of work are needed
- WHY they're sequenced this way
- WHERE integration points exist
- WHAT risks need mitigation
- HOW MUCH effort is involved

**The TIP does NOT answer** (plan-tasks handles these):
- WHICH specific files to modify
- EXACTLY what tests to write
- HOW to implement specific features
- WHAT specific code changes to make

Trust `plan-tasks` to interpret your strategic direction and make it concrete with file paths, test names, and specific deliverables.
