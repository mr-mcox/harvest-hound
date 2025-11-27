# Explore Domain Design Command

Generate a domain design proposal for: $ARGUMENTS

This command helps explore how the domain model should evolve to enable new capabilities or address design tensions. Use this when:
- You've identified a pain point or limitation in the current domain
- You need to design how domain concepts should change
- Multiple solution approaches are possible and need exploration

---

## Available Agents

**For understanding current state:**
- `domain-locator` - Finds relevant domain model sections
- `domain-analyzer` - Synthesizes domain understanding
- `code-locator` - Finds implementation examples
- `code-analyzer` - Explains how code currently works
- `thoughts-locator` - Finds related session notes/research
- `thoughts-analyzer` - Extracts insights from past work

---

## Process

### Step 1: Initial Message

I'll help you explore the domain design for: [topic from $ARGUMENTS]

Let me start by researching the current domain model and any related past work to understand the context.

Then wait while agents run...

### Step 2: Spawn Research Agents in Parallel

Immediately spawn these agents concurrently to gather context:

**Domain Context**:
- Use `domain-locator` to find relevant sections in docs/architecture/domain-model/
- Use `domain-analyzer` to understand current domain concepts and relationships

**Code Context** (if implementation exists):
- Use `code-locator` to find related implementation files
- Optionally use `code-analyzer` on key files to understand current approach

**Historical Context**:
- Use `thoughts-locator` to find related sessions, research, or decisions
- If relevant docs found, use `thoughts-analyzer` to extract key insights

Wait for ALL agents to complete before proceeding.

### Step 3: Synthesize Research Findings

Based on my research, I understand the current state:

**Current Domain Model** (from domain-analyzer):
- [Key concepts involved with file:line refs]
- [Current responsibilities and boundaries]
- [Existing events and behaviors]

**Current Implementation** (from code-analyzer if relevant):
- [How it currently works with file:line refs]
- [Patterns in use]
- [Integration points]

**Past Context** (from thoughts-analyzer if relevant):
- [Related decisions or explorations]
- [Key insights from previous work]

**Problem Analysis**:
- [Specific gaps or tensions identified]
- [What the domain model doesn't currently support]
- [Where flexibility is constrained or missing]

### Step 4: Ask Clarifying Questions

Now I need to understand the design space better. Questions that my research couldn't answer:

**Scope & Priority**:
- [Question about what aspects are most important]
- [Question about priority or urgency]

**Design Constraints**:
- [Question about must-preserve behaviors]
- [Question about acceptable tradeoffs]

**Solution Space**:
- [Question about preferred approaches]
- [Question about future evolution needs]

Then WAIT for user responses before proceeding.

### Step 5: After User Responses

Thank you. Based on your answers, I'll now explore design alternatives.

[If user provided a problem brief or opportunity doc, acknowledge and reference it]

### Step 6: Generate Design Proposal

Create a comprehensive domain design proposal following the template at `docs/templates/domain-design-proposal.md`.

The proposal should include:

**Problem Context Section**:
- What's not working (synthesized from research and user input)
- Current domain limitations with specific file:line references
- User impact

**Design Alternatives** (2-3 distinct approaches):
For each alternative:
- Core idea and domain changes required
- **Supple design analysis** - what becomes easier/harder
- Domain concepts affected with references to current domain-model/
- Integration points and implementation complexity
- Risks and concerns

**Recommended Approach**:
- Which alternative and why
- Clear rationale based on flexibility, clarity, and pragmatism
- Borrowed elements from other alternatives if combining ideas

**Detailed Domain Model Changes**:
- Specific modifications to specific domain-model/ files
- Diff previews showing proposed changes

**Use Cases Validated**:
- Existing use cases that must still work
- New use cases enabled by this design
- Edge cases with defined behavior

**Implementation Implications**:
- High-level phases
- Code areas affected
- Testing strategy
- Effort estimate (t-shirt size)

### Step 7: Present for Review

I've created a domain design proposal at:
`docs/development/domain-designs/domain-[feature-name].md`

The proposal explores [X] design alternatives for [problem]:
- **Alternative A**: [Brief description]
- **Alternative B**: [Brief description]
- **Alternative C** (if exists): [Brief description]

**Recommendation**: Alternative [X] because [brief rationale]

**Key Domain Changes**:
- [Specific high-level change]
- [Specific high-level change]

**Estimated Implementation**: [T-shirt size]

Please review the proposal and let me know:
- Does the recommended approach feel right?
- Are there design aspects that need more exploration?
- Should we proceed to update the domain-model/ files?

Then WAIT for user feedback.

### Step 8: After User Approval

Based on your approval, I'll now update the domain model files:

**Files to Update**:
- `docs/architecture/domain-model/[file].md` - [What sections]

[Make the specific changes to domain-model/ files as outlined in the proposal]

Domain model updated! The design proposal will remain in `docs/development/domain-designs/` until after implementation, then can be archived.

**Next steps**:
- Use `create-tip "[feature]"` when ready to plan implementation
- Or continue exploring design questions

---

## Quality Guidelines

**Good Domain Design Proposals**:
- Address real friction or limitations with evidence
- Explore meaningfully different alternatives (not just variations)
- Honest supple design analysis - what flexibility is gained/lost
- Clear about invariants and use cases that must be preserved
- Specific file:line references to current domain model
- Concrete domain changes, not vague aspirations
- Realistic effort estimates

**Supple Design Focus**:
Ask yourself for each alternative:
- Where do we need polymorphism vs conditionals?
- What intention-revealing interfaces clarify the design?
- Where should operations be side-effect-free?
- What are the natural conceptual contours?
- Where will we need future variations?
- What should be open for extension, closed for modification?

**Agent Usage Tips**:
- Always use domain-locator + domain-analyzer for context
- Use thoughts-locator if this is a recurring theme
- Code analysis is helpful if implementation exists to learn from
- Don't over-research - focus on what's needed for good design exploration

---

Remember: You're exploring design space to make an informed decision, not just documenting what to build. The goal is clarity about the domain model evolution before implementation.
