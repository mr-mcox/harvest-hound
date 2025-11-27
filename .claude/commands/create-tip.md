# Create Technical Implementation Plan Command

Generate a Technical Implementation Plan (TIP) for: $ARGUMENTS

This command creates a strategic implementation plan focused on sequencing, integration, and risk management. Use this when:
- Domain model is clear (or you have a domain design proposal)
- You need to align on the implementation approach and sequencing
- You want to identify risks and dependencies before detailed task planning

**Purpose**: Establish strategic direction for implementation. The TIP provides high-level phases and integration awareness - detailed file changes and specific tests come later in `plan-tasks`.

---

## Available Agents

**For focused context gathering:**
- `architecture-context-builder` - Orchestrates locators to build minimal context package
- `domain-locator` - Finds relevant domain model sections (if you need to go deeper)
- `domain-analyzer` - Synthesizes domain understanding (if you need to go deeper)
- `code-locator` - Finds implementation patterns and tests (if you need more examples)
- `code-analyzer` - Explains current implementation (if you need to understand existing code)
- `thoughts-locator` - Finds related past work (if context is needed)

---

## Process

### Step 1: Initial Message

I'll help you create an implementation plan for: [topic from $ARGUMENTS]

Let me start by reading any related design decision documents to understand the full scope.

Then continue immediately...

### Step 2: Read Design Decision First

**If design decision exists**:
- Read `docs/development/design-decisions/decision-[name].md` fully
- Extract: design decision, domain changes, integration points, pain points to monitor
- Use this to inform targeted context gathering

**If no design decision exists**:
- Proceed directly to Step 3

### Step 3: Build Focused Context

Use `architecture-context-builder` to gather focused context (informed by design decision if available):

The context builder will spawn locators in parallel to find:
- Essential domain model sections (minimal, focused)
- Relevant code patterns and test examples
- Key architectural decisions that constrain implementation

**Context Budget Target**: ~800-2000 tokens of focused references

Wait for context builder to complete.

### Step 4: Optional Deep Dives

[Only if architecture-context-builder flags areas needing deeper understanding]

If context builder suggests deeper analysis:
- Use `domain-analyzer` on [specific sections] to understand [specific aspect]
- Use `code-analyzer` on [specific files] to understand [specific implementation]
- Use `thoughts-locator` for [specific historical context]

### Step 5: Read Additional Artifacts

**If this modifies existing features**:
- Read relevant sections of domain-model/ (from context builder)
- Understand: current behavior, integration points, constraints

### Step 6: Synthesize Understanding

Based on my research:

**Domain Context** (from architecture-context-builder):
- Key concepts: [list concepts, reference docs with file:line]
- Relevant behaviors: [specific aspects]
- Constraints: [specific rules to respect]

