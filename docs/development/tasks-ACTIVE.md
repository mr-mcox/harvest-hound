# Task Plan: Dashboard Inline Store Creation

**TIP Reference**: `docs/development/tips/tip-dashboard-inline-store-creation.md`
**Implementation Sequence**: Foundation → Core → Integration → Polish
**Timeline Estimate**: 2-3 development days (streamlined approach)

---

## Task 1: Backend Event Schema Foundation (TIP Section 3: Event Flow Design)
**Goal**: Create event schema infrastructure that enables orchestration service implementation

### 1.1 Event Schema Definition - **SETUP ONLY**
- [x] **Add StoreCreatedWithInventory event class** - Create event in `app/events/domain_events.py` with fields: store_id, successful_items, error_message (simplified)
- [x] **Update event imports** - Add new event to `app/events/__init__.py` exports
- [x] **Add event type registration** - Include in projection registry event type mappings

### 1.2 Response Model Schema - **SETUP ONLY**
- [x] **Extend CreateStoreRequest model** - Add optional `inventory_text: str | None = None` field to existing model in `api.py`
- [x] **Extend CreateStoreResponse model** - Add optional fields: `successful_items: int | None`, `error_message: str | None` (simplified)
- [x] **Update API endpoint signature** - Modify return type annotation to include new fields

---

## Task 2: StoreService Enhancement (TIP Section 3: Bounded Context Impacts)
**Goal**: Enhance StoreService with unified creation flow and eliminate unnecessary orchestrator complexity

### 2.1 Remove StoreCreationOrchestrator - **REFACTOR**
- [x] **Migrate orchestrator tests to StoreService tests** - Move test cases from `test_store_creation_orchestrator.py` to `test_store_service.py`
- [x] **Update API endpoint imports** - Remove orchestrator imports from `api.py` and `dependencies.py`
- [x] **Delete orchestrator files** - Remove `app/services/store_creation_orchestrator.py` and `tests/test_store_creation_orchestrator.py`
- [x] **Clean up dependency injection** - Remove orchestrator factory functions from `app/dependencies.py`

### 2.2 Unified Creation Logic in StoreService - **NEW BEHAVIOR**  
- [x] **Add create_store_with_inventory method** - New method on StoreService with signature matching former orchestrator
- [x] **Implement conditional inventory processing** - When inventory_text provided, call existing upload_inventory method
- [x] **Implement result aggregation** - Count successful items and capture error message from upload results
- [x] **Implement StoreCreatedWithInventory event emission** - Generate event with complete operation results and publish via event bus

### 2.3 Enhanced StoreService for Partial Success - **NEW BEHAVIOR**
- [ ] **Enhance InventoryUploadResult** - Add `parsing_notes: Optional[str]` field to capture LLM error messages
- [ ] **Update StoreService.upload_inventory** - Modify to use enhanced parsing that reports partial success
- [ ] **Remove fail-fast behavior** - Process all successfully parsed items instead of stopping on first error
- [ ] **Return comprehensive results** - Include both successful item count and parsing notes in result

### 2.4 Enhanced Inventory Parsing with LLM Error Reporting - **NEW BEHAVIOR**
- [ ] **Update BAML schema for error message field** - Add error_message field to BAML response schema
- [ ] **Enhance BAML prompt engineering** - Update prompts to flag problematic items with natural language explanations (e.g., "Volvos" not a food item, "3 gazillion eggs" unclear quantity)  
- [ ] **Update BamlInventoryParserClient** - Modify client to return enhanced parsing results with error messages
- [ ] **Add BAML integration tests** - Test real LLM behavior with various partial success scenarios

---

## Task 3: API Integration Layer (TIP Section 3: Integration Points)
**Goal**: Enhance POST /stores endpoint to support unified creation and maintain backward compatibility

### 3.1 Enhanced Endpoint Logic - **NEW BEHAVIOR**
- [ ] **Update create_store endpoint implementation** - Check for optional inventory_text field in request
- [ ] **Implement conditional unified creation** - Route to StoreService.create_store_with_inventory when inventory_text present, otherwise use existing create_store flow
- [ ] **Update response construction** - Include unified creation results (successful_items, error_message) in response when applicable

