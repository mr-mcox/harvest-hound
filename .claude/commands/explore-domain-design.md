# Explore Domain Design Command

Generate a domain design proposal for: $ARGUMENTS

This command helps explore how the domain model should evolve to enable new capabilities or address design tensions. Use this when:
- You've identified a pain point or limitation in the current domain
- You need to design how domain concepts should change
- Multiple solution approaches are possible and need exploration

**Purpose**: Drive alignment on domain design decisions through exploration of alternatives. The output is ephemeral - used for discussion, then discarded after domain model is updated.

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

### Step 6: Generate Design Proposal (Ephemeral Discussion Document)

Create a design proposal for discussion. This is **NOT committed** - it's ephemeral scaffolding for alignment.

**Save to**: `.scratch/domain-design-[feature-name].md` (git-ignored)

The proposal should include:

**Problem Context Section**:
- What's not working (synthesized from research and user input)
- Current domain limitations with specific file:line references
- User impact (why this matters)

**Design Alternatives** (2-3 distinct approaches):
For each alternative:
- **Core idea**: High-level conceptual approach
- **Domain changes**: New concepts, modified responsibilities, changed relationships
- **Supple design analysis**: What becomes easier/harder, more/less flexible
- **Light code sketch** (if helpful): Class signatures, key method names, polymorphic relationships
  - Example: "Abstract base class X with polymorphic method Y()"
  - NOT: Full method implementations, test code, migration scripts
- **Tradeoffs**: Honest assessment of complexity vs flexibility gains
- **Integration implications**: How this affects IngredientBroker, RecipePlanner, etc.

**Recommended Approach**:
- Which alternative and why
- Clear rationale based on flexibility, clarity, and pragmatism
- Borrowed elements from other alternatives if combining ideas
- Key design principles that guided the decision

**Use Cases Validated**:
- Existing use cases that must still work (behavior preservation)
- New use cases enabled by this design (new capabilities)
- Edge cases with defined behavior (clarity on boundaries)

**Pain Points to Monitor**:
- Known complexity areas (e.g., "event sourcing with subclasses")
- Aspects that may need revision during implementation
- Alternative approaches to consider if pain points become blockers

### Step 7: Present for Review

I've created a design proposal for discussion at:
`.scratch/domain-design-[feature-name].md`

**Note**: This is an ephemeral discussion document - it will be deleted after we update the domain model.

The proposal explores [X] design alternatives for [problem]:
- **Alternative A**: [Brief description]
- **Alternative B**: [Brief description]
- **Alternative C** (if exists): [Brief description]

**Recommendation**: Alternative [X] because [brief rationale]

**Key Domain Changes**:
- [Specific high-level change]
- [Specific high-level change]

Please review the proposal and let me know:
- Does the recommended approach feel right?
- Are there design aspects that need more exploration?
- Should we proceed to update the domain-model/ files?

Then WAIT for user feedback.

### Step 8: After User Approval

Based on your approval, I'll now:

1. **Update domain model documentation**: `docs/architecture/domain-model.md`
2. **Create design decision document**: `docs/development/design-decisions/decision-[feature-name].md` (for TIP handoff)
3. **Delete ephemeral proposal**: Remove `.scratch/domain-design-[feature-name].md`

### Step 8a: Update Domain Model Files

Update `docs/architecture/domain-model.md` with the approved design changes:

**Files to Update**:
- `docs/architecture/domain-model.md` - [What sections being changed]

[Make the specific changes to domain model as outlined in the approved alternative]

### Step 8b: Create Design Decision Document (TIP Handoff)

Create a focused design decision at `docs/development/design-decisions/decision-[feature-name].md`:

