# Frontend Integration Guide for Read Models

## Overview

This guide explains how frontend components consume read models and what changed when we migrated from manual data merging to denormalized views.

## Before and After

### Before: Manual Data Merging

```typescript
// Old pattern: Frontend had to merge data from multiple sources
interface InventoryItem {
  store_id: string;
  ingredient_id: string; 
  quantity: number;
  unit: string;
}

interface Ingredient {
  ingredient_id: string;
  name: string;
}

// Frontend code had to combine these:
interface InventoryItemWithIngredient extends InventoryItem {
  ingredient_name: string;  // Added by frontend
  store_name: string;       // Added by frontend
}
```

### After: Direct Read Model Consumption

```typescript
// New pattern: Backend provides exactly what UI needs
interface InventoryItem {
  store_id: string;
  ingredient_id: string;
  ingredient_name: string;  // Denormalized from backend
  store_name: string;       // Denormalized from backend
  quantity: number;
  unit: string;
  notes?: string;
  added_at: string;
}
```

## Type Generation

### Regenerating Types

When backend read models change, regenerate frontend types:

```bash
# From backend
cd packages/backend
python scripts/export_schemas.py

# From frontend
cd packages/frontend  
npm run generate-types
```

### Type Import Pattern

```typescript
// Import generated types
import type { InventoryItem, StoreListItem } from '$lib/types/generated';

// Use directly in components
export let items: InventoryItem[];
```

## Component Updates

### Removing Interface Extensions

**Old pattern** (eliminated):

```typescript
// REMOVED: No longer needed
interface InventoryItemWithIngredient extends InventoryItem {
  ingredient_name: string;
  store_name: string;
}

// REMOVED: Manual data merging
function enrichInventoryItems(items: InventoryItem[], ingredients: Ingredient[]): InventoryItemWithIngredient[] {
  // Complex merging logic eliminated
}
```

**New pattern**:

```typescript
// Direct consumption of read model
export let items: InventoryItem[];  // Already denormalized

{#each items as item}
  <tr>
    <td>{item.ingredient_name}</td>  <!-- Direct access -->
    <td>{item.store_name}</td>       <!-- Direct access -->
    <td>{item.quantity} {item.unit}</td>
  </tr>
{/each}
```

### API Calls

**Before**:

```typescript
// Multiple API calls + manual merging
const [items, ingredients, stores] = await Promise.all([
  api.getInventoryItems(storeId),
  api.getIngredients(),
  api.getStores()
]);

const enrichedItems = mergeData(items, ingredients, stores);
```

**After**:

```typescript
// Single API call with complete data
const items = await api.getStoreInventory(storeId);
// items already contain ingredient_name and store_name
```

## Common Patterns

### Store List with Counts

```typescript
// Stores now include computed item_count
interface StoreListItem {
  store_id: string;
  name: string;
  description: string;
  item_count: number;  // Computed by backend
}

// Frontend just displays it
{#each stores as store}
  <div class="store-card">
    <h3>{store.name}</h3>
    <p>{store.item_count} items</p>
  </div>
{/each}
```

### Inventory Tables

```typescript
// Full inventory display without additional lookups
<InventoryTable items={inventoryItems} />

<!-- Component implementation -->
<script lang="ts">
  export let items: InventoryItem[];
</script>

<table>
  <thead>
    <tr>
      <th>Ingredient</th>
      <th>Store</th>
      <th>Quantity</th>
      <th>Added</th>
    </tr>
  </thead>
  <tbody>
    {#each items as item}
      <tr>
        <td>{item.ingredient_name}</td>
        <td>{item.store_name}</td>
        <td>{item.quantity} {item.unit}</td>
        <td>{new Date(item.added_at).toLocaleDateString()}</td>
      </tr>
    {/each}
  </tbody>
</table>
```

## API Response Handling

### Error Handling

Read model endpoints return consistent structures:

```typescript
// Store creation
interface CreateStoreResponse {
  store_id: string;
  name: string;
  description: string;
  infinite_supply: boolean;
}

// Inventory upload
interface InventoryUploadResponse {
  items_added: number;
  errors: string[];
  success: boolean;
}

// Handle errors consistently
if (!response.success) {
  // Display response.errors to user
  errors = response.errors;
}
```

### Loading States

```typescript
let loading = false;
let items: InventoryItem[] = [];

async function loadInventory(storeId: string) {
  loading = true;
  try {
    items = await api.getStoreInventory(storeId);
  } catch (error) {
    // Handle error
  } finally {
    loading = false;
  }
}
```

## Testing Updates

### Mock Data

Update test mocks to match read model structure:

```typescript
// Mock data includes denormalized fields
const mockInventoryItems: InventoryItem[] = [
  {
    store_id: "store-1",
    ingredient_id: "ingredient-1", 
    ingredient_name: "carrots",     // Required in read model
    store_name: "CSA Box",          // Required in read model
    quantity: 2.0,
    unit: "lbs",
    notes: "",
    added_at: "2025-07-07T10:30:00Z"
  }
];
```

### Component Tests

```typescript
// Test that components render denormalized data correctly
test('displays ingredient and store names', () => {
  render(InventoryTable, { items: mockInventoryItems });
  
  expect(screen.getByText('carrots')).toBeInTheDocument();
  expect(screen.getByText('CSA Box')).toBeInTheDocument();
});
```

### API Tests

```typescript
// Test API responses match read model structure
test('inventory API returns denormalized data', async () => {
  const response = await api.getStoreInventory(storeId);
  
  expect(response[0]).toMatchObject({
    ingredient_name: expect.any(String),
    store_name: expect.any(String),
    quantity: expect.any(Number),
    // ... other fields
  });
});
```

## Performance Considerations

### Reduced API Calls

- **Before**: 3 API calls + frontend merging
- **After**: 1 API call with complete data

### Simpler Components

- **Before**: Complex data transformation logic in components
- **After**: Direct data binding to UI elements

### Better Caching

```typescript
// Cache denormalized responses longer since they're complete
const cachedInventory = new Map<string, InventoryItem[]>();

async function getStoreInventory(storeId: string): Promise<InventoryItem[]> {
  if (cachedInventory.has(storeId)) {
    return cachedInventory.get(storeId)!;
  }
  
  const items = await api.getStoreInventory(storeId);
  cachedInventory.set(storeId, items);
  return items;
}
```

## Migration Checklist

When migrating components to use read models:

- [ ] Remove interface extensions (e.g., `InventoryItemWithIngredient`)
- [ ] Update import statements to use generated types
- [ ] Remove data merging/enrichment functions
- [ ] Update component props to expect denormalized data
- [ ] Simplify API calls to single endpoints
- [ ] Update test mocks to include denormalized fields
- [ ] Remove unused API endpoints and types
- [ ] Update Storybook stories with correct data structure

## Troubleshooting

### Type Errors

If TypeScript complains about missing fields:

1. Regenerate types from backend schemas
2. Check that backend read models include all required fields
3. Update component expectations to match read model structure

### Missing Data

If denormalized fields are empty or undefined:

1. Verify projection handlers are working correctly
2. Check that all necessary events are being emitted
3. Ensure projection registry includes all event handlers

### Performance Issues

If components are slow:

1. Verify you're using read model endpoints (not aggregate endpoints)
2. Check that unnecessary API calls have been removed
3. Ensure components aren't doing additional data transformation