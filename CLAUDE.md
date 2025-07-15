# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Harvest Hound is an agentic meal planning application designed for families receiving CSA (Community Supported Agriculture) deliveries. The core challenge is optimizing meal selection to prioritize fresh ingredients while leveraging an AI agent to handle complex decision-making around ingredient availability, substitutions, and recipe iteration.

## Architecture

This is a **Domain-Driven Design (DDD)** application with **Event Sourcing** patterns:

### Core Domain Concepts

- **InventoryStore**: Different sources of ingredients (Perishable/CSA, Frozen, Pantry, Grocery)
- **Ingredient**: Canonical ingredient representation with normalization and unit conversion
- **Recipe**: Immutable aggregate with states (Pitch → Draft → Final)
- **IngredientBroker**: Domain service mediating between recipe planning and inventory availability
- **RecipePlanner**: AI agent responsible for recipe selection, adaptation, and substitution
- **IngredientClaim**: Immutable reservation of ingredients during planning
- **MealPlan**: Weekly collection of meals in various states

### Architecture Patterns

- **Event-Driven Architecture**: All domain changes emit events
- **Negotiation Pattern**: RecipePlanner ↔ IngredientBroker communication
- **Claim-Based Planning**: Immutable ingredient reservations
- **Event Sourcing**: All state changes captured as events
- **Recipe Materialization**: Lazy ingredient normalization during meal planning
- **Bounded Context Separation**: Distinct domains for Recipe, Inventory, Ingredient, and Planning

### Technology Stack

- **Frontend**: Svelte/SvelteKit + TypeScript
- **Backend**: FastAPI (Python) + SQLModel/Pydantic
- **AI/LLM**: BAML for completion engine
- **Database**: SQLite (development), event store pattern
- **Communication**: WebSocket for real-time updates

## Project Structure

```
/
├── docs/                     # Architecture documentation
├── packages/
│   ├── frontend/            # Svelte app (see packages/frontend/CLAUDE.md)
│   │   ├── src/components/
│   │   ├── src/lib/
│   └── backend/             # FastAPI app (see packages/backend/CLAUDE.md)
│       ├── app/
│       │   ├── routers/     # REST endpoints
│       │   ├── models/      # Domain aggregates
│       │   └── events/      # Event definitions
```

## API Design

### REST Endpoints
- POST `/meal-plans` - Start planning session
- POST `/stores` - Create ingredient store
- POST `/stores/{id}/inventory` - Bulk upload ingredients
- GET `/inventory/current` - Current availability
- POST `/meal-plans/{id}/feedback` - User recipe feedback

### WebSocket Events
- `RecipeProposed` - New recipe suggestion
- `IngredientClaimed` - Ingredient reservation
- `ClaimPartial` - Partial ingredient availability
- `MealPlanFinalised` - Planning complete

## Development Status

**Current Phase**: Active Development
- Core domain models implemented in backend
- Basic frontend UI components created
- Event sourcing infrastructure in place

## Package-Specific Guidelines

Each package has its own CLAUDE.md file with specific development guidelines:

- **Backend**: See `packages/backend/CLAUDE.md` for Python, FastAPI, and domain modeling guidelines. Backend uses uv as a package manager.
- **Frontend**: See `packages/frontend/CLAUDE.md` for Svelte, TypeScript, and UI development guidelines. Frontend uses pnpm as a package manager.

## Global Development Guidelines

### General Principles
- **Red/Green TDD**: Test-driven development with focus on observable behavior
- **Meaningful Testing**: Test at a level low enough to isolate behavior but high enough to avoid implementation details
- **Concrete Task Planning**: Tasks should be specific and actionable, not abstract concepts

### Development Philosophy: Single-User MVP with Migration Paths
- **Current Context**: Single-user hobby application prioritizing rapid time-to-value
- **Future Consideration**: Multi-user/multi-account expansion without complete re-architecture
- **Decision Framework**: Choose simple approaches that don't create technical debt for future expansion
- **Example**: Default room pattern for WebSocket (simple now, clean migration to user-based rooms later)

### Domain Model Principles
- Keep schemas lean, rely on LLM for validation/transformation
- Immutable events over complex state
- Recipe state transitions create new versions
- All ingredient claims are tracked as immutable objects

### Event Sourcing
- Every domain change emits events
- Event streams partitioned by aggregate (Store, MealPlan, Recipe)
- Projections materialize query models
- Outbox pattern for reliable event publishing

### AI Integration
- RecipePlanner handles all recipe generation and adaptation
- Natural language MealPlanSpec inputs
- Ingredient substitution and conflict resolution
- Context management for planning sessions

## Environment Configuration & Debugging

### Docker Environment Variable Loading
- **Issue**: Environment variables from `--env-file` may not override Docker Compose hardcoded values
- **Solution**: Add environment variables to `docker-compose.dev.yml` using `${VAR_NAME:-default}` syntax
- **Example**: `ENABLE_BAML=${ENABLE_BAML:-false}` allows env file override while providing default
- **Why**: Docker Compose merges env files with hardcoded environment section, hardcoded takes precedence

### LLM Integration Debugging
- **Mock vs Real LLM**: Always verify which parser is being used in production
- **Factory Pattern**: Use `create_inventory_parser_client()` factory, not hardcoded mock instances
- **Environment Check**: `ENABLE_BAML=true` required for real LLM, defaults to mock for safety
- **Dependency Injection**: Ensure dependency injection uses factory, not hardcoded implementations

### Common Debugging Patterns
1. **"0 items added" with 201 Created**: Usually mock parser returning empty results
2. **Environment variables not loading**: Check Docker Compose env section vs --env-file precedence
3. **Dependency injection issues**: Verify factory functions used, not hardcoded implementations
4. **Silent failures**: Add temporary logging to track execution flow through complex pipelines

### Testing Strategy
- **Unit Tests**: Fast, isolated, use mocks by default
- **Integration Tests**: Slow, real LLM, manual trigger only
- **Manual Testing Scripts**: `./scripts/test-manual.sh` for real LLM, `./scripts/dev-start.sh` for mocked
- **Environment Verification**: Always check which parser/client is actually being used
