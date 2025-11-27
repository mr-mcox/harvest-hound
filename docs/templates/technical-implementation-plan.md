---
date: [YYYY-MM-DD]
feature: [feature-name]
status: [draft | approved | in_progress | complete]
related_domain_design: [path/to/domain-design if exists]
estimated_effort: [XS/S/M/L/XL]
confidence: [High/Medium/Low]
tags: [implementation, relevant, tags]
---

# Technical Implementation Plan: [Feature Name]

## Domain Context

**Relevant Domain Model Docs**:
- `docs/architecture/domain-model/[file].md` ([sections])
- Key concepts: [list core domain concepts this leverages]

**Domain Changes Required** *(if from domain design)*:
- [Summary of domain model changes, link to domain design doc]

---

## Implementation Phases

### Phase 1: [e.g., "Extend Core Domain Model"]

**Purpose**: [What this phase accomplishes and why it comes first]

**Code Changes**:
- `[path/file.py]:[line]` - [Specific change]
- `[path/file.py]` - [New file or major addition]
- Modify: [list files]
- Create: [list files]

**Test Strategy**:
- Unit tests: [What to test and where]
  - `tests/[path]/test_[name].py` - [Specific test cases]
- Integration tests: [If needed]
  - [Specific integration scenarios]

**Success Criteria**:
- [ ] [Specific testable outcome]
- [ ] [Specific testable outcome]
- [ ] Tests pass: `[command]`

**Dependencies**: None

**Estimated Effort**: [XS/S/M/L]

---

### Phase 2: [e.g., "Update API Layer"]

**Purpose**: [What this phase accomplishes]

**Code Changes**:
- [Specific file:line changes]

**Test Strategy**:
- [Specific testing approach]

**Success Criteria**:
- [ ] [Specific testable outcome]

**Dependencies**: Phase 1 complete

**Estimated Effort**: [XS/S/M/L]

---

### Phase 3: [e.g., "Frontend Integration"]

**Purpose**: [What this phase accomplishes]

**Code Changes**:
- [Specific file:line changes]

**Test Strategy**:
- [Specific testing approach]

**Success Criteria**:
- [ ] [Specific testable outcome]

**Dependencies**: Phase 2 complete

**Estimated Effort**: [XS/S/M/L]

---

## Library Research Needed

[Only if specific library investigation required for implementation]

### [Library Name]
- **Need**: [What we need to figure out]
- **Focus Areas**: [Specific APIs or patterns to research]
- **Alternatives**: [If exploring multiple options]

---

## Key Test Scenarios

[High-level test cases that give confidence the implementation is correct]

### Scenario 1: [Happy Path]
**Given**: [Initial state]
**When**: [Action taken]
**Then**: [Expected outcome]
**Validates**: [What this proves]

### Scenario 2: [Edge Case]
**Given**: [Initial state]
**When**: [Action taken]
**Then**: [Expected outcome]
**Validates**: [What this proves]

### Scenario 3: [Error Handling]
**Given**: [Initial state]
**When**: [Action taken]
**Then**: [Expected outcome]
**Validates**: [What this proves]

---

## Integration Points

**Backend**:
- [API endpoints affected]
- [Database changes]
- [Event types]

**Frontend**:
- [Components affected]
- [New UI elements]
- [State management changes]

**External**:
- [Third-party services]
- [LLM integration points]

---

## Data Migration

[Only if changing existing data structures]

**Migration Strategy**:
- [How to handle existing data]

**Rollback Plan**:
- [How to revert if needed]

**Testing Migration**:
- [ ] [Specific validation steps]

---

## Performance Considerations

[Only if performance is a concern]

**Expected Impact**:
- [Specific performance implications]

**Optimization Strategy**:
- [If needed, how to address]

**Monitoring**:
- [What to track]

---

## Risk Assessment

### High Risk
- **Risk**: [Description]
- **Mitigation**: [How to address]
- **Contingency**: [Backup plan]

### Medium Risk
- **Risk**: [Description]
- **Mitigation**: [How to address]

---

## Implementation Notes

**Architectural Patterns to Follow**:
- [Specific patterns from architecture docs with refs]
- Example: Event sourcing pattern from `docs/architecture/[file].md`

**Code Conventions**:
- [Testing patterns to follow with file:line refs]
- [Error handling patterns]

**Quality Gates**:
- [ ] All tests pass
- [ ] No linting errors
- [ ] [Specific performance requirement met]
- [ ] [Specific behavior validated]

---

## Total Effort Estimate

**Total**: [XS/S/M/L/XL]

**Confidence**: [High/Medium/Low]

**Justification**: [Why this estimate and confidence level]

---

## References
- Domain design: [link if exists]
- Related TIPs: [links]
- Similar implementations: [file:line refs]
