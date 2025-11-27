# Functional Event Generation Pattern for Domain Models

## Context and Problem Statement

The initial implementation used an `uncommitted_events` list attached to domain model instances to track generated events. This approach violates single responsibility principle by mixing domain logic with infrastructure concerns, creates tight coupling between models and event storage, and is not idiomatic Python. Domain models should focus purely on business logic, while event generation should be explicit and handled separately.

## Considered Options

* **Current Approach**: `uncommitted_events` list attached to domain models
* **Factory Pattern**: Separate factory classes that return `DomainEventResult` objects
* **Functional Approach**: Pure functions returning `(aggregate, events)` tuples
* **Context Manager**: Event collection via context managers and thread-local storage

## Decision Outcome

Chosen option: "Functional Approach with method convenience", because it provides the cleanest separation of concerns while maintaining ergonomic usage. Pure functions are highly testable, immutable by design, and follow Python's explicit-is-better-than-implicit principle.

### Implementation Pattern

```python
# Pure functions handle the core logic
def create_inventory_store(store_id: UUID, name: str, ...) -> Tuple[InventoryStore, List[DomainEvent]]:
    store = InventoryStore(store_id=store_id, name=name, ...)
    event = StoreCreated(store_id=store_id, name=name, ...)
    return store, [event]

# Models provide convenient method interfaces
class InventoryStore(BaseModel):
    # Clean domain fields only - NO uncommitted_events
    store_id: UUID
    name: str

    @classmethod
    def create(cls, ...) -> Tuple['InventoryStore', List[DomainEvent]]:
        return create_inventory_store(...)
```

### Consequences

* Good, because domain models are purely focused on business logic
* Good, because pure functions are trivial to test in isolation
* Good, because event generation is explicit and cannot be forgotten
* Good, because follows Python's tuple unpacking and explicit return idioms
* Good, because enables easy composition and transaction boundary management
* Bad, because requires updating all existing tests to handle tuple returns
* Bad, because slightly more verbose than the magical `uncommitted_events` approach

## Update: Refinement of Implementation (2025-07-02)

After implementing the separate operations module approach, we discovered several issues:

1. **Circular Import Problem**: Separating operations from models created circular import issues requiring `TYPE_CHECKING` workarounds
2. **Not Actually Pure**: The functions call `datetime.now()` and have side effects, so "pure functions" was misleading
3. **Violates DDD**: Domain-Driven Design advocates for rich domain models with behavior, not separation of logic from data
4. **Unnecessary Complexity**: Methods just delegated to functions, adding indirection without value

### Refined Implementation Pattern

The core insight was the **tuple return pattern**, not the separation into external functions:

```python
class InventoryStore(BaseModel):
    # Clean domain fields only - NO uncommitted_events
    store_id: UUID
    name: str
    inventory_items: List[InventoryItem] = Field(default_factory=list)

    @classmethod
    def create(cls, store_id: UUID, name: str, ...) -> Tuple['InventoryStore', List[DomainEvent]]:
        """Create store and return (store, events) tuple for explicit event handling."""
        created_at = datetime.now()
        store = cls(store_id=store_id, name=name, ...)
        event = StoreCreated(store_id=store_id, name=name, ..., created_at=created_at)
        return store, [event]

    def add_inventory_item(self, ...) -> Tuple['InventoryStore', List[DomainEvent]]:
        """Add item and return (updated_store, events) tuple."""
        # Logic directly in method - simple and clear
```

This approach maintains all the benefits while eliminating the architectural complexity:
* ✅ Explicit event handling via tuple returns
* ✅ No infrastructure concerns in domain models
* ✅ Rich domain models with behavior (DDD compliant)
* ✅ No circular imports or complexity
* ✅ Methods stay close to the data they operate on
