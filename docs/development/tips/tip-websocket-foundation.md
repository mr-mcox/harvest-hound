# Technical Implementation Plan (TIP): WebSocket Foundation for Real-time Inventory Updates

**Use Case**: Real-time inventory synchronization across multiple browser sessions/tabs
**Estimated Scope**: S - Simplified implementation leveraging existing event infrastructure
**Target Value**: Enable live inventory updates when users add ingredients in one session, automatically reflecting in other open sessions

---

## 1. Context & Problem Analysis

### Current State
- **Existing Code**: Complete event sourcing infrastructure with domain events (`StoreCreated`, `InventoryItemAdded`), event store, and projection handlers
- **Current Architecture**: REST-only API with synchronous request-response pattern, no real-time communication
- **Known Issues**: Users must manually refresh to see inventory changes made in other sessions

### Problem Statement
- **Core Challenge**: Implement WebSocket foundation to enable real-time inventory synchronization across multiple browser sessions
- **User Impact**: Currently, users working in multiple tabs/sessions miss inventory updates, leading to confusion and potential data conflicts
- **Technical Impact**: Need to bridge event-driven backend with real-time frontend communication

### Architecture Fit Assessment
- **DDD Alignment**: Clean fit with existing event sourcing - domain events can be broadcast via WebSocket
- **Event Sourcing**: Perfect integration point - existing event store can trigger WebSocket broadcasts
- **Existing Patterns**: Leverages established projection pattern and functional event generation (ADR-004)

---

## 2. Technical Approach & Design Decisions

### High-Level Strategy
Build WebSocket layer that broadcasts existing domain events from event store to subscribed clients, maintaining separation between domain logic and real-time communication.

### Key Design Decisions
| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| Invert event store dependencies with async event bus | Keep current synchronous projection calling | Decouples WebSocket broadcasting from projections, cleaner architecture |
| Default room approach for single-user | Global broadcasting vs complex room filtering | Simple now, clean migration path to multi-user later |
| FastAPI built-in WebSocket support | External WebSocket library (Socket.IO) | Minimal dependencies, consistent with FastAPI ecosystem |
| Skip graceful degradation for MVP | Implement REST polling fallback | Reduces complexity significantly, can add later if needed |
| Simple reconnection without state recovery | Complex missed-message handling | Much simpler implementation, sufficient for inventory updates |

### Pattern Applications
- **Patterns to Follow**: Event-driven architecture, functional event generation (ADR-004), container/presentation separation
- **Anti-Patterns to Avoid**: Mixing domain logic with WebSocket concerns, synchronous WebSocket handling
- **New Patterns**: Async event bus, default room pattern, simple reconnection strategy
- **Key Library APIs**: FastAPI WebSocket endpoints, JavaScript WebSocket API, async/await patterns

### Research Recommendations *(Deferred for Future)*
- **Multi-User Migration**: When adding user accounts, research room-based filtering patterns
- **State Recovery**: If simple reconnection proves insufficient, investigate missed message handling
- **Performance Optimization**: Monitor real usage to determine if filtering/optimization needed

### Risk Assessment
- **Medium Risk**: Event bus refactoring may affect existing projection handlers
- **Low Risk**: Simple WebSocket connection management, basic reconnection
- **Mitigation Strategies**: Thorough testing of event bus changes, gradual rollout of WebSocket features

---

## 3. Implementation Architecture

### Bounded Context Impacts
- **Inventory Context**: Event store extended with WebSocket broadcasting capability
- **Infrastructure Context**: New WebSocket connection management and message routing
- **UI Context**: Real-time event handling and state synchronization

### Event Flow Design
```
Domain Command → Event Store → Event Bus
                                  ↓
                    ┌─────────────┼─────────────┐
                    ↓             ↓             ↓
            Projection    WebSocket     Future
            Handlers     Broadcaster   Consumers
```
- **Architecture Change**: Invert dependencies - event store publishes to event bus, consumers subscribe
- **New Events**: No new domain events needed - reuse existing (`InventoryItemAdded`, `StoreCreated`)
- **Event Consumers**: Both projections and WebSocket broadcaster subscribe to event bus
- **Event Schema**: Existing domain events wrapped in WebSocket envelope

