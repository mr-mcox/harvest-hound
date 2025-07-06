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

### Component Design Principles

- Keep components focused on single responsibilities
- Use TypeScript interfaces for prop definitions
- Leverage Svelte's reactivity for state management
- Prefer composition over inheritance for component reuse

### State Management

- Use Svelte stores for application-wide state
- Component-level state for local UI concerns
- Reactive statements for derived state
- Event-driven updates to maintain consistency with backend

### Testing Guidelines

- **Component Testing**: Use Vitest with `@testing-library/svelte` for component behavior
- **E2E Testing**: Use Playwright for user journey testing
- **Mock External Dependencies**: Mock API calls and backend services
- **Test User Interactions**: Focus on what users can see and do

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
│   ├── lib/                 # Shared utilities and types
│   │   ├── generated/       # Generated API types
│   │   ├── types.ts         # Frontend-specific types
│   │   └── validation.ts    # Form validation utilities
│   ├── routes/              # SvelteKit routes
│   │   ├── +layout.svelte   # App layout
│   │   ├── +page.svelte     # Home page
│   │   └── stores/          # Store management pages
│   └── stories/             # Storybook stories
├── tests/                   # Test files
├── e2e/                     # End-to-end tests
└── static/                  # Static assets
```

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