```markdown
# Design Decision: [Feature Name]

**Purpose**: [One sentence - what problem does this solve]

**Status**: Approved - Ready for Implementation

**Cleanup After Implementation**:
- Verify: [Key classes/files that should exist after implementation]
- Verify: Domain model updated in `docs/architecture/domain-model.md` [specific sections]
- Delete: This file after implementation complete

---

## Design Decision

**Chosen Approach**: [Name of selected alternative]

**Core Concept**: [2-3 sentences explaining the fundamental design idea]

**Why This Approach**: [Brief rationale - key factors that drove the decision]

---

## Domain Model Changes

**Affected Sections**: `docs/architecture/domain-model.md` [specific sections]

**New Concepts**:
- [ConceptName]: [Brief description of new domain concept]
- [ConceptName]: [Brief description]

**Modified Concepts**:
- [ConceptName]: [What changed and why]

**Removed Concepts**:
- [ConceptName]: [What was removed and why]

---

## Key Relationships & Behaviors

**[Concept A] ↔ [Concept B]**:
- [How they interact]
- [Key polymorphic or delegation patterns]

**[Concept C] Responsibilities**:
- [What this concept is responsible for]
- [What it explicitly is NOT responsible for]

---

## Use Cases Enabled

**New Capabilities**:
1. [Use case name]: [What users can now do]
2. [Use case name]: [What users can now do]

**Preserved Behaviors**:
1. [Existing use case]: [Still works as before]
2. [Existing use case]: [Still works as before]

---

## Implementation Considerations

**Integration Points**:
- [System/Service]: [How this domain change affects it]
- [System/Service]: [How this domain change affects it]

**Pain Points to Monitor**:
- [Known complexity]: [What to watch for during implementation]
- [Potential friction]: [Alternative approach if this becomes blocker]

**Event Sourcing Notes** (if applicable):
- [Any event sourcing patterns or constraints]

---

## Light Code Sketch (Conceptual)

[Only if helpful for understanding the design]

```python
# Abstract concepts - NOT detailed implementation
class ConceptA(ABC):
    @abstractmethod
    def key_behavior(self) -> Result:
        """Polymorphic behavior that varies by subclass"""
        pass

class ConceptB(ConceptA):
    # Specific field semantics for this variant
    field_for_llm: str  # LLM-facing instructions

class ConceptC(ConceptA):
    # Different field semantics for this variant
    field_for_humans: str  # Human-readable notes
```

---

**Next Step**: Use `create-tip "[feature-name]"` to plan implementation.

This design decision provides the domain context that `create-tip` will use to generate the Technical Implementation Plan (TIP).
```

### Step 8c: Clean Up Ephemeral Files

Delete the discussion proposal: `.scratch/domain-design-[feature-name].md`

### Step 9: Present Completion

Domain model updated! Here's what was created:

**Committed Files**:
- ✅ Updated: `docs/architecture/domain-model.md` - [sections changed]
- ✅ Created: `docs/development/design-decisions/decision-[feature-name].md` - TIP handoff document

**Deleted Files** (ephemeral):
- 🗑️ Removed: `.scratch/domain-design-[feature-name].md` - Discussion proposal no longer needed

**Next steps**:
Run `create-tip "[feature-name]"` when ready to plan implementation. The TIP will use `decision-[feature-name].md` for domain context.

**Note**: The design decision file is scaffolding - it should be deleted after implementation is complete and the code becomes the authoritative source of truth.

---

## Quality Guidelines

**Good Design Exploration**:
- Focus on WHAT and WHY, not HOW
- Explore meaningfully different alternatives (not just variations)
- Honest supple design analysis - what flexibility is gained/lost
- Clear about invariants and use cases that must be preserved
- Specific file:line references to current domain model
- Concrete domain changes, not vague aspirations

**Code Sketches (When Helpful)**:
- ✅ Class signatures and inheritance hierarchies
- ✅ Key method names and polymorphic relationships
- ✅ Field semantics and their purposes
- ❌ Full method implementations
- ❌ Test code and test strategies
- ❌ Migration scripts or database schemas
- ❌ API endpoints or frontend components

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

## Remember

**This command is about design alignment, not implementation planning**:
- Explore alternatives to make informed decisions
- Create ephemeral discussion documents (not committed)
- Update permanent domain model documentation
- Produce focused handoff summary for TIP creation
- Delete discussion scaffolding after completion

The goal is clarity about domain model evolution before implementation, not exhaustive implementation documentation.
