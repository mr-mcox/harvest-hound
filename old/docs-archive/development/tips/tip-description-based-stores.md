# Technical Implementation Plan: Description-Based Stores

---
date: 2025-11-27
feature: description-based-stores
status: draft
related_domain_design: docs/development/design-decisions/decision-description-based-stores.md
estimated_effort: M
confidence: High
tags: [domain-model, event-sourcing, polymorphism, stores]
---

## Domain Context

This implementation transforms the inventory store model from a single concrete class to a polymorphic hierarchy with abstract base class and two concrete implementations. This enables natural language store definitions that can be interpreted by LLMs for ingredient availability.

**Key Design Decision**: The existing `infinite_supply` boolean field is removed as part of this refactoring. The concept of "infinite availability" is now implicit in the polymorphic design:
- `ExplicitInventoryStore`: finite, enumerated inventory
- `DefinitionBasedStore`: LLM-inferred availability (can represent infinite-like behavior through description)

**Relevant Domain Model Documentation**:
- docs/architecture/domain-model.md (Section 4: InventoryStore Hierarchy)
- docs/development/design-decisions/decision-description-based-stores.md

**Key Concepts**:
- Abstract `InventoryStore` base class defines common interface
- `ExplicitInventoryStore` for enumerated inventories with tracked quantities
- `DefinitionBasedStore` for LLM-inferred availability from natural language
- Distinction between `description` (human notes) vs `definition` (LLM instructions)
- Event sourcing pattern with discriminator-based routing

## Implementation Phases

### Phase 1: Domain Model Refactoring

**Purpose**: Transform the concrete InventoryStore into an abstract hierarchy with two concrete subclasses, establishing the foundation for all subsequent work.

**Scope**: Backend domain model refactoring - creating abstract base class, implementing subclasses, updating event structure with discriminator field. Remove existing store tests and implement new tests following TDD.

**Key Considerations**:
- Remove tests of old concrete InventoryStore behavior first
- TDD: Write tests for new polymorphic behavior before implementation
- Pydantic BaseModel + ABC compatibility must be validated
- Event discriminator field enables proper aggregate reconstruction
- Each subclass has genuinely different fields and behaviors
- No backward compatibility needed - clean break acceptable

**Dependencies**: None - this is the foundational phase

**Complexity**: M

### Phase 2: Repository and Event Sourcing Adaptation

**Purpose**: Update the repository layer to handle polymorphic aggregates, ensuring correct routing during event replay and persistence.

**Scope**: Repository pattern updates - discriminator-based routing in `from_events()`, proper subclass instantiation, event stream handling. Remove old repository tests and write new ones using TDD.

**Key Considerations**:
- Remove tests assuming single concrete store class
- TDD: Write tests for polymorphic event routing before implementation
- Repository must route StoreCreated events to correct subclass constructor
- Event sourcing pattern must preserve all existing guarantees
- Each subclass may have different event handling logic
- Clean separation between aggregate persistence and reconstruction

**Dependencies**: Phase 1 (Domain Model Refactoring)

**Complexity**: S

### Phase 3: Service Layer and API Updates

**Purpose**: Modify the service layer to instantiate correct store subclasses and update REST API to accept store type discriminator.

**Scope**: StoreService refactoring, API endpoint modifications, request/response schema updates. Remove obsolete service/API tests and replace with TDD tests.

**Key Considerations**:
- Remove service tests expecting old store structure
- TDD: Write API tests for new store_type field before implementation
- API must accept `store_type` field to determine which subclass to create
- Service layer orchestrates correct domain model instantiation
- Validation logic differs between store types
- Error handling for invalid store type requests

**Dependencies**: Phase 2 (Repository adaptation)

**Complexity**: S

### Phase 4: Frontend Store Creation UI

**Purpose**: Update the frontend to distinguish between store types and present appropriate form fields based on user selection.

**Scope**: Frontend components - store creation forms, field visibility logic, validation rules. Update component tests following TDD approach.

