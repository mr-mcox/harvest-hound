# Decision: Ingredient Identity & Aggregation via UNIQUE Constraint

**Date**: 2025-12-20
**Context**: Ingredient Identity & Aggregation feature implementation
**Status**: Accepted

## Decision

Use a database UNIQUE constraint on (ingredient_name, unit) combined with upsert logic to enforce ingredient identity and automatically aggregate duplicate entries. Replace soft-delete pattern (deleted_at timestamp) with quantity-based lifecycle (quantity=0).

## Rationale

### Identity Problem
Adding "2 lb carrots" twice was creating two separate inventory items instead of one item with 4 lbs total. This made quantity tracking unreliable and created confusion about actual inventory state.

### Aggregation Solution
UNIQUE(ingredient_name, unit) constraint at database level ensures:
- Only one row per (name, unit) combination
- Upsert logic automatically aggregates quantities on import
- No duplicate detection logic needed in application code
- Database enforces integrity (can't accidentally create duplicates)

### Lifecycle Simplification
Quantity=0 instead of deleted_at because:
- Simpler mental model: quantity is the source of truth
- Enables automatic resurrection via aggregation (adding "2 lb carrots" when "0 lb carrots" exists just increments)
- Claims can reference zero-quantity items (shows "insufficient inventory" in recipes)
- Filtering is simpler: `WHERE quantity > 0` vs `WHERE deleted_at IS NULL`
- No timestamp tracking needed for deletion

## Alternatives Considered

- **Fuzzy matching + embeddings**: Too complex for MVP, exact match works well enough with BAML normalization
  - BAML already provides normalized singular/lowercase/full-unit names
  - Added complexity not worth it for current scale (hobby project)

- **Separate stats table tracking duplicates**: Extra maintenance, risk of data drift
  - Would need cleanup jobs
  - Adds complexity without clear benefit

- **Client-side duplicate detection**: Unreliable, can't prevent backend races
  - Database constraint is authoritative
  - Application logic can't guarantee atomicity

- **Soft-delete (deleted_at) retention**: Standard pattern but adds complexity
  - Resurrection logic needed when ingredient returns
  - Can't tell difference between "deleted" and "out of stock"
  - Claims FK pointing to deleted items creates confusion

## Trade-offs Accepted

**Limitations**:
- Different units create separate items ("2 lb carrots" vs "3 each carrots")
  - No unit conversion in MVP
  - Accepted: Most ingredients use consistent units

- Exact name matching (case-insensitive only)
  - "Yellow Onion" ≠ "Onion"
  - Accepted: BAML normalization handles most cases, user can manually merge if needed

- Zero-quantity items remain in database forever
  - Only filtered from UI views
  - Accepted: Small data volume (hobby project), session cleanup handles most cases

**Constraints**:
- Must clean existing duplicates before adding UNIQUE constraint (migration requirement)
- Claim matching must be unit-aware (not just name)

## Consequences

**Enables**:
- Reliable quantity tracking across imports
- Automatic aggregation without application logic
- Simpler lifecycle model (quantity is source of truth)
- Clean resurrection when ingredients return in future deliveries

**Constrains**:
- Can't have multiple inventory items with same (name, unit) combination
- Must normalize names before insert (already handled by BAML)
- Unit conversion would require schema changes (deferred to post-MVP)

**Technical Debt**:
- No unit conversion or fuzzy matching (acceptable for MVP scale)
- Zero-quantity items accumulate in database (acceptable with filtering)

## References

- Implemented in: PR #42 (feat: Ingredient identity)
- Original TIP: `docs/implementation/tip-ingredient-identity.md` (deleted 2025-12-22)
- Related learnings:
  - `learnings/technical.md`: BAML normalization provides consistent identity foundation
  - `learnings/workflows.md`: Inventory editing heavily used, delete action common
  - `learnings/domain.md`: Claims must persist when ingredient deleted to preserve recipe planning
