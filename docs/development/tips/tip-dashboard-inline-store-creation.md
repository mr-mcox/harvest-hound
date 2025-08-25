# Technical Implementation Plan (TIP): Dashboard Inline Store Creation

**Use Case**: Streamlined Store Creation UX - Enable unified store creation and inventory population within the dashboard context
**Estimated Scope**: S - Streamlined implementation focusing on core value with simple error handling
**Target Value**: Reduce store setup time from ~5 minutes to ~2 minutes by eliminating context switches
**Domain Design Reference**: `docs/development/domain-designs/domain-streamlined-store-creation-ux.md`

---

## 1. Context & Problem Analysis

### Current State
- **Existing Code**: Store creation via `POST /stores` and inventory upload via `POST /stores/{id}/inventory` are separate operations
- **Current Architecture**: StoreService orchestrates domain operations, InventoryStore aggregate handles events, projection handlers maintain read models
- **Known Issues**: User must navigate between create form → store list → specific store → upload form (6-7 steps total)

### Problem Statement
- **Core Challenge**: Store creation and inventory population are artificially separated in the UI workflow, causing navigation overhead
- **User Impact**: Users abandon setup mid-process due to complexity; cannot see immediate results of their work
- **Technical Impact**: Current API requires multiple round trips and navigation state management

### Architecture Fit Assessment
- **DDD Alignment**: Changes stay within Inventory context; new Application Service fits orchestration patterns
- **Event Sourcing**: New StoreCreatedWithInventory event follows existing event patterns
- **Existing Patterns**: Container/presentation pattern already established; can extend existing StoreList component

---

## 2. Technical Approach & Design Decisions

### High-Level Strategy
Enhance StoreService with unified creation flow to coordinate store creation and inventory upload as a single operation, with enhanced API endpoint and simplified event model.

### Key Design Decisions
| Decision | Alternatives Considered | Rationale |
|----------|------------------------|--------------|
| Single Enhanced API Endpoint | New /stores/with-inventory endpoint | Simplifies client code; single request reduces network overhead |
| Batch LLM Processing | Progressive streaming with updates | User feedback indicates "super quick" processing doesn't need progress tracking |
| Enhanced StoreService | Separate orchestration service | Simplifies architecture; unified creation fits within existing service responsibilities |
| Single Completion Event | Multiple progress events | Reduces WebSocket complexity; aligns with simplified UX requirement |

### Pattern Applications
- **Patterns to Follow**: Existing Application Service pattern (StoreService), event sourcing with projection updates, container/presentation component separation
- **Anti-Patterns to Avoid**: Domain logic in API controllers, tight coupling between creation and inventory operations at domain level
- **New Patterns**: Orchestration service for combined operations, partial success result patterns
- **Key Library APIs**: FastAPI dependency injection, Svelte form actions with progressive enhancement, WebSocket event patterns

### Research Recommendations *(Optional)*
- **Error UX Patterns**: Deferred - start with simple success/error message, enhance later if needed

### Risk Assessment
- **Medium Risk**: API breaking change coordination between frontend/backend deployments
- **Low Risk**: Batch processing latency for reasonable inventory sizes (≤20 items)
- **Mitigation Strategies**: Coordinate deployments, add loading states during processing, simple error messaging (enhance later if needed)

---

## 3. Implementation Architecture

### Bounded Context Impacts
- **Inventory Context**: Enhanced StoreService with unified creation capabilities; new StoreCreatedWithInventory event
- **Interface Layer**: Enhanced POST /stores endpoint; updated WebSocket event catalog; modified frontend components

### Event Flow Design
```
[User Action: Submit unified form] → [StoreService.create_store_with_inventory] → [StoreCreated + InventoryItemAdded events] → [StoreCreatedWithInventory event] → [Frontend UI update + WebSocket notification]
```
- **New Events**: StoreCreatedWithInventory with payload `{storeId, successfulItems, errorMessage?}` (simplified)
- **Event Consumers**: WebSocket subscribers, projection handlers for StoreView updates
- **Event Schema**: Combines creation confirmation with inventory processing results

### Data Flow
- **Input Sources**: Enhanced CreateStoreRequest with optional inventory_text field from dashboard form
- **Processing Steps**: Store creation → inventory parsing → batch item addition → result aggregation
- **Output Destinations**: Updated read models, WebSocket broadcast, API response with complete results

### Integration Points
- **REST Endpoints**: Enhanced `POST /stores` to accept optional inventory_text and return extended response
- **WebSocket Events**: New store_created_with_inventory event for real-time dashboard updates
- **Database Schema**: No schema changes needed; uses existing event store and read model tables
- **LLM Integration**: Existing inventory parser service handles batch processing
- **Frontend Components**: Modified StoreList to show inline creation form; enhanced form handling

---

## 4. Testing & Quality Strategy

### Testing Levels
- **Unit Tests**: Enhanced StoreService methods, unified creation operations, error handling
- **Integration Tests**: Complete create-with-inventory flow, WebSocket event propagation, projection consistency
- **E2E Tests**: Dashboard inline creation workflow, partial success scenarios, error display and recovery

### TDD Strategy
- **Behaviors Requiring Tests**: Store creation with inventory success, partial inventory failure handling, orchestration error scenarios
- **Setup-Only Work**: API endpoint signature changes, WebSocket event schema additions
- **Test Data Strategy**: Mock LLM responses for consistent inventory parsing, fixture data for various success/failure combinations

### Quality Gates
- **Performance**: Single operation completes within 3 seconds for reasonable inventory sizes (< 20 items)
- **User Experience**: Simple success feedback with item count; clear error message if processing fails
- **Data Integrity**: Store always created successfully; inventory failures don't block store creation
- **Integration Reliability**: WebSocket events consistently propagate within 100ms

---

## 5. Implementation Sequencing

### Dependencies & Critical Path
1. **Foundation Work**: Enhanced StoreService methods, updated API endpoint signature
2. **Core Implementation**: Unified creation logic, error handling, event generation
3. **Integration Work**: WebSocket event broadcasting, frontend form enhancement
4. **Polish & Optimization**: Loading states, error display, inline form UX refinements

### Risk-First Approach
- **Highest Risk First**: API breaking change coordination (deploy backend changes before frontend updates)
- **Proof of Concept**: Test unified creation service with realistic inventory sizes to validate flow
- **Fallback Options**: Temporary API compatibility layer if deployment coordination becomes complex

### Incremental Value Delivery
- **Phase 1**: Working unified creation service with API endpoint (backend functionality complete)
- **Phase 2**: Basic inline form without progressive enhancement (functional but not optimal UX)
- **Phase 3**: Full progressive enhancement with WebSocket updates and error handling

### Rollback Considerations *(Optional)*
- **Database Changes**: No schema changes needed; events are append-only
- **Event Schema**: New event is additive; won't break existing consumers
- **Breaking Changes**: API change requires coordinated frontend deployment; can temporarily support both signatures

---

## 6. Task Breakdown Preview

### Major Work Streams
1. **Backend StoreService Enhancement** (S)
   - Add unified creation method to existing StoreService
   - Implement unified creation flow with error handling
   - Add StoreCreatedWithInventory event and projection handlers

2. **API Integration Layer** (S)
   - Enhance POST /stores endpoint signature and implementation
   - Update WebSocket event broadcasting
   - Modify response models and error handling

3. **Frontend Enhancement** (M)
   - Add inline creation form to StoreList component
   - Implement progressive enhancement with use:enhance (required for dashboard context preservation)
   - Design and build error display and retry UX

### Cross-Stream Dependencies
- **Backend → Frontend**: API changes must be deployed before frontend can consume new interface
- **StoreService → API**: Service implementation required before endpoint can coordinate unified operations

### Total Effort Estimate
**Overall Size**: S
**Confidence**: High - Well-understood patterns, simplified error handling, no premature optimizations
**Timeline Estimate**: 2-3 development days with testing

---

## 7. Success Criteria

### Definition of Done
- [ ] User can create store and upload inventory in single dashboard form
- [ ] Store appears in list with final item count after processing completes
- [ ] Simple error messaging when inventory processing fails (enhancement opportunities identified for later)
- [ ] Progressive enhancement provides immediate feedback during processing
- [ ] All existing store creation functionality remains intact

### Validation Approach
- **Technical Validation**: Integration tests verify orchestration flow; unit tests cover error scenarios
- **User Validation**: Time-to-completion measurement (target: < 2 minutes); error recovery testing
- **Performance Validation**: Load testing with various inventory sizes; WebSocket event latency measurement

---

## Next Steps

1. **Review & Align**: Confirm enhanced StoreService pattern aligns with domain boundaries
2. **Task Generation**: Ready to break down into detailed implementation tasks with clear acceptance criteria
3. **Deployment Strategy**: Plan coordinated backend/frontend deployment to handle API changes

---

*TIP Created*: 2025-08-23
*Last Updated*: 2025-08-24
*Status*: Updated (Simplified Architecture)
