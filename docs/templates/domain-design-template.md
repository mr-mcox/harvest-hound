# Domain Design: [Concept Name]

**Date Created**: [Date]  
**Domain Architect**: [Your name/role]  
**Status**: [Draft/Approved/Implemented]

## Source Documents
- **Opportunity**: `opportunities/[filename].md`
- **Concept Design**: `concepts/[filename].md`
- **Selected Concept**: [A/B/C] - [Concept Name]

## Executive Summary

[1-2 paragraphs summarizing what domain changes are needed to enable the selected concept and why these specific changes are the right approach]

---

## Domain Translation

Mapping user-facing concepts to domain concepts:

| User Concept | Current Domain Concept | Proposed Domain Change |
|--------------|------------------------|------------------------|
| "[What user calls it]" | [Existing concept or "None"] | [New/modified concept] |
| "[What user calls it]" | [Existing concept or "None"] | [New/modified concept] |
| "[What user calls it]" | [Existing concept or "None"] | [New/modified concept] |

---

## Domain Model Evolution

### New Bounded Contexts *(only if needed)*

#### [Context Name]
- **Purpose**: [Why this needs its own bounded context]
- **Core Responsibility**: [What it owns and manages]
- **Ubiquitous Language**: [Key terms within this context]
- **Relationships**: 
  - Upstream from: [Other contexts it depends on]
  - Downstream to: [Contexts that depend on it]
  - Shared kernel with: [Contexts sharing models]

### New Aggregates/Entities

#### [Entity Name]
- **Purpose**: [Core domain responsibility]
- **Aggregate Root**: [Yes/No - if No, which aggregate owns it]
- **Identity**: [How it's uniquely identified]

**Properties**:
- `id`: [Type and generation strategy]
- `property1`: [Type and purpose]
- `property2`: [Type and purpose]

**Invariants**:
- [Business rule this entity must always satisfy]
- [Another invariant]

**Commands**:
- `commandName(params)`: [What it does]
- `commandName(params)`: [What it does]

**Domain Events**:
- `EventName`: Emitted when [condition]
- `EventName`: Emitted when [condition]

### Modified Aggregates/Entities

#### [Existing Entity Name]

**Current State**:
- Responsibility: [What it does today]
- Key properties: [Current important fields]

**Proposed Changes**:

**New Properties**:
- `newProperty`: [Type and purpose]

**New Behaviors**:
- `newCommand(params)`: [What it enables]

**Modified Behaviors**:
- `existingCommand()`: Now also [what changes]

**New Events**:
- `NewEventName`: Emitted when [condition]

**Breaking Changes**: [Yes/No]
- If Yes: [Description of what breaks]
- Migration: [How to handle existing data]

### New Value Objects

#### [Value Object Name]
- **Purpose**: [What domain concept it represents]
- **Immutable Properties**:
  - `property1`: [Type and meaning]
  - `property2`: [Type and meaning]
- **Behaviors**:
  - `method()`: [What it computes/validates]
- **Validation Rules**: [What makes it valid]

### New Domain Services *(only if needed)*

#### [Service Name]
- **Purpose**: [Why this cross-aggregate coordination is needed]
- **Coordinates Between**: [Aggregate 1] ↔ [Aggregate 2]
- **Key Operations**:
  - `operation(params)`: [What it orchestrates]
- **Domain Events**: [Events it might emit]

---

## Event Design

### New Events

#### `[EventName]`
- **Context**: [Which bounded context]
- **Emitted By**: [Aggregate name]
- **Triggered When**: [Specific business condition]
- **Event Stream**: `[StreamName-{id}]`

**Payload**:
```json
{
  "eventId": "uuid",
  "aggregateId": "uuid", 
  "occurredAt": "timestamp",
  "data": {
    "field1": "value",
    "field2": "value"
  }
}
```

**Consumers**:
- [Handler/Projection]: [What it does with event]
- [Handler/Projection]: [What it does with event]

### Modified Events *(only if needed)*

#### `[ExistingEventName]`
- **Current Version**: v1
- **New Version**: v2
- **Changes**: [New fields added]
- **Compatibility**: [How to handle both versions]

---

## Behavioral Flows

### [Primary Behavior from Concept]

```
1. User Action: [What user does in UI]
   ↓
   HTTP POST /api/[endpoint]
   ↓
2. Command: [CommandName] 
   → Handler: [CommandHandler]
   → Aggregate: [AggregateName]
   → Validation: [What's checked]
   ↓
3. Event: [EventEmitted]
   → Stream: [stream-name]
   ↓
4. Projections:
   → [ProjectionName]: Updates [read model]
   → [ProjectionName]: Updates [read model]
   ↓
5. WebSocket: [EventName] 
   → Client receives: [UI update]
```

### [Secondary Behavior] *(if needed)*

[Similar flow structure]

---

## API Surface Changes

### New REST Endpoints

#### `POST /api/[resource]`
- **Purpose**: [What user action it supports]
- **Request Body**:
  ```json
  {
    "field1": "value",
    "field2": "value"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "id": "uuid",
    "status": "created"
  }
  ```

### Modified Endpoints

#### `GET /api/[existing-resource]`
- **Change**: Response now includes [new field]
- **Breaking**: [Yes/No]
- **Compatibility**: [How to handle]

### New WebSocket Events

#### `event_name`
- **When Emitted**: [Business trigger]
- **Payload Shape**:
  ```json
  {
    "type": "event_name",
    "data": {
      "field": "value"
    }
  }
  ```
- **Client Action**: [What UI should do]

---

## Technical Considerations

### Performance Impact
- **New Queries**: [Description and expected load]
- **Projection Complexity**: [Any expensive computations]
- **Event Volume**: [Expected events per action]

### Data Migration
- **Existing Data**: [What needs transformation]
- **Migration Strategy**: [How to migrate safely]
- **Rollback Plan**: [How to undo if needed]

### Consistency Boundaries
- **Transaction Scope**: [What must be atomic]
- **Eventual Consistency**: [What can be async]
- **Saga Requirements**: [Any long-running processes]

---

## Implementation Risks

### High Risk
- **[Risk Name]**: [Description]
  - Mitigation: [Approach to reduce risk]

### Medium Risk
- **[Risk Name]**: [Description]
  - Mitigation: [Approach to reduce risk]

### Open Questions
- [ ] [Technical question needing research]
- [ ] [Architectural decision needed]
- [ ] [Alternative approach to consider]

---

## Success Criteria

The domain model successfully enables the concept when:
- [ ] [Specific user behavior is possible]
- [ ] [Performance requirement is met]
- [ ] [Domain invariant is maintained]
- [ ] [Integration works correctly]

---

## Domain Model Updates Required

### Section: [Section Name in domain-model.md]
- Add new aggregate [Name] to the [Context] context
- Update relationships diagram to show [relationship]

### Section: [Domain Events]
- Add [EventName] to [Context] event catalog
- Update event flow example to include [behavior]

### Section: [Value Objects]
- Add [ValueObject] definition
- Update invariants to include [rule]

---

## Next Steps

1. Review domain design with team
2. Update domain-model.md with approved changes
3. Create Technical Implementation Plan (TIP)
4. Begin implementation with event schema design

---

*This domain design will be removed from the repository once the feature is implemented.*