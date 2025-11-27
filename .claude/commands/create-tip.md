# Create Technical Implementation Plan Command

Generate a Technical Implementation Plan (TIP) for: $ARGUMENTS

This command creates a detailed implementation plan with phased approach, test strategy, and effort estimates. Use this when:
- Domain model is clear (or you have a domain design proposal)
- You need to plan the implementation sequencing
- You want to identify risks and dependencies before coding

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

Let me start by gathering the minimal architectural context needed for this implementation.

Then continue immediately...

### Step 2: Build Focused Context

Use `architecture-context-builder` to gather focused context:

The context builder will spawn locators in parallel to find:
- Essential domain model sections (minimal, focused)
- Relevant code patterns and test examples
- Key architectural decisions that constrain implementation

**Context Budget Target**: ~800-2000 tokens of focused references

Wait for context builder to complete.

### Step 3: Optional Deep Dives

[Only if architecture-context-builder flags areas needing deeper understanding]

If context builder suggests deeper analysis:
- Use `domain-analyzer` on [specific sections] to understand [specific aspect]
- Use `code-analyzer` on [specific files] to understand [specific implementation]
- Use `thoughts-locator` for [specific historical context]

### Step 4: Read Related Artifacts

**If domain design exists**:
- Read `docs/development/domain-designs/domain-[name].md` fully
- Extract: recommended approach, domain changes, implementation implications

**If this modifies existing features**:
- Read relevant sections of domain-model/ (from context builder)
- Understand: current behavior, integration points, constraints

### Step 5: Synthesize Understanding

Based on my research:

**Domain Context** (from architecture-context-builder):
- Key concepts: [list with file:line refs]
- Relevant behaviors: [specific aspects]
- Constraints: [specific rules to respect]

**Code Patterns** (from context builder):
- Implementation pattern to follow: `[file:line]` - [pattern name]
- Test pattern to follow: `[test file:line]` - [approach]
- Similar feature for reference: `[file:line]` - [what's relevant]

**Architecture Decisions**:
- [Relevant decision/principle]
- [How it constrains this work]

[If domain design exists]:
**From Domain Design** (`docs/development/domain-designs/domain-[name].md`):
- Recommended approach: [brief summary]
- Domain changes needed: [high-level list]
- Implementation complexity: [assessment from design]

### Step 6: Ask Clarifying Questions

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

### Step 7: After User Responses

Thank you. Based on your input and the architectural context, I'll create the implementation plan.

### Step 8: Generate Implementation Plan

Create a comprehensive TIP following the template at `docs/templates/technical-implementation-plan.md`.

The plan should include:

**Domain Context Section**:
- List relevant domain-model/ docs with specific sections
- Summarize key concepts (reference, don't reproduce)
- Note domain changes if from a domain design

**Implementation Phases** (3-6 phases typically):
For each phase:
- **Purpose**: What this phase accomplishes and why it's sequenced here
- **Code Changes**: Specific files and modifications with file:line refs
- **Test Strategy**: Unit tests, integration tests, specific test cases
- **Success Criteria**: Testable outcomes, commands to verify
- **Dependencies**: What must complete first
- **Estimated Effort**: XS/S/M/L t-shirt size

**Sequencing Logic**:
- Why this order minimizes risk
- Where parallel work is possible
- Where dependencies constrain sequencing

**Key Test Scenarios** (3-5 scenarios):
- Happy path validation
- Key edge cases
- Error handling
- What each scenario proves

**Integration Points**:
- Backend APIs, database, events
- Frontend components, state
- External services, LLMs

**Library Research** (only if needed):
- What needs investigation
- Specific APIs or patterns to explore
- Alternative libraries being considered

**Risk Assessment**:
- High risks with mitigation strategies
- Medium risks to watch
- Contingency plans

**Implementation Notes**:
- Architectural patterns to follow (with refs from context builder)
- Code conventions (with file:line examples)
- Quality gates

**Total Effort Estimate**:
- Overall t-shirt size
- Confidence level (High/Medium/Low)
- Justification

### Step 9: Present for Review

I've created the initial implementation plan at:
`docs/development/tips/tip-[feature-name].md`

**Plan Overview**:
- **Phases**: [Number] phases
- **Effort**: [T-shirt size] ([Confidence])
- **Key Risks**: [1-2 main risks]

**Phase Breakdown**:
1. Phase 1: [Name] - [Effort] - [Brief purpose]
2. Phase 2: [Name] - [Effort] - [Brief purpose]
3. Phase 3: [Name] - [Effort] - [Brief purpose]
[etc.]

**Context Used** (~[X] tokens):
- Domain model: [Y] sections
- Code patterns: [Z] examples
- Test patterns: [N] examples

Please review the plan and let me know:
- Are the phases properly scoped and sequenced?
- Are the success criteria specific enough?
- Any technical details that need adjustment?
- Missing edge cases or considerations?
- Is the effort estimate realistic?

Then WAIT for user feedback and approval.

### Step 10: After Approval

Great! The TIP is approved and ready for task breakdown.

**Next steps**:
- Use `plan-tasks "docs/development/tips/tip-[feature-name].md"` to create detailed task breakdown
- Then use `implement-tasks` to start implementation

The TIP will remain in `docs/development/tips/` during implementation and can be archived after completion.

---

## Quality Guidelines

**Good TIPs**:
- Phases are independently testable and deliverable
- Success criteria are specific and verifiable
- Test strategy follows established patterns (from context)
- Sequencing minimizes risk and rework
- Effort estimates are realistic with stated confidence
- Integration points are clearly identified
- Risks have mitigation strategies

**Context Efficiency**:
- Use architecture-context-builder first - it's designed for this
- Only use specific locators/analyzers if you need to go deeper
- Don't gather context you won't use in the plan
- Quality over quantity - focused context beats comprehensive

**Phasing Principles**:
- Early phases enable later phases
- Each phase has clear value on its own
- Phases minimize dependencies and coordination
- Test incrementally as you go
- Database/schema changes come early
- Integration points identified per phase

**Agent Usage Tips**:
- Architecture-context-builder is your primary tool - trust it
- Only spawn additional agents if context builder suggests it
- Code-analyzer for understanding complex existing implementations
- Domain-analyzer if domain model sections need deeper synthesis
- Thoughts-locator rarely needed (usually for brownfield projects)

**Estimate Guidance**:
- XS: 1-2 hours
- S: 2-4 hours
- M: 4-8 hours (half day to full day)
- L: 1-2 days
- XL: 2-5 days

---

Remember: The TIP is about implementation sequencing and risk management. The domain model already defines WHAT to build - the TIP defines HOW to build it incrementally and safely.