**Key Considerations**:
- Remove or update existing store creation component tests
- TDD: Write tests for dynamic form behavior before implementation
- UI must clearly communicate difference between store types
- ExplicitInventoryStore shows description field (optional)
- DefinitionBasedStore shows definition field (required)
- User experience should guide toward appropriate store type selection

**Dependencies**: Phase 3 (API Updates)

**Complexity**: S

## Sequencing Logic

The phases follow a bottom-up approach, starting with the domain model core and radiating outward through the application layers:

1. **Domain First**: Phase 1 establishes the polymorphic domain model as the foundation
2. **Persistence Next**: Phase 2 ensures we can persist and reconstruct the new model correctly
3. **Service Integration**: Phase 3 connects the domain to the external world via API
4. **User Interface**: Phase 4 provides the user-facing capability

This sequencing minimizes risk by validating each layer before building the next. Each phase includes removing old tests and writing new tests using TDD, ensuring we have a clean break from the old implementation. The domain model and repository changes (Phases 1-2) could potentially be done in parallel since they're closely related, but sequential execution ensures clean interfaces.

## High-Level Test Strategy

**TDD Approach Throughout**:
Each phase follows Test-Driven Development with a clean break from old implementation:
1. Remove tests of old behavior first
2. Write tests for new behavior before implementation
3. Implement to make tests pass
4. Refactor if needed while keeping tests green

**Phase-Specific Testing Focus**:
- **Phase 1**: Domain model behaviors - subclass instantiation, method polymorphism, field validation
- **Phase 2**: Event sourcing - event creation, persistence, aggregate reconstruction with discriminator
- **Phase 3**: API behavior - request validation with store_type, response schemas, error cases
- **Phase 4**: UI logic - dynamic form fields, validation rules based on store type

**Key Scenarios to Validate**:
- Creating both types of stores with valid data
- Attempting invalid operations (e.g., adding inventory to DefinitionBasedStore)
- Event replay correctly reconstructs both store types using discriminator
- API properly routes requests based on store_type field
- UI dynamically shows/hides fields based on store type selection
- LLM inference properly stubbed in DefinitionBasedStore

## Integration Points

**Backend**:
- Domain model: Abstract hierarchy with polymorphic behaviors
- Event sourcing: Discriminator-based routing for aggregate reconstruction
- Repository layer: Polymorphic aggregate persistence and retrieval
- Service layer: Correct subclass instantiation based on store type
- REST API: New store_type field in creation endpoints

**Frontend**:
- Store creation components: Dynamic form fields based on type
- State management: Handle different store type schemas
- Validation logic: Type-specific field requirements

**External**:
- LLM integration: Stubbed for now in DefinitionBasedStore.check_availability()
- Future IngredientBroker: Foundation prepared for polymorphic store interaction

## Risk Assessment

**Medium Risks**:
- **Pydantic + ABC compatibility**: May require specific configuration or patterns to work correctly
  - *Mitigation*: Early validation in Phase 1, fallback to composition if inheritance proves problematic

- **Frontend state management complexity**: Different field requirements per store type
  - *Mitigation*: Clear component separation, comprehensive UI testing

**Low Risks**:
- **Event sourcing routing logic**: Discriminator pattern is well-established
  - *Mitigation*: Thorough testing of reconstruction logic

**Contingency Plans**:
- If Pydantic + ABC proves incompatible, use composition pattern with protocol/interface
- If repository routing becomes complex, consider separate event streams per aggregate type

## Implementation Notes

**Architectural Patterns to Follow**:
- Event sourcing pattern as established in existing codebase
- Domain-driven design with clear aggregate boundaries
- Repository pattern for persistence abstraction
- Service layer orchestration pattern
- Test-Driven Development throughout all phases

**Key Principles to Maintain**:
- Clean break from old implementation - no backward compatibility
- Type safety through proper subclassing
- Clear field semantics (description vs definition)
- Event immutability and replay capability
- Clean separation of concerns across layers

**Quality Gates**:
- Old tests removed before writing new tests in each phase
- New tests written and failing before implementation
- All tests passing before moving to next phase
- Domain invariants validated through tests
- API contracts verified through tests

