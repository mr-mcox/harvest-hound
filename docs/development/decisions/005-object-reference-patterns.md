---
status: proposed
date: 2025-07-04
---

# Object Reference Patterns in DDD: Aggregate References vs. Data Convenience

## Context and Problem Statement

Our current implementation follows pure DDD principles with UUID references between aggregates (`InventoryItem` references `Ingredient` by `ingredient_id`). However, this creates ergonomic challenges in the frontend where we need ingredient names for display. The frontend currently uses interface extensions (`InventoryItemWithIngredient`) that depend on database joins, creating coupling between frontend and backend data shapes.

The core tension is: **How do we balance DDD purity (aggregate references by ID) with practical needs (easy access to related data) while maintaining clean event sourcing patterns?**

## Decision Drivers

* **DDD Compliance**: Maintain aggregate boundaries and consistency rules
* **Event Sourcing**: Enable clean serialization/deserialization of domain events
* **Frontend Ergonomics**: Eliminate need for complex lookup logic in UI code
* **Performance**: Avoid N+1 queries and complex joins
* **Maintainability**: Keep coupling low between domain layers
* **Scalability**: Support future growth without architectural changes
* **UI Access Patterns**: Optimize for common frontend data access (avoid deep object hierarchies)
* **Persistence Ignorance**: Keep domain models free from database/ORM concerns

## Considered Options

* **Current Approach**: UUID references + frontend interface extensions
* **Value Object Embedding**: Denormalize ingredient data in InventoryItem
* **Domain Service Resolution**: Service layer coordinates cross-aggregate queries
* **Read Model Projections**: Event-driven materialized views for queries
* **Lazy Loading**: Repository-based loading on demand

## Decision Outcome

Chosen option: **"Read Model Projections + Domain Services"**, because it maintains DDD purity while solving the frontend ergonomics problem through event-driven architecture that aligns with our existing event sourcing patterns.

### Consequences

* Good, because domain aggregates remain pure and follow DDD principles
* Good, because leverages existing event sourcing infrastructure
* Good, because eliminates frontend coupling to database joins
* Good, because provides excellent query performance through materialized views
* Good, because handles ingredient name updates automatically via events
* Bad, because adds complexity with event projection infrastructure
* Bad, because introduces eventual consistency (though minimal for this use case)
* Bad, because requires additional read model maintenance

### Confirmation

Implementation compliance will be confirmed through:
1. Unit tests verifying domain aggregates only reference others by ID
2. Integration tests validating event projections update correctly
3. Frontend tests ensuring no direct database join dependencies
4. Performance tests confirming query efficiency

## Pros and Cons of the Options

### Current Approach: UUID References + Frontend Extensions

Pure DDD with frontend interface extensions to add ingredient names via joins.

* Good, because maintains strict aggregate boundaries
* Good, because enables clean event sourcing serialization
* Good, because follows DDD best practices
* Neutral, because requires no additional infrastructure
* Bad, because creates coupling between frontend and database schema
* Bad, because requires complex join logic in frontend data layer
* Bad, because leads to N+1 query problems or complex join operations

### Value Object Embedding

Embed ingredient data directly in InventoryItem as a value object.

* Good, because provides direct access to ingredient names
* Good, because eliminates join operations
* Good, because improves query performance
* Neutral, because simple to implement
* Bad, because violates DDD aggregate boundaries
* Bad, because creates data consistency issues (stale ingredient names)
* Bad, because makes ingredient updates complex in event sourcing

### Domain Service Resolution

Service layer coordinates queries across aggregates.

* Good, because maintains DDD compliance
* Good, because provides consistent data access
* Good, because centralizes cross-aggregate logic
* Neutral, because fits within existing service patterns
* Bad, because adds service layer complexity
* Bad, because still requires careful query optimization
* Bad, because doesn't eliminate all join operations

### Read Model Projections

Event-driven materialized views for queries requiring joined data.

* Good, because perfect fit for event sourcing architecture
* Good, because excellent query performance (no joins needed)
* Good, because maintains DDD aggregate separation
* Good, because handles updates automatically via events
* Good, because eliminates frontend coupling to database schema
* Neutral, because uses existing event infrastructure
* Bad, because adds event projection complexity
* Bad, because introduces eventual consistency
* Bad, because requires projection maintenance