### Data Flow
- **Input Sources**: Domain commands via REST API
- **Processing Steps**: Event store → WebSocket publisher → Connection manager → Client broadcast
- **Output Destinations**: Connected WebSocket clients with filtered subscriptions

### Integration Points
- **REST Endpoints**: No changes to existing endpoints
- **WebSocket Events**: New `/ws` endpoint with default room (single-user MVP)
- **Database Schema**: No schema changes - leverage existing event store
- **LLM Integration**: No direct integration needed for MVP
- **Frontend Components**: New WebSocket client service, real-time event handling

---

## 4. Testing & Quality Strategy

### Testing Levels
- **Unit Tests**: WebSocket connection manager, event broadcasting logic, message serialization
- **Integration Tests**: Event store to WebSocket flow, client subscription management
- **E2E Tests**: Multi-session inventory updates, connection recovery scenarios

### TDD Strategy
- **Behaviors Requiring Tests**: Connection lifecycle, message broadcasting, subscription filtering
- **Setup-Only Work**: WebSocket endpoint configuration, dependency injection setup
- **Test Data Strategy**: Mock WebSocket connections, event fixtures from existing tests

### Quality Gates
- **Performance**: Sub-100ms message delivery for single-user scenario
- **User Experience**: Real-time updates work or fail cleanly (no degraded mode complexity)
- **Data Integrity**: Event ordering maintained, no duplicate events
- **Integration Reliability**: Simple reconnection, existing REST API unaffected

---

## 5. Implementation Sequencing

### Dependencies & Critical Path
1. **Foundation Work**: Refactor event store to use async event bus pattern
2. **Core Implementation**: WebSocket connection manager with default room, event broadcasting
3. **Integration Work**: Frontend WebSocket client with simple reconnection
4. **Polish & Optimization**: Error handling, basic performance monitoring

### Risk-First Approach
- **Highest Risk First**: Event store refactoring to avoid breaking existing projections
- **Proof of Concept**: Verify event bus pattern with existing projection handlers
- **Fallback Options**: REST API completely unaffected by WebSocket implementation

### Incremental Value Delivery
- **Phase 1**: Event bus refactoring while maintaining existing functionality
- **Phase 2**: WebSocket connection with default room and basic broadcasting
- **Phase 3**: Frontend integration and simple reconnection logic

### Rollback Considerations
- **Database Changes**: No schema changes - fully backward compatible
- **Event Schema**: Existing domain events unchanged - no migration needed
- **Breaking Changes**: WebSocket is additive - existing REST API unaffected

---

## 6. Task Breakdown Preview

### Major Work Streams
1. **Event Store Refactoring** (S)
   - Implement async event bus pattern
   - Migrate existing projection handlers to subscribe pattern
   - Ensure backward compatibility

2. **WebSocket Infrastructure** (S)
   - Connection manager with default room pattern
   - WebSocket endpoint and event broadcasting
   - Integration with event bus

3. **Frontend Integration** (S)
   - WebSocket client with simple reconnection
   - Real-time UI updates for inventory changes
   - Basic error handling and connection status

### Cross-Stream Dependencies
- **Backend Infrastructure → Frontend Client**: WebSocket endpoint must be complete before client development
- **Frontend Client → Integration Testing**: Client implementation needed for E2E scenarios

### Total Effort Estimate
**Overall Size**: S
**Confidence**: High - Simplified approach with clear boundaries
**Timeline Estimate**: 1-2 development iterations

---

## 7. Success Criteria

### Definition of Done
- [ ] Users see real-time inventory updates across multiple browser sessions
- [ ] WebSocket connection handles simple reconnection after disconnection
- [ ] REST API functionality completely unaffected by WebSocket implementation
- [ ] Event bus refactoring maintains all existing projection functionality

### Validation Approach
- **Technical Validation**: Multi-session inventory updates, connection stress testing
- **User Validation**: Smooth real-time experience without page refreshes
- **Performance Validation**: Message delivery timing, concurrent connection limits

---

## Next Steps

1. **Review & Align**: Confirm approach leverages existing event infrastructure appropriately
2. **Risk Validation**: Prototype WebSocket connection management for complexity assessment
3. **Task Generation**: Break down into detailed implementation tasks for each work stream

---

*TIP Created*: 2025-07-08
*Last Updated*: 2025-07-08
*Status*: Accepted