## Overall Complexity Estimate

**Overall**: M (Moderate)
**Confidence**: High

**Justification**:
- Well-defined domain model changes with clear design decision
- Established patterns in codebase to follow (event sourcing, service layer)
- Main complexity in polymorphic event sourcing routing (Phase 2)
- Frontend changes are straightforward form field management
- No migration complexity since backward compatibility not required
- Limited external dependencies (LLM stubbed out)

---

## Implementation Tasks

**TIP Reference**: Phases 1-4 above
**Task Sequencing**: Tasks map directly to TIP phases - domain model foundation first, then radiating outward through persistence, service, and UI layers.

---

## Task 1: Domain Model Refactoring (TIP Phase 1)
**Goal**: Transform concrete InventoryStore into abstract hierarchy with two polymorphic subclasses
**TIP Context**: Phase 1 - establishes foundation for all subsequent work

### 1.1 Abstract Base Class Creation - **SETUP ONLY**
- [ ] **Create abstract InventoryStore base class** - Add ABC import and @abstractmethod decorators in `app/models/inventory_store.py:11`
- [ ] **Move shared fields to base class** - `store_id`, `name`, `description` remain as common interface
- [ ] **Define abstract method signatures** - `@abstractmethod def check_availability()` and `@abstractmethod def supports_inventory_addition()`

### 1.2 ExplicitInventoryStore Implementation - **NEW BEHAVIOR**
- [ ] **Create ExplicitInventoryStore subclass** - Inherit from InventoryStore, include `inventory_items` field in `app/models/inventory_store.py:35`
- [ ] **Remove infinite_supply field** - No longer needed with polymorphic design (explicit vs definition-based stores)
- [ ] **Implement concrete methods** - `check_availability()` returns inventory lookup, `supports_inventory_addition()` returns True
- [ ] **Write test_explicit_store_creation()** - Verify ExplicitInventoryStore can be instantiated with inventory_items field

### 1.3 DefinitionBasedStore Implementation - **NEW BEHAVIOR**
- [ ] **Create DefinitionBasedStore subclass** - Include `definition` field (required), no inventory_items in `app/models/inventory_store.py:55`
- [ ] **Implement concrete methods** - `check_availability()` returns stubbed LLM call, `supports_inventory_addition()` returns False
- [ ] **Write test_definition_store_creation()** - Verify DefinitionBasedStore requires definition field and rejects inventory operations

### 1.4 Event Structure Updates - **SETUP ONLY**
- [ ] **Add store_type discriminator to StoreCreated event** - Add `store_type: str` field in `app/events/domain_events.py:15`
- [ ] **Remove infinite_supply from StoreCreated event** - Field is obsolete with polymorphic design
- [ ] **Update StoreView read model** - Remove `infinite_supply` field from `app/models/read_models.py`
- [ ] **Update database schema** - Remove `infinite_supply` column from store_views table in `app/infrastructure/database.py`
- [ ] **Update create() factory methods** - Each subclass emits StoreCreated with appropriate store_type value
- [ ] **Remove old tests** - Delete existing InventoryStore tests in `tests/test_inventory_store.py` (entire file)

---

## Task 2: Repository and Event Sourcing Adaptation (TIP Phase 2)
**Goal**: Update repository layer for polymorphic aggregate reconstruction via discriminator routing
**TIP Context**: Phase 2 - ensures persistence layer handles new domain model correctly

### 2.1 Event Sourcing Discriminator Logic - **NEW BEHAVIOR**
- [ ] **Update from_events() method** - Add discriminator routing logic in `app/models/inventory_store.py:91` to instantiate correct subclass
- [ ] **Write test_event_sourcing_explicit_store()** - Verify StoreCreated with store_type="explicit" rebuilds ExplicitInventoryStore
- [ ] **Write test_event_sourcing_definition_store()** - Verify StoreCreated with store_type="definition" rebuilds DefinitionBasedStore