### Lazy Loading with Repository Pattern

Load related data on-demand through repository injection.

* Good, because provides convenient access to related data
* Good, because loads data only when needed
* Neutral, because familiar pattern to many developers
* Bad, because violates DDD aggregate boundaries
* Bad, because creates infrastructure coupling in domain layer
* Bad, because makes unit testing more complex
* Bad, because can lead to unexpected query patterns

## Implementation Plan

### Phase 1: Read Model Infrastructure
1. Create `InventoryItemView` read model with ingredient names
2. Add event projections for `IngredientCreated` and `InventoryItemAdded` events
3. Implement projection rebuilding from event store

### Phase 2: Frontend Migration
1. Replace `InventoryItemWithIngredient` with `InventoryItemView`
2. Update frontend API calls to use read model endpoints
3. Remove database join dependencies

### Phase 3: Domain Service Enhancement
1. Add `InventoryQueryService` for complex cross-aggregate queries
2. Implement bulk operations that maintain consistency
3. Add caching layer for frequently accessed projections

## Design Rationale

### View Model Structure: Flat vs. Hierarchical

**Decision**: Use flat, denormalized view models rather than nested object hierarchies.

**Rationale**: 
- **UI Ergonomics**: Templates can access `item.ingredient_name` directly instead of `item.ingredient.name`
- **Serialization Efficiency**: Smaller JSON payloads without nested objects
- **Query Optimization**: Easier to sort/filter by denormalized fields
- **Read Model Purpose**: Optimized for consumption patterns, not domain purity

### SQLAlchemy Integration Strategy

**Decision**: Use SQLAlchemy Core for domain repositories, allow flexibility for read model stores.

**Rationale**:
- **Persistence Ignorance**: Domain models remain pure Pydantic, unaware of database concerns
- **Avoid ORM Coupling**: Prevents database schema from driving domain design
- **Aggregate Boundaries**: Core prevents lazy loading from breaking DDD boundaries
- **Read Model Flexibility**: View stores can use ORM if preferred (already query-optimized)

### Denormalization Strategy

**Decision**: Denormalize commonly accessed fields (ingredient_name, store_name) into view models.

**Rationale**:
- **Performance**: Eliminates joins for common UI queries
- **Eventual Consistency**: Acceptable for rarely-changing reference data
- **Event-Driven Updates**: Automatic synchronization via domain events

## Implementation Details

### Flat View Model Structure

```python
# Flat read model optimized for UI consumption
class InventoryItemView(BaseModel):
    # Core identifiers
    store_id: UUID
    ingredient_id: UUID
    
    # Denormalized for UI convenience (no deep hierarchies)
    ingredient_name: str
    store_name: str
    
    # Inventory data
    quantity: float
    unit: str
    notes: Optional[str] = None
    added_at: datetime
    
    # Computed fields for common UI patterns
    @property
    def display_name(self) -> str:
        return f"{self.quantity} {self.unit} {self.ingredient_name}"
```

### SQLAlchemy Core Repository Pattern

```python
# Domain Repository - SQLAlchemy Core (no ORM coupling)
class IngredientRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, ingredient: Ingredient):
        # Pure SQL with Core - maintains persistence ignorance
        stmt = insert(ingredients).values(**ingredient.model_dump())
        self.session.execute(stmt)
    
    def get_by_id(self, ingredient_id: UUID) -> Optional[Ingredient]:
        stmt = select(ingredients).where(ingredients.c.ingredient_id == ingredient_id)
        result = self.session.execute(stmt).fetchone()
        return Ingredient.model_validate(result._asdict()) if result else None
```

### Event Projection with Denormalization

