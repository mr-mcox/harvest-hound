# Design Domain Changes Command

**Persona**: Domain Architect - focused on evolving the domain model to enable new capabilities

Generate domain design changes for concept: $ARGUMENTS

## Preparation Phase

### 1. Concept Understanding
Review the chosen concept design thoroughly:
- @$ARGUMENTS - The concept design to implement
- Identify the recommended concept (A/B/C)
- Extract key behaviors and mental models
- Note information architecture changes

### 2. Domain Model Analysis
Deep dive into current domain structure:
- @docs/architecture/domain-model.md - Current domain model
- @docs/architecture/overview.md - System architecture
- @docs/architecture/interface.md - API contracts
- Map user concepts from design to existing domain concepts
- Identify gaps and tensions

### 3. Event Sourcing Review
Understand current event flows:
- Review existing event definitions in domain model
- Identify event streams that might be affected
- Consider projection impacts

### 4. Related Domain Changes
Check for recent or planned domain evolution:
- @docs/development/domain-designs/ - Other domain changes in flight
- @docs/development/tips/ - Recent TIPs that modified domain

## Domain Design Process

### Part 1: Create Domain Design Document

Generate a domain design document that translates the concept into domain changes:

### Domain Design: [Concept Name]

**Source Documents**
- Opportunity: `docs/development/opportunities/[name].md`
- Concept: `docs/development/concepts/[name].md`
- Selected Concept: [A/B/C] - [Concept Name]

**Executive Summary**
Brief description of what domain changes are needed and why

---

## Domain Translation

Map user-facing concepts to domain concepts:

| User Concept | Current Domain Concept | Proposed Domain Change |
|--------------|------------------------|------------------------|
| [User's mental model] | [Existing concept or "none"] | [New/modified concept] |
| [User's mental model] | [Existing concept or "none"] | [New/modified concept] |

---

## Domain Model Evolution

### New Bounded Contexts *(if needed)*
- **Context Name**: Purpose and responsibilities
- **Justification**: Why this needs its own context
- **Relationships**: How it interacts with other contexts

### New Aggregates/Entities

#### [Entity Name]
- **Purpose**: Core responsibility in the domain
- **Key Properties**: Essential attributes
- **Invariants**: Business rules it enforces
- **Commands**: Operations it supports
- **Events**: Domain events it emits

### Modified Aggregates/Entities

#### [Existing Entity Name]
- **Current Responsibility**: What it does today
- **New Responsibility**: What it needs to do
- **New Properties**: Additional attributes needed
- **New Behaviors**: Additional operations
- **Breaking Changes**: Y/N - if yes, describe impact
- **Migration Strategy**: How to evolve existing data

### New Value Objects

#### [Value Object Name]
- **Purpose**: What it represents
- **Properties**: Immutable attributes
- **Behaviors**: Operations it supports

### New Domain Services

#### [Service Name]
- **Purpose**: Cross-aggregate coordination need
- **Key Operations**: What it orchestrates
- **Dependencies**: Which aggregates it works with

---

## Event Design

### New Events

#### [EventName]
- **Emitted By**: Which aggregate
- **Triggered When**: Specific conditions
- **Payload**: Key data included
- **Consumers**: Who needs to react

### Modified Events

#### [ExistingEventName]
- **Current Payload**: What it includes today
- **New Fields**: Additional data needed
- **Breaking Change**: Y/N
- **Compatibility Strategy**: How to handle versions

---

## Behavioral Flows

Document key domain behaviors using event flows:

### [Behavior Name]
```
1. User Action: [what user does]
   → Command: [domain command]
   → Aggregate: [which aggregate handles it]
   → Event: [what event is emitted]
   
2. Event Handler: [what reacts]
   → Side Effect: [what happens]
   → Event: [follow-up event]
   
3. Projection: [what read model updates]
   → Result: [what user sees]
```

---

## API Surface Changes

### New Endpoints Needed
- `[METHOD] /path` - [Purpose]
- Rough request/response shape

### Modified Endpoints
- `[METHOD] /path` - [What changes]
- Breaking change? Y/N

### New WebSocket Events
- `[event_name]` - [When emitted, what payload]

---

## Technical Considerations

### Performance Impact
- New queries or projections that might be expensive
- Increased event volume considerations

### Data Migration
- Existing data that needs transformation
- Event replay considerations

### Consistency Boundaries
- Transaction boundaries that change
- Eventual consistency implications

---

## Implementation Risks

### High Risk
- [Risk description and mitigation approach]

### Medium Risk
- [Risk description and mitigation approach]

### Open Questions
- Technical questions needing research
- Architectural decisions needed
- Alternative approaches to consider

---

## Success Criteria

How we know the domain model successfully enables the concept:
- [ ] [Specific capability enabled]
- [ ] [Performance requirement met]
- [ ] [Consistency guarantee maintained]

---

### Part 2: Update Domain Model Document

After creating the domain design artifact, propose updates to the main domain model:

1. **Analyze Impact**: Determine which sections of domain-model.md need updates:
   - New bounded contexts or components
   - Modified entity relationships
   - New events or commands
   - Updated invariants or behaviors

2. **Propose Changes**: Show the user specific changes to domain-model.md:
   ```markdown
   "I'll update the domain model with these changes:
   
   In Section X - [Section Name]:
   - Add new aggregate [Name] with [purpose]
   - Modify [Entity] to include [new behavior]
   
   In Section Y - Domain Events:
   - Add event [EventName] to [Context]
   ```

3. **Update Document**: After user approval, update domain-model.md:
   - Add new concepts in appropriate sections
   - Update diagrams if included in text
   - Ensure consistency across the document
   - Preserve existing content organization

## Output

1. Save domain design as: `docs/development/domain-designs/domain-[concept-name].md`
2. Update `docs/architecture/domain-model.md` with approved changes

The domain design artifact will be removed after implementation, but the domain-model.md updates persist as living documentation.

## Quality Checklist

Before finalizing, verify:
- [ ] All user concepts from design are mapped to domain concepts
- [ ] Domain changes enable the selected concept's key behaviors  
- [ ] Event flows support the interaction patterns
- [ ] Breaking changes are identified with migration strategies
- [ ] Technical risks are honestly assessed
- [ ] Changes maintain domain model consistency
- [ ] Updates to domain-model.md are clear and integrated

The domain design should provide enough detail for TIP creation while maintaining conceptual clarity.