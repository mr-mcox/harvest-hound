# Frontend CLAUDE.md

This file provides frontend-specific guidance for the Harvest Hound Svelte application.

## Technology Stack

- **Framework**: SvelteKit with TypeScript
- **Language**: TypeScript
- **Testing**: Vitest + Playwright
- **Package Manager**: pnpm
- **Styling**: CSS with component-scoped styles
- **Build Tool**: Vite

## Development Setup

```bash
# From packages/frontend directory
# Install dependencies
pnpm install

# Run development server
pnpm dev

# Build for production
pnpm build

# Run unit tests
pnpm test

# Run e2e tests
pnpm test:e2e

# Linting and formatting
pnpm lint
pnpm format
```

## Key Frontend Guidelines

### Development Approach

- **Red/Green TDD**: Test-driven development adapted for UI components
- **Meaningful Testing**: Test component behavior and user interactions, not implementation details
- **Component vs Behavior**: Distinguish between basic component structure (minimal tests) and meaningful user interactions (comprehensive tests)
- **Concrete Task Planning**: Tasks should be specific and actionable, not abstract concepts

### Test Construction Preferences

- **Test Organization**: Use Vitest `describe` blocks to group related component behaviors logically (e.g., `describe('InventoryTable - Creation')`, `describe('InventoryTable - Interaction')`)
- **Focused Tests**: Each test should verify one specific user behavior - avoid multiple assertions testing different UI concepts
- **User-Centric Testing**: Test what users see and do, not internal component state
- **Integration Testing**: Prefer testing component integration over isolated unit tests

### Component Architecture: Hybrid Container/Presentation Pattern

**CRITICAL**: This project uses a strict separation between pure UI components and data-fetching page wrappers.

#### Pure Components (`src/lib/components/`)
**Purpose**: Reusable, testable UI components that accept props and emit events.

```svelte
<!-- ✅ GOOD: Pure component -->
<script lang="ts">
  export let inventory: InventoryItem[];
  export let onItemClick: (item: InventoryItem) => void = () => {};
  
  // Only UI logic - no API calls, no SvelteKit imports
</script>

<table>
  {#each inventory as item}
    <tr on:click={() => onItemClick(item)}>
      <td>{item.name}</td>
    </tr>
  {/each}
</table>
```

**Rules for Pure Components**:
- ✅ Accept data via props
- ✅ Emit events via prop functions (`onSubmit`, `onClick`)
- ✅ Handle UI state (loading, validation errors)
- ❌ NO API calls (`apiGet`, `apiPost`)
- ❌ NO SvelteKit imports (`$app/navigation`, `$app/stores`)
- ❌ NO direct routing or navigation

#### Page Wrappers (`src/routes/**/+page.svelte`)
**Purpose**: Handle data fetching, routing, and SvelteKit integration.

```svelte
<!-- ✅ GOOD: Page wrapper -->
<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { apiGet, apiPost } from '$lib/api';
  import InventoryTable from '$lib/components/InventoryTable.svelte';
  
  let inventory = [];
  let loading = true;
  
  onMount(async () => {
    const response = await apiGet(`/stores/${$page.params.id}/inventory`);
    inventory = await response.json();
    loading = false;
  });
  
  async function handleItemClick(item) {
    await goto(`/items/${item.id}`);
  }
</script>

{#if loading}
  <div>Loading...</div>
{:else}
  <InventoryTable {inventory} onItemClick={handleItemClick} />
{/if}
```

**Rules for Page Wrappers**:
- ✅ Handle data fetching and API calls
- ✅ Manage route parameters (`$page.params`)
- ✅ Handle navigation (`goto`)
- ✅ Pass data down to pure components
- ✅ Handle component events and side effects
- ❌ NO complex UI rendering (delegate to components)

#### Why This Pattern?

**Testability**:
```javascript
// ✅ Easy to test pure components
render(InventoryTable, { 
  inventory: mockData,
  onItemClick: vi.fn()
});

// ❌ Impossible to test mixed components
render(InventoryPageWithEverything); // Requires full SvelteKit context
```

**Reusability**:
```svelte
<!-- ✅ Reuse components anywhere -->
<InventoryTable {inventory} />
<Modal><InventoryTable {inventory} /></Modal>
<Dashboard><InventoryTable {inventory} /></Dashboard>
```

**Storybook Development**:
```javascript
// ✅ Pure components work in Storybook
export default {
  component: InventoryTable,
  args: { inventory: mockData }
};
```

#### Common Anti-Patterns to Avoid

❌ **DON'T mix data fetching with UI**:
```svelte
<script>
  import { onMount } from 'svelte';
  import { apiGet } from '$lib/api';
  
  let data = [];
  onMount(() => apiGet('/api').then(r => data = r)); // ❌ Untestable
</script>
<table>{#each data as item}...{/each}</table>
```

❌ **DON'T use SvelteKit APIs in reusable components**:
```svelte
<script>
  import { goto } from '$app/navigation'; // ❌ Breaks reusability
  function handleClick() { goto('/somewhere'); }
</script>
```

❌ **DON'T create "god components" that do everything**:
```svelte
<!-- ❌ BAD: One component handling everything -->
<script>
  // API calls + UI logic + navigation + validation...
</script>
```