**Code Patterns** (from context builder):
- Implementation pattern to follow: `[file:line]` - [pattern name]
- Test pattern to follow: `[test file:line]` - [approach]
- Similar feature for reference: `[file:line]` - [what's relevant]

**Architecture Decisions**:
- [Relevant decision/principle]
- [How it constrains this work]

**From Design Decision** (if applicable):
- Design decision: [brief summary of chosen approach]
- Domain changes: [new/modified/removed concepts]
- Integration points: [systems affected]
- Pain points to monitor: [known complexity areas from domain design]

### Step 7: Ask Clarifying Questions

Questions that research and context couldn't answer:

**Implementation Approach**:
- [Question about technical approach or sequencing]
- [Question about specific integration points]

**Testing Strategy**:
- [Question about test coverage needs]
- [Question about test data or scenarios]

**Scope Boundaries**:
- [Question about what's in/out of scope]
- [Question about phasing decisions]

**Technical Details**:
- [Question requiring human judgment]
- [Question about non-functional requirements]

Only ask questions you genuinely cannot answer from the architectural context.

Then WAIT for user responses before proceeding.

### Step 8: After User Responses

Thank you. Based on your input and the architectural context, I'll create the strategic implementation plan.

### Step 9: Generate Strategic Implementation Plan

Create a TIP at `docs/development/tips/tip-[feature-name].md`.

**IMPORTANT - What belongs in the TIP**:
- ✅ Strategic phase groupings ("Refactor domain model", "Update event sourcing")
- ✅ Sequencing rationale (why this order, dependencies)
- ✅ Integration points awareness (what systems are affected)
- ✅ Risk assessment and mitigation strategies
- ✅ High-level test strategy direction
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
related_domain_design: [path if exists]
estimated_effort: [XS/S/M/L/XL]
confidence: [High/Medium/Low]
tags: [relevant, tags]
---
```

**Domain Context Section**:
- List relevant domain-model/ docs
- Summarize key concepts (reference, don't reproduce)
- Note domain changes if from a domain design
- **Keep references at doc level, not file:line level**

**Implementation Phases** (Use as many as needed - could be 2, could be 10):
For each phase:
```markdown
### Phase N: [Descriptive Name]

**Purpose**: [What this accomplishes and why it's sequenced here]

**Scope**: [High-level areas of work - domain model, events, API, etc.]

**Key Considerations**:
- TDD: Write tests for new behavior before implementation
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
- Key scenarios to validate (happy path, edge cases, error handling)
- Testing approach per phase
- **Do NOT specify exact test names or assertions**

**Integration Points**:
- Backend: [General areas - API, domain model, events, persistence]
- Frontend: [General areas - components, state, UI flows]
- External: [Services, LLMs, etc.]
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
- Architectural patterns to follow (reference docs)
- Key principles to maintain
- Quality gates
- **General guidance, not specific code examples**

**Overall Complexity Estimate**:
- Overall t-shirt size (XS/S/M/L/XL)
- Confidence level (High/Medium/Low)
- Justification: What drives complexity (novel patterns, integration points, decision density, steering needs)

### Step 10: Present for Review

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

### Step 11: After Approval

Great! The strategic plan is approved and ready for detailed task breakdown.

**Next steps**:
- Use `plan-tasks "docs/development/tips/tip-[feature-name].md"` to add detailed task breakdown
- `plan-tasks` will interpret this strategic direction and add specific file changes, test cases, and deliverables
- The TIP will be updated in place with the tactical details

---

## Quality Guidelines

**Good TIPs Focus On**:
- Strategic sequencing (why this order)
- Integration awareness (what's affected)
- Risk management (what could go wrong)
- Test strategy direction (what needs testing)
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
- Use architecture-context-builder first - it's designed for this
- Only use specific locators/analyzers if you need to go deeper
- Don't gather context you won't use in the plan
- Quality over quantity - focused context beats comprehensive

**Agent Usage Tips**:
- Architecture-context-builder is your primary tool - trust it
- Only spawn additional agents if context builder suggests it
- Code-analyzer for understanding complex existing implementations
- Domain-analyzer if domain model sections need deeper synthesis
- Thoughts-locator rarely needed (usually for brownfield projects)

**Complexity Estimate Guidance**:

*Note: This is spec-based development where Claude implements with human oversight. Estimates reflect cognitive complexity, decision density, and steering needs - not raw coding time.*

- **XS (Trivial)**: Clear pattern to follow, minimal decisions, Claude executes independently
  - Example: Add field to existing model following established pattern

- **S (Simple)**: Established patterns, few decision points, occasional steering
  - Example: Create new endpoint using existing endpoint as template

- **M (Moderate)**: Some novel patterns, multiple integration points, regular oversight needed
  - Example: Add event sourcing to new domain concept with multiple projections

- **L (Complex)**: Novel approach, many architectural decisions, frequent steering required
  - Example: Implement new bounded context with custom patterns

- **XL (Very Complex)**: Unclear patterns, extensive decision-making, continuous collaboration
  - Example: Major refactor affecting multiple systems with new architectural patterns

**Complexity Factors**:
- Pattern novelty: Can Claude follow existing examples or forge new ground?
- Decision density: How many judgment calls required?
- Context coordination: How much context must be held across files/systems?
- Integration points: How many systems must coordinate?
- Steering likelihood: How much human course-correction expected?

Complexity is per-phase; overall complexity considers how phases build on each other.

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
