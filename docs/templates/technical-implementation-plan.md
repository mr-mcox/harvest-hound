# Technical Implementation Plan (TIP): [Feature Name]

**Use Case**: [Brief reference to the driving use case]  
**Estimated Scope**: [XS/S/M/L/XL] - [Brief justification]  
**Target Value**: [Core user/business value being delivered]

---

## 1. Context & Problem Analysis

### Current State
- **Existing Code**: What relevant code/patterns are already in place?
- **Current Architecture**: How does the existing system handle related concerns?
- **Known Issues**: Any technical debt or limitations that impact this work?

### Problem Statement
- **Core Challenge**: What specific problem are we solving?
- **User Impact**: How does the current state affect users?
- **Technical Impact**: What technical problems need resolution?

### Architecture Fit Assessment
- **DDD Alignment**: Which bounded contexts are involved? Do they fit cleanly?
- **Event Sourcing**: How does this integrate with our event-driven patterns?
- **Existing Patterns**: What established patterns (Container/Presentation, etc.) apply?

---

## 2. Technical Approach & Design Decisions

### High-Level Strategy
[1-2 sentences describing the core technical approach]

### Key Design Decisions
| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| [Decision 1] | [Alt 1, Alt 2] | [Why this choice] |
| [Decision 2] | [Alt 1, Alt 2] | [Why this choice] |

### Pattern Applications
- **Patterns to Follow**: [Which existing patterns apply and how]
- **Anti-Patterns to Avoid**: [What NOT to do based on project guidelines]
- **New Patterns**: [Any new patterns being introduced]
- **Key Library APIs**: [Important APIs and patterns from current documentation]

### Research Recommendations *(Optional)*
- **[Research Area 1]**: [Why this might be worth investigating]
- **[Research Area 2]**: [Specific questions or patterns to explore]
- **[Research Area 3]**: [Performance or implementation details to research]

### Risk Assessment
- **High Risk**: [Items that could cause significant problems]
- **Medium Risk**: [Items that need careful attention]
- **Mitigation Strategies**: [How to reduce identified risks]

---

## 3. Implementation Architecture

### Bounded Context Impacts
- **[Context Name]**: [What changes, what's added, what's affected]
- **[Context Name]**: [What changes, what's added, what's affected]

### Event Flow Design
```
[User Action] → [Domain Event] → [Projection/Handler] → [Updated State]
```
- **New Events**: [Events being added]
- **Event Consumers**: [What responds to these events]
- **Event Schema**: [Key event structure decisions]

### Data Flow
- **Input Sources**: [Where data enters the system]
- **Processing Steps**: [How data flows through the system]
- **Output Destinations**: [Where processed data goes]

### Integration Points
- **REST Endpoints**: [New/modified API endpoints]
- **WebSocket Events**: [Real-time communication changes]
- **Database Schema**: [Schema changes or new tables]
- **LLM Integration**: [AI/LLM touchpoints]
- **Frontend Components**: [UI integration requirements]

---

## 4. Testing & Quality Strategy

### Testing Levels
- **Unit Tests**: [What domain logic needs isolated testing]
- **Integration Tests**: [What cross-service integration needs testing]
- **E2E Tests**: [What user journeys need end-to-end validation]

### TDD Strategy
- **Behaviors Requiring Tests**: [Specific behaviors that need test-driven development]
- **Setup-Only Work**: [Infrastructure/scaffolding that doesn't need tests]
- **Test Data Strategy**: [How to handle test data and fixtures]

### Quality Gates
- **Performance**: [Specific performance requirements]
- **User Experience**: [UX standards that must be met]
- **Data Integrity**: [Data consistency/safety requirements]
- **Integration Reliability**: [Cross-service reliability standards]

---

## 5. Implementation Sequencing

### Dependencies & Critical Path
1. **Foundation Work**: [What must be built first]
2. **Core Implementation**: [Main feature development order]  
3. **Integration Work**: [How pieces connect together]
4. **Polish & Optimization**: [Final refinements]

### Risk-First Approach
- **Highest Risk First**: [Tackle uncertain/difficult items early]
- **Proof of Concept**: [Any prototyping needed to validate approach]
- **Fallback Options**: [What to do if high-risk items fail]

### Incremental Value Delivery
- **Phase 1**: [Minimal viable implementation]
- **Phase 2**: [Enhanced functionality]
- **Phase 3**: [Full feature completion]

### Rollback Considerations *(Optional)*
- **Database Changes**: [How to undo schema/data changes if needed]
- **Event Schema**: [How to handle event format changes]
- **Breaking Changes**: [How to safely revert API/interface changes]

---

## 6. Task Breakdown Preview

### Major Work Streams
1. **[Stream 1 Name]** ([Size estimate])
   - [High-level description]
   - [Key deliverables]

2. **[Stream 2 Name]** ([Size estimate])
   - [High-level description]  
   - [Key deliverables]

3. **[Stream 3 Name]** ([Size estimate])
   - [High-level description]
   - [Key deliverables]

### Cross-Stream Dependencies
- **[Stream A] → [Stream B]**: [What dependency exists]
- **[Stream B] → [Stream C]**: [What dependency exists]

### Total Effort Estimate
**Overall Size**: [XS/S/M/L/XL]  
**Confidence**: [High/Medium/Low] - [Brief explanation]  
**Timeline Estimate**: [Rough development time estimate]

---

## 7. Success Criteria

### Definition of Done
- [ ] [Specific technical milestone]
- [ ] [User-facing capability]
- [ ] [Quality/performance threshold]
- [ ] [Integration requirement]

### Validation Approach
- **Technical Validation**: [How to verify the solution works correctly]
- **User Validation**: [How to confirm user value is delivered]
- **Performance Validation**: [How to verify performance requirements]

---

## Next Steps

1. **Review & Align**: [Any areas needing clarification or discussion]
2. **Risk Validation**: [Any high-risk items that need early validation]
3. **Task Generation**: [Ready to break down into detailed implementation tasks]

---

*TIP Created*: [Date]  
*Last Updated*: [Date]  
*Status*: [Draft/Approved/In Progress/Complete]