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