### 3.2 WebSocket Event Broadcasting - **NEW BEHAVIOR**
- [ ] **Add StoreCreatedWithInventory event handler** - Create handler in `app/projections/handlers.py` to broadcast new event type
- [ ] **Register WebSocket event mapping** - Add event type to WebSocket event catalog in connection manager
- [ ] **Test event propagation** - Ensure events reach connected WebSocket clients within 100ms

---

## Task 4: Frontend Component Foundation (TIP Section 3: Integration Points)
**Goal**: Prepare StoreList component to support inline creation form

### 4.1 Component Structure Updates - **SETUP ONLY**
- [ ] **Add form state to StoreList** - Create local state variables for inline form visibility and submission state
- [ ] **Add form toggle UI** - Create "Add Store" button that shows/hides inline creation form
- [ ] **Create inline form markup** - Add form HTML with fields for name, description, store_type, and inventory_text textarea

### 4.2 Enhanced API Client - **SETUP ONLY**
- [ ] **Update apiPost function signature** - Accept optional inventory_text parameter in store creation call
- [ ] **Update type definitions** - Add inventory_text to CreateStoreRequest type and extend CreateStoreResponse with simplified result fields

---

## Task 5: Frontend Progressive Enhancement (TIP Section 2: Pattern Applications)
**Goal**: Implement use:enhance form handling to preserve dashboard context

### 5.1 Form Enhancement Logic - **NEW BEHAVIOR**
- [ ] **Add use:enhance to inline form** - Implement progressive enhancement with custom submit handler
- [ ] **Implement loading state management** - Show loading indicator during form submission, disable form controls
- [ ] **Implement optimistic UI updates** - Add "Creating store..." placeholder to store list immediately on submission

### 5.2 Simplified Response Handling - **NEW BEHAVIOR**
- [ ] **Handle successful creation response** - Update store list with new store including final item count, clear form, hide inline form
- [ ] **Handle error scenarios** - Show simple error message in form context, maintain form state for user correction (defer complex partial success UX)

---

## Task 6: Basic WebSocket Updates (TIP Section 3: Event Flow Design)
**Goal**: Simple WebSocket event broadcasting without premature optimization

### 6.1 Basic Event Handling - **NEW BEHAVIOR**
- [ ] **Add StoreCreatedWithInventory event listener** - Subscribe to new event type in dashboard WebSocket connection
- [ ] **Implement simple dashboard updates** - Update store list when receiving WebSocket events (rely on form response as primary update mechanism)

---

## Task 7: Integration Testing and Validation (TIP Section 4: Testing Strategy)
**Goal**: Ensure complete workflow functions correctly end-to-end

### 7.1 Backend Integration Tests - **NEW BEHAVIOR**
- [ ] **Test complete unified creation flow** - Verify store creation with inventory succeeds and generates correct events
- [ ] **Test simple error scenarios** - Verify store created successfully even when inventory processing fails (simple error message)
- [ ] **Test WebSocket event propagation** - Ensure StoreCreatedWithInventory events broadcast correctly

### 7.2 Frontend Integration Tests - **NEW BEHAVIOR**
- [ ] **Test inline form submission** - Verify use:enhance preserves dashboard context and updates UI correctly
- [ ] **Test basic error handling** - Verify simple error message display works as expected

### 7.3 End-to-End Validation - **NEW BEHAVIOR**
- [ ] **Test streamlined user workflow** - Dashboard → inline form → unified submission → success/error result
- [ ] **Test performance requirements** - Verify operation completes within 3 seconds for ≤20 inventory items
- [ ] **Test backward compatibility** - Ensure existing store creation workflow continues to function

---

## Success Criteria Validation

Based on TIP Section 7 Definition of Done:
- [ ] User can create store and upload inventory in single dashboard form
- [ ] Store appears in list with final item count after processing completes
- [ ] Simple error messaging when inventory processing fails (enhancement opportunities identified for later)
- [ ] Progressive enhancement provides immediate feedback during processing
- [ ] All existing store creation functionality remains intact

**Implementation Notes**:
- Tasks 1-3 enable backend functionality (Phase 1)
- Tasks 4-5 enable basic frontend functionality (Phase 2)
- Tasks 6-7 complete integration and testing (Phase 3)
- Follow TIP risk mitigation: coordinate backend deployment before frontend updates
- **Deferred Complexity**: Race condition handling, complex partial success UX, detailed error breakdowns - add later if actually needed