#### File Organization

```
src/
├── lib/components/           # Pure UI components
│   ├── InventoryTable.svelte
│   ├── InventoryUpload.svelte
│   └── StoreCreateForm.svelte
├── routes/                   # Page wrappers only
│   ├── stores/
│   │   ├── [id]/+page.svelte      # Fetches data, passes to InventoryTable
│   │   └── create/+page.svelte    # Handles API calls, uses StoreCreateForm
└── stories/                  # Test pure components in isolation
    ├── InventoryTable.stories.svelte
    └── StoreCreateForm.stories.svelte
```

### Component Design Principles

- Keep components focused on single responsibilities
- Use TypeScript interfaces for prop definitions
- Leverage Svelte's reactivity for state management
- Prefer composition over inheritance for component reuse
- **Strictly separate presentation from data fetching**

### State Management

- Use Svelte stores for application-wide state
- Component-level state for local UI concerns
- Reactive statements for derived state
- Event-driven updates to maintain consistency with backend

### Testing Guidelines

#### Component Testing Strategy
- **Test Pure Components Only**: Import from `$lib/components/`, never from `src/routes/`
- **Use Vitest with `@testing-library/svelte`**: For component behavior testing
- **Mock Data, Not Dependencies**: Pass mock data as props instead of mocking API calls
- **Test User Interactions**: Focus on what users see and do, not internal state

#### Testing Examples

**✅ GOOD: Test pure components**:
```javascript
import InventoryTable from '$lib/components/InventoryTable.svelte';

test('displays inventory items', () => {
  const mockInventory = [{ name: 'Carrots', quantity: 2 }];
  render(InventoryTable, { inventory: mockInventory });
  expect(screen.getByText('Carrots')).toBeInTheDocument();
});
```

**❌ BAD: Test page components**:
```javascript
import InventoryPage from '../routes/stores/[id]/+page.svelte'; // ❌ Requires SvelteKit context
```

#### Test Organization
- **Unit Tests**: Pure components with mock props
- **Integration Tests**: API client functions and backend communication  
- **E2E Testing**: Use Playwright for full user journey testing
- **Mock External Dependencies**: Mock API calls at the service layer, not component level

## Code Quality Guidelines

- Use TypeScript strict mode for type safety
- Prefer explicit type annotations for component props
- Use Svelte's built-in accessibility features
- Follow semantic HTML practices

## Workflow Guidelines

- Use `pnpm` for all package management
- Run tests before committing changes
- Use TypeScript for all new code
- Leverage Svelte's reactivity patterns

## Package Structure

```
packages/frontend/
├── src/
│   ├── lib/
│   │   ├── components/      # 🎯 Pure UI components (testable, reusable)
│   │   │   ├── InventoryTable.svelte
│   │   │   ├── InventoryUpload.svelte
│   │   │   └── StoreCreateForm.svelte
│   │   ├── generated/       # Generated API types from backend
│   │   ├── api.ts           # API client functions
│   │   ├── types.ts         # Frontend-specific types
│   │   └── validation.ts    # Form validation utilities
│   ├── routes/              # 🔌 Page wrappers (data fetching, routing)
│   │   ├── +layout.svelte   # App layout
│   │   ├── +page.svelte     # Home page wrapper
│   │   └── stores/          # Store management page wrappers
│   │       ├── [id]/+page.svelte      # Loads data → InventoryTable
│   │       ├── [id]/upload/+page.svelte # API calls → InventoryUpload  
│   │       └── create/+page.svelte    # API calls → StoreCreateForm
│   └── stories/             # 📚 Storybook stories (pure components only)
│       ├── InventoryTable.stories.svelte
│       └── StoreCreateForm.stories.svelte
├── tests/                   # 🧪 Component tests (pure components only)
├── e2e/                     # 🎭 End-to-end tests (full user journeys)
└── static/                  # Static assets
```

**Key Architecture Rules**:
- **`src/lib/components/`**: Pure UI components only (no SvelteKit imports)
- **`src/routes/`**: Data fetching wrappers only (minimal UI logic)
- **Tests**: Only test pure components, never page wrappers
- **Stories**: Only create stories for pure components

## Component Guidelines

### Svelte Component Best Practices

- Use `<script lang="ts">` for TypeScript support
- Export props with explicit types
- Use reactive statements (`$:`) for derived values
- Leverage Svelte's event system for component communication

### Testing Patterns

- Test component rendering with various prop combinations
- Test user interactions (clicks, form submissions, etc.)
- Test component state changes and reactivity
- Use Playwright for full user journey testing

### Type Safety

- Import generated API types from `lib/generated/api-types.ts`
- Define component prop interfaces
- Use discriminated unions for component variants
- Leverage TypeScript's strict mode features

## Development Notes

- Use SvelteKit's file-based routing system
- Leverage Vite's hot module replacement for fast development
- Use Storybook for component development and documentation
- Prefer semantic HTML and accessibility-first design
- Use CSS custom properties for theming and consistency

## Integration with Backend

- Use generated TypeScript types from backend schemas
- Implement type-safe API client functions
- Handle loading states and error conditions
- Use reactive stores for real-time data updates