```python
# Event Projection Handler
class InventoryProjectionHandler:
    def handle_inventory_item_added(self, event: InventoryItemAdded):
        # Fetch related data for denormalization
        ingredient = self.ingredient_repo.get_by_id(event.ingredient_id)
        store = self.store_repo.get_by_id(event.store_id)
        
        # Create flat view model with denormalized fields
        view = InventoryItemView(
            store_id=event.store_id,
            ingredient_id=event.ingredient_id,
            ingredient_name=ingredient.name,  # Denormalized
            store_name=store.name,            # Denormalized
            quantity=event.quantity,
            unit=event.unit,
            notes=event.notes,
            added_at=event.added_at
        )
        
        self.view_store.save_inventory_item_view(view)
    
    def handle_ingredient_name_updated(self, event: IngredientNameUpdated):
        # Update all inventory views when ingredient name changes
        views = self.view_store.get_by_ingredient_id(event.ingredient_id)
        for view in views:
            updated_view = view.model_copy(update={"ingredient_name": event.new_name})
            self.view_store.save_inventory_item_view(updated_view)
```

### Read Model Storage Options

```python
# Option 1: SQLAlchemy Core (consistent with domain layer)
class InventoryViewStore:
    def save_inventory_item_view(self, view: InventoryItemView):
        stmt = insert(inventory_item_views).values(**view.model_dump())
        self.session.execute(stmt)

# Option 2: SQLAlchemy ORM (acceptable for read models)
class InventoryItemViewTable(Base):
    __tablename__ = "inventory_item_views"
    
    store_id: Mapped[UUID] = mapped_column(UUID, primary_key=True)
    ingredient_id: Mapped[UUID] = mapped_column(UUID, primary_key=True)
    ingredient_name: Mapped[str] = mapped_column(String)
    quantity: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String)
```

## Migration Considerations

### Database Schema for Read Models

```sql
-- Read model table (denormalized)
CREATE TABLE inventory_item_views (
    store_id UUID NOT NULL,
    ingredient_id UUID NOT NULL,
    ingredient_name VARCHAR NOT NULL,
    store_name VARCHAR NOT NULL,
    quantity DECIMAL NOT NULL,
    unit VARCHAR NOT NULL,
    notes TEXT,
    added_at TIMESTAMP NOT NULL,
    PRIMARY KEY (store_id, ingredient_id)
);

-- Indexes for common query patterns
CREATE INDEX idx_inventory_views_ingredient_name ON inventory_item_views(ingredient_name);
CREATE INDEX idx_inventory_views_store_name ON inventory_item_views(store_name);
```

### Frontend Migration Path

```typescript
// BEFORE: Interface extension (the "smell")
export interface InventoryItemWithIngredient extends InventoryItem {
    ingredient_name: string;
}

// AFTER: Native backend type (generated from InventoryItemView)
export interface InventoryItemView {
    store_id: string;
    ingredient_id: string;
    ingredient_name: string;  // Now native to the type
    store_name: string;
    quantity: number;
    unit: string;
    notes?: string;
    added_at: string;
}

// API calls change from:
// GET /stores/{id}/inventory (returns InventoryItem[])
// + separate ingredient lookups
// TO:
// GET /stores/{id}/inventory-view (returns InventoryItemView[])
// - no additional lookups needed
```

### Performance Implications

**Read Performance**: Significant improvement
- **Before**: N+1 queries or complex joins
- **After**: Single table scan with indexes

**Write Performance**: Minimal impact
- **Additional writes**: One view table update per domain event
- **Event processing**: Asynchronous, doesn't block domain operations

**Storage**: Moderate increase
- **Denormalization**: Ingredient/store names stored multiple times
- **Mitigation**: Reference data is typically small relative to transactional data

## More Information

This decision aligns with our existing event sourcing architecture and provides a clear path forward. The read model approach is commonly used in CQRS systems and provides excellent separation between command (domain) and query (read model) concerns.

The eventual consistency trade-off is minimal for this use case since ingredient names rarely change, and when they do, the lag will be milliseconds in most cases.

**Key Benefits of This Approach**:
1. **Eliminates Frontend "Smell"**: No more interface extensions or join dependencies
2. **Maintains DDD Purity**: Domain aggregates stay clean and focused
3. **Leverages Event Architecture**: Uses existing event sourcing patterns
4. **Optimizes for UI Patterns**: Flat structures avoid deep object hierarchies
5. **Preserves Persistence Ignorance**: SQLAlchemy Core keeps domain models clean

Future iterations could add:
- Read model caching for high-frequency queries
- Snapshot projections for complex aggregations
- Query optimization for specific frontend use cases
- Eventual consistency monitoring and alerting