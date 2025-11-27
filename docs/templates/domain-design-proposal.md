---
date: [YYYY-MM-DD]
feature: [feature-name]
status: [draft | approved | implemented | archived]
related_opportunity: [path/to/problem-brief if exists]
tags: [domain-modeling, relevant, tags]
---

# Domain Design: [Feature/Pain Point Name]

## Problem Context

### What's Not Working
[Describe the current limitation, pain point, or capability gap]

### User Impact
[How this affects users or development velocity]

### Current Domain Limitations
[Specific gaps or tensions in current domain-model/ docs with file:line references]
- `docs/architecture/domain-model/[file].md:line` - [Issue description]

---

## Design Alternatives Considered

### Alternative A: [Approach Name]

**Core Idea**
[One paragraph capturing the key insight behind this approach]

**Domain Changes Required**
- New aggregates/entities: [list]
- Modified concepts: [list with domain-model/ refs]
- New value objects: [list]
- New domain services: [list]

**Supple Design Analysis**
- **What becomes easier**: [specific use cases or extensions]
- **What becomes harder**: [tradeoffs or constraints introduced]
- **Flexibility gained**: [where this opens doors]
- **Flexibility lost**: [where this closes doors]

**Key Domain Concepts**
```
[Show the core domain structure]
Aggregate: Store
  - Behavior: availability()
  - Invariants: [rules that must hold]
```

**Integration Points**
[How this affects other bounded contexts]

**Implementation Complexity**: [High/Medium/Low]

**Risks & Concerns**
- [Specific risks with this approach]

---

### Alternative B: [Approach Name]

[Same structure as Alternative A]

---

### Alternative C: [Approach Name] *(if meaningfully different)*

[Same structure as Alternative A]

---

## Recommended Approach

**Selected**: Alternative [A/B/C]

**Rationale**
[Why this approach best balances simplicity, flexibility, and domain clarity]
-
-
-

**Borrowed Elements**
[If combining ideas from multiple alternatives]
- From Alternative X: [specific element]

**Future Evolution Path**
[How this approach can grow to handle anticipated changes]

---

## Detailed Domain Model Changes

### Modified Domain Model Files

#### `docs/architecture/domain-model/[file].md`

**Changes**:
- Line XX: Add new aggregate [Name]
- Section Y: Modify [Entity] responsibilities
- New section: [Service] behavior

**Diff Preview**:
```diff
+ New content
- Removed content
  Unchanged content
```

---

## Use Cases Validated

[Ensure existing and new use cases work naturally]

### Existing Use Cases (Must Preserve)
- [ ] [Use case 1] - Still works naturally
- [ ] [Use case 2] - No added complexity

### New Use Cases (Enabled by This Design)
- [ ] [New use case 1] - Now straightforward
- [ ] [New use case 2] - Clear handling path

### Edge Cases
- [ ] [Edge case] - Has defined behavior

---

## Implementation Implications

### High-Level Phases
1. [Phase 1]: [What needs to change]
2. [Phase 2]: [What depends on phase 1]
3. [Phase 3]: [Final integration]

### Code Areas Affected
- Backend: [specific modules/services]
- Frontend: [specific components]
- Database: [schema changes needed]
- Events: [new or modified event types]

### Testing Strategy
- Domain model tests: [what to verify]
- Integration tests: [key flows to test]
- Migration tests: [if changing existing behavior]

### Estimated Effort
[T-shirt size: XS/S/M/L/XL with brief justification]

---

## Open Questions

### Technical
- [Question that needs research or experimentation]

### Design
- [Aspect that could go multiple ways]

### Dependencies
- [External factors that might affect this]

---

## References
- Related domain designs: [links]
- Relevant ADRs: [links]
- Similar patterns in codebase: [file:line refs]
