# Design Decision: [Feature Name]

**Purpose**: [One sentence - what problem does this solve]

**Status**: Approved - Ready for Implementation

**Cleanup After Implementation**:
- Verify: [Key classes/files that should exist after implementation]
- Verify: Domain model updated in `docs/architecture/domain-model.md` [specific sections]
- Delete: This file after implementation complete

---

## Design Decision

**Chosen Approach**: [Name of selected alternative from exploration]

**Core Concept**: [2-3 sentences explaining the fundamental design idea]

**Why This Approach**: [Brief rationale - key factors that drove the decision]

---

## Domain Model Changes

**Affected Sections**: `docs/architecture/domain-model.md` [specific sections modified]

**New Concepts**:
- **[ConceptName]**: [Brief description of new domain concept and its responsibility]
- **[ConceptName]**: [Brief description]

**Modified Concepts**:
- **[ConceptName]**: [What changed and why]

**Removed Concepts** (if applicable):
- **[ConceptName]**: [What was removed and why]

---

## Key Relationships & Behaviors

**[Concept A] ↔ [Concept B]**:
- [How they interact or collaborate]
- [Key polymorphic patterns, delegation, or composition strategies]

**[Concept C] Responsibilities**:
- [What this concept is responsible for]
- [What it explicitly is NOT responsible for - important boundaries]

**[Concept D] ↔ [External System]**:
- [How domain concepts integrate with external systems like IngredientBroker, RecipePlanner, etc.]

---

## Use Cases Enabled

**New Capabilities**:
1. **[Use case name]**: [What users can now do that they couldn't before]
2. **[Use case name]**: [New capability enabled by this design]

**Preserved Behaviors**:
1. **[Existing use case]**: [How existing functionality continues to work]
2. **[Existing use case]**: [Behavior maintained despite domain changes]

**Edge Cases Defined**:
1. **[Edge case scenario]**: [How system behaves in this boundary condition]

---

## Implementation Considerations

**Integration Points**:
- **[System/Service]**: [How this domain change affects it, what needs to adapt]
- **[System/Service]**: [Integration implications]

**Pain Points to Monitor**:
- **[Known complexity area]**: [What to watch for during implementation, why it might be tricky]
- **[Potential friction point]**: [Alternative approach if this becomes a blocker]

**Event Sourcing Notes** (if applicable):
- [Event patterns required - discriminators, event versioning, etc.]
- [Aggregate reconstruction considerations]
- [Event stream partitioning or routing logic]

**Data Migration** (if applicable):
- [Migration approach from old to new domain model]
- [Backward compatibility considerations]

---

## Light Code Sketch (Conceptual Only)

[Include ONLY if helpful for understanding the design - focus on structure, not implementation]

```python
# Conceptual sketch - NOT detailed implementation
# Purpose: Illustrate polymorphic relationships and field semantics

class ConceptA(ABC):
    """[What this abstraction represents]"""
    common_field: Type  # [Semantic meaning]

    @abstractmethod
    def key_behavior(self, context) -> Result:
        """[What this polymorphic behavior accomplishes]"""
        pass

class ConceptB(ConceptA):
    """[What this concrete variant represents]"""
    specific_field: Type  # [Field semantic meaning - e.g., "LLM-facing instructions"]

    # Shows different implementation approach for key_behavior

class ConceptC(ConceptA):
    """[What this concrete variant represents]"""
    different_field: Type  # [Different field semantics - e.g., "Human-readable notes"]

    # Shows different implementation approach for key_behavior
```

**Key Design Patterns**:
- [Pattern name]: [Where and why it's used]
- [Pattern name]: [Where and why it's used]

---

## Glossary Updates (if needed)

**New Ubiquitous Language Terms**:
- **[Term]**: [Definition and usage in domain context]
- **[Term]**: [Definition]

**Modified Terms**:
- **[Term]**: [How definition or usage has changed]

---

**Next Step**: Use `create-tip "[feature-name]"` to plan implementation.

This design decision provides the domain context that `create-tip` will use to generate the Technical Implementation Plan (TIP).

**Note**: This file is scaffolding - delete it after implementation is complete and the code becomes the authoritative source of truth.
