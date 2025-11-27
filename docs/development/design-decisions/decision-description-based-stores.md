# Design Decision: Description-Based Stores

**Purpose**: Enable LLM-inferred ingredient availability from natural language store descriptions (e.g., "Cub Foods with Somali community influence") instead of requiring explicit inventory enumeration.

**Status**: Approved - Ready for Implementation

**Cleanup After Implementation**:
- Verify: `ExplicitInventoryStore` and `DefinitionBasedStore` classes exist in `packages/backend/app/models/inventory_store.py`
- Verify: Domain model updated in `docs/architecture/domain-model.md` Section 4
- Delete: This file after implementation complete

---

## Design Decision

**Chosen Approach**: Subclass-Based Store Types

**Core Concept**: Replace the binary `infinite_supply` flag with inheritance-based polymorphism. Two concrete store types inherit from abstract `InventoryStore` base class: `ExplicitInventoryStore` (tracked quantities) and `DefinitionBasedStore` (LLM-inferred availability). Each subclass has appropriate fields and behaviors for its availability model.

**Why This Approach**:
- **Honest model**: Fields match store semantics - `ExplicitInventoryStore` has `inventory_items`, `DefinitionBasedStore` does not
- **Type safety**: Can't accidentally call `add_inventory_item()` on `DefinitionBasedStore` - method doesn't exist
- **Separate field semantics**: `description` (human notes) vs `definition` (LLM instructions) serve different audiences and purposes
- **Natural polymorphism**: `check_availability()` has genuinely different implementations per store type

---

## Domain Model Changes

**Affected Sections**: `docs/architecture/domain-model.md` Section 4 (InventoryStore Hierarchy)

**New Concepts**:
- **Abstract InventoryStore**: Base class with common properties (`StoreId`, `Name`, `Priority`) and polymorphic methods (`check_availability`, `can_claim`)
- **ExplicitInventoryStore**: Concrete subclass for enumerated inventories (CSA box, freezer) with tracked quantities
- **DefinitionBasedStore**: Concrete subclass for LLM-inferred availability (grocery stores, pantries) from natural language definitions
- **Priority**: Integer field (higher = check first during claiming) enables broker-based ingredient prioritization

**Modified Concepts**:
- **InventoryStore**: Changed from concrete class to abstract base class
- **Store types**: Previously documented as enum (Perishable, Frozen, Pantry, Grocery), now emergent from subclass choice and properties

**Removed Concepts**:
- **`infinite_supply` flag**: Replaced by subclass distinction and field semantics

---

## Key Relationships & Behaviors

**ExplicitInventoryStore → InventoryItem**:
- Maintains list of concrete inventory items with quantities
- `add_inventory_item()` method creates `InventoryItemAdded` events
- `check_availability()` queries concrete inventory list
- Claiming decrements tracked quantities (reserve behavior)

**DefinitionBasedStore → LLM Inference**:
- NO inventory items - availability determined by LLM interpretation of `definition` field
- `check_availability()` delegates to LLM with definition context
- Claiming generates shopping lists or verification prompts (no quantity changes)

**InventoryStore ↔ IngredientBroker**:
- Broker calls polymorphic `check_availability()` regardless of store type
- Uses `isinstance()` checks for type-specific claiming strategies
- Respects `priority` field for store ordering (highest priority checked first)

**Field Semantics**:
- **ExplicitInventoryStore.description**: Optional human-readable note (e.g., "premade sauces we have lying around")
- **DefinitionBasedStore.definition**: Required LLM-facing instructions with rich context (e.g., "Cub Foods on Lake St in Minneapolis. Strong Somali community influence means excellent global foods selection...")

---

## Use Cases Enabled

**New Capabilities**:
1. **Grocery store as LLM-inferred source**: Users can create stores like "Typical urban Cub grocery store" without enumerating thousands of items
2. **Specialized pantry descriptions**: Users can describe "Well-stocked Italian and Indian cooking pantry" and RecipePlanner understands ingredient availability
3. **Rich contextual definitions**: Multi-paragraph definitions with neighborhood, cultural, or specialty context (e.g., Somali community influence on global foods selection)

**Preserved Behaviors**:
1. **Explicit inventory tracking**: CSA boxes, freezers still work with enumerated items and quantity tracking
2. **Event sourcing**: All store operations continue to emit domain events
3. **Inventory upload**: Bulk inventory text parsing for explicit stores unchanged

