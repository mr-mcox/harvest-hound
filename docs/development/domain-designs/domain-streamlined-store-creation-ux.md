# Domain Design: Dashboard Inline Store Creation

**Source Documents**
- Opportunity: `docs/development/opportunities/opp-streamlined-store-creation-ux.md`
- Concept: `docs/development/concepts/concept-streamlined-store-creation-ux.md`
- Selected Concept: A - Dashboard Inline Creation

**Executive Summary**
Enable unified store creation and inventory population within the dashboard context by supporting combined operations, real-time feedback during inventory processing, and immediate projection updates. This requires minimal domain changes focused on orchestration and projection patterns rather than core aggregate modifications.

---

## Domain Translation

Map user-facing concepts to domain concepts:

| User Concept | Current Domain Concept | Proposed Domain Change |
|--------------|------------------------|------------------------|
| "Single form for store + inventory" | Separate POST `/stores` + POST `/stores/{id}/inventory` | New Application Service for orchestrated operation |
| "Real-time inventory processing feedback" | Batch inventory upload with success/failure response | WebSocket events during inventory processing |
| "Immediate store count updates" | StoreView projection updated after inventory events | Enhanced projection for progressive updates |
| "Dashboard stays in context" | Navigation between creation form and store list | Read model optimized for dashboard view |

---

## Domain Model Evolution

### No New Bounded Contexts Required
The existing **Inventory** context handles store and inventory operations adequately. Changes are primarily in Application and Interface layers.

### No New Aggregates/Entities Required
Current `InventoryStore` aggregate supports the required operations. The concept maps to existing domain capabilities.

### Enhanced Application Services

#### StoreCreationOrchestrator *(New Application Service)*
- **Purpose**: Coordinate store creation and inventory upload as a unified operation
- **Key Operations**: 
  - `CreateStoreWithInventory(storeSpec, inventoryText)` - creates store, attempts inventory batch processing
- **Dependencies**: InventoryStore aggregate, IngredientNormalizer, event bus
- **Error Handling**: Store always created; inventory parsing failures return partial results + error details

---

## Event Design

### New Application Events

#### StoreCreatedWithInventory
- **Emitted By**: StoreCreationOrchestrator
- **Triggered When**: Store creation and batch inventory processing complete
- **Payload**: 
  - `storeId: string`
  - `successfulItems: number`
  - `failedItems: string[]` - unparseable inventory lines
  - `processingErrors: string[]` - LLM parsing errors
- **Consumers**: Dashboard updates, error notifications
- **Purpose**: Single event containing complete results of unified operation

---

## Behavioral Flows

### Unified Store Creation Flow
```
1. User Action: Fill inline form with store details + inventory text
   → Command: CreateStoreWithInventory
   → Service: StoreCreationOrchestrator
   
2. Orchestrator: Create store first
   → Command: CreateStore (existing)
   → Aggregate: InventoryStore
   → Event: StoreCreated (existing)
   
3. Orchestrator: Process inventory as single LLM batch
   → Command: BulkAddInventory (existing)
   → Aggregate: InventoryStore  
   → Events: Multiple IngredientAddedToStore (existing, for successful items)
   
4. Orchestrator: Emit unified completion event
   → Event: StoreCreatedWithInventory
   → Payload: Success count, failed lines, errors
   
5. Frontend: Update dashboard + show notifications
   → Handler: Dashboard state updates
   → UI: Store appears with final count + error toaster if needed
```

---

## API Surface Changes

### Replace Existing Endpoints
- **Replace** `POST /stores` with unified endpoint that handles both creation patterns:
  - `POST /stores` - Enhanced to accept optional `inventory_text` field
  - Request: `{name, description?, store_type, inventory_text?}`
  - Response: `{store_id, successful_items?, failed_items?, processing_errors?}`
  - Behavior: Creates store, processes inventory if provided, returns complete results

### New WebSocket Events
- `store_created_with_inventory` - `{store_id, successful_items, failed_items[], processing_errors[]}`

---

## Technical Considerations

### Performance Impact
- **Single LLM Call**: Inventory processing happens as one batch operation
- **Reduced WebSocket Volume**: Single completion event instead of progress stream
- **Projection Updates**: Standard StoreView updates after batch completion

### Data Migration
- **API Breaking Change**: `POST /stores` request/response format changes
- **No Data Migration**: Existing stores and inventory remain unchanged

### Consistency Boundaries
- **Transaction Boundary**: Store creation and inventory processing in separate transactions
- **Partial Success Pattern**: Store always created; inventory failures captured in response
- **Error Recovery**: Failed inventory lines available for user correction and retry

---

## Implementation Risks

### Medium Risk
- **LLM Batch Processing Latency**: Single large inventory could cause noticeable delay
  - *Mitigation*: Add loading state during processing, consider reasonable size limits
  
- **Partial Failure UX Design**: Need clear patterns for showing partial success + errors
  - *Mitigation*: Design toaster/notification system for error display, retry affordances

### Low Risk
- **API Breaking Change Impact**: Frontend needs update to handle new response format
  - *Mitigation*: Single frontend codebase, coordinated deployment

### Open Questions
- **Error Display Patterns**: Toast notifications vs inline error display for failed inventory items?
- **Retry Mechanism**: Should users retry entire inventory or just failed lines?
- **Size Limits**: What's reasonable maximum for single inventory upload?

---

## Success Criteria

How we know the domain model successfully enables the concept:
- [ ] User can create store and upload inventory in single form without navigation
- [ ] Store appears in dashboard list with final item count after processing
- [ ] Partial failure scenarios show successful items + clear error notifications
- [ ] Error messages contain enough detail for user correction and retry
- [ ] Single API call handles entire operation efficiently
- [ ] Simple event model reduces WebSocket complexity

---

This design enables the Dashboard Inline Creation concept through a simplified orchestration pattern that eliminates progress tracking complexity while maintaining clear error handling and partial success patterns.