### 2.2 Repository Method Updates - **REFACTOR**
- [ ] **Update StoreRepository.from_events calls** - Verify repository correctly calls polymorphic from_events() in `app/infrastructure/repositories.py:85`
- [ ] **Write test_repository_polymorphic_reconstruction()** - Test repository can rebuild both store types from event streams
- [ ] **Remove old repository tests** - Clean up tests in `tests/test_store_repository.py` that assume single concrete store type

---

## Task 3: Service Layer and API Updates (TIP Phase 3)
**Goal**: Modify service layer and REST API to accept store type discriminator and instantiate correct subclasses
**TIP Context**: Phase 3 - connects new domain model to external world via API

### 3.1 Service Layer Polymorphic Creation - **NEW BEHAVIOR**
- [ ] **Update StoreService.create_store method** - Accept store_type parameter and route to correct subclass in `app/services/store_service.py:75`
- [ ] **Remove infinite_supply parameter** - Remove from create_store_with_inventory() method signature
- [ ] **Write test_service_creates_explicit_store()** - Verify service creates ExplicitInventoryStore when store_type="explicit"
- [ ] **Write test_service_creates_definition_store()** - Verify service creates DefinitionBasedStore when store_type="definition"

### 3.2 API Schema Updates - **SETUP ONLY**
- [ ] **Add store_type field to CreateStoreRequest** - Required field with Literal["explicit", "definition"] type in `api.py:44`
- [ ] **Remove infinite_supply from API schemas** - Remove from CreateStoreRequest and CreateStoreResponse in `api.py`
- [ ] **Add store_type to CreateStoreResponse** - Include in response for client confirmation in `api.py:51`
- [ ] **Update API endpoint handler** - Pass store_type from request to service in `api.py:156`

### 3.3 API Validation and Error Handling - **NEW BEHAVIOR**
- [ ] **Write test_api_explicit_store_creation()** - POST /stores with store_type="explicit" creates correct store type
- [ ] **Write test_api_definition_store_creation()** - POST /stores with store_type="definition" creates correct store type
- [ ] **Write test_api_invalid_store_type_error()** - POST /stores with invalid store_type returns 422 validation error

---

## Task 4: Frontend Store Creation UI (TIP Phase 4)
**Goal**: Update frontend form to distinguish between store types with dynamic field visibility
**TIP Context**: Phase 4 - provides user-facing capability for the new domain model

### 4.1 Component Schema Updates - **SETUP ONLY**
- [ ] **Add store_type to StoreCreateForm props** - Update TypeScript interface to include store_type selection in `src/lib/components/StoreCreateForm.svelte:4`
- [ ] **Update form submission type** - Include store_type in onSubmit callback data structure
- [ ] **Add StoreType enum** - Create type definition for "explicit" | "definition" in `src/lib/types.ts`

### 4.2 Dynamic Form Fields - **NEW BEHAVIOR**
- [ ] **Add store type radio buttons** - User selects between "Explicit Inventory" and "Definition-Based" in `StoreCreateForm.svelte:35`
- [ ] **Implement conditional field visibility** - Show description for explicit, definition field for definition-based stores
- [ ] **Write test_form_shows_correct_fields()** - Verify dynamic field visibility based on store type selection

### 4.3 Frontend Validation Updates - **NEW BEHAVIOR**
- [ ] **Update validateStoreForm function** - Include store_type validation and conditional field requirements in `src/lib/validation.ts`
- [ ] **Write test_validation_requires_definition_field()** - Verify definition-based stores require definition field
- [ ] **Write test_validation_explicit_store_optional_description()** - Verify explicit stores allow optional description

---

## Success Criteria for Implementation

- [ ] All tasks completed and marked as done
- [ ] All tests passing: `cd packages/backend && uv run pytest`
- [ ] Integration points validated between domain model, repository, service, and API layers
- [ ] Risk mitigations implemented: Pydantic + ABC compatibility validated, frontend form complexity managed
- [ ] Code follows architectural patterns: Event sourcing, domain-driven design, test-driven development

**Implementation Note**: Tasks may be reordered, skipped, or added during implementation as reality requires. This task plan is a guide, not a script. Use `implement-tasks` to begin implementation.