**Edge Cases Defined**:
1. **Empty definition**: `DefinitionBasedStore.create()` with empty definition raises `ValueError`
2. **Empty explicit inventory**: `ExplicitInventoryStore` can exist with empty `inventory_items` (user may populate later)
3. **Type mismatch**: Attempting `add_inventory_item()` on `DefinitionBasedStore` raises `AttributeError` (method doesn't exist)

---

## Implementation Considerations

**Integration Points**:
- **IngredientBroker** (not yet implemented): Will use polymorphic `check_availability()` + `isinstance()` for claiming strategy
- **RecipePlanner** (not yet implemented): Will receive store definitions as context for recipe generation
- **StoreService**: Must instantiate correct subclass based on `store_type` discriminator
- **REST API**: Accepts `store_type` field ("explicit" or "definition") in store creation requests
- **Frontend**: UI distinguishes between store types with appropriate form fields

**Pain Points to Monitor**:
- **Event sourcing with subclasses**: Requires discriminator field in `StoreCreated` event to route to correct subclass during `from_events()`. If routing logic becomes complex, consider event sourcing library or separate event streams per subclass.
- **Pydantic + ABC**: Ensure Pydantic BaseModel works correctly with abstract base class inheritance
- **Repository complexity**: `from_events()` must route to correct subclass constructor

**Event Sourcing Notes**:
- `StoreCreated` event includes `store_type: Literal["explicit", "definition"]` discriminator
- `description` and `definition` fields are both optional in event (one populated based on `store_type`)
- Repository `from_events()` uses discriminator to route: `ExplicitInventoryStore.from_events()` vs `DefinitionBasedStore.from_events()`

---

## Light Code Sketch (Conceptual Only)

```python
from abc import ABC, abstractmethod

class InventoryStore(BaseModel, ABC):
    """Abstract base class for all inventory store types"""
    store_id: UUID
    name: str
    priority: int = 0  # Higher = check first during claiming

    @abstractmethod
    def check_availability(self, ingredient_id: UUID, ingredient_name: str) -> AvailabilityResult:
        """Polymorphic - implementation depends on subclass"""
        pass

class ExplicitInventoryStore(InventoryStore):
    """Store with enumerated inventory and tracked quantities"""
    description: str = ""  # Human-readable note (optional)
    inventory_items: List[InventoryItem]

    def check_availability(self, ingredient_id, ingredient_name) -> AvailabilityResult:
        # Check concrete inventory
        items = [i for i in self.inventory_items if i.ingredient_id == ingredient_id]
        return AvailabilityResult(available=bool(items), quantity=sum(i.quantity for i in items))

    def add_inventory_item(self, ingredient_id, quantity, unit, notes=None):
        """Add item to explicit inventory - only on this subclass"""
        # Implementation...

class DefinitionBasedStore(InventoryStore):
    """Store with LLM-inferred availability from natural language definition"""
    definition: str  # LLM-facing instructions (required)
    # NO inventory_items field
    # NO add_inventory_item() method

    def check_availability(self, ingredient_id, ingredient_name) -> AvailabilityResult:
        # Delegate to LLM with definition context
        return llm_infer_availability(ingredient_name, self.definition)
```

**Key Design Patterns**:
- **Abstract base class**: Defines polymorphic interface for all store types
- **Discriminator pattern**: Event sourcing uses `store_type` field to route to correct subclass
- **Type-specific methods**: `add_inventory_item()` only exists on `ExplicitInventoryStore`

---

## Glossary Updates

**New Ubiquitous Language Terms**:
- **ExplicitInventoryStore**: Store with enumerated inventory items and tracked quantities (e.g., refrigerator, freezer)
- **DefinitionBasedStore**: Store with LLM-inferred availability based on natural language definition (e.g., grocery store, pantry)
- **Definition**: LLM-facing natural language instructions describing what's available in a DefinitionBasedStore
- **Priority**: Integer ranking determining store query order during ingredient claiming (higher checked first)

**Modified Terms**:
- **InventoryStore**: Now abstract base class instead of concrete class; defines common interface for all store types

---

**Next Step**: Use `create-tip "description-based-stores"` to plan implementation.

This summary provides the domain context that `create-tip` will use to generate the Technical Implementation Plan (TIP).
