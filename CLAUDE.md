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

### Technology Stack (Planned)

- **Frontend**: Svelte/SvelteKit + TypeScript
- **Backend**: FastAPI (Python) + SQLModel/Pydantic
- **AI/LLM**: BAML for completion engine
- **Database**: SQLite (development), event store pattern
- **Communication**: WebSocket for real-time updates

## Development Setup

**Note**: This codebase is currently in the design/documentation phase. The actual implementation has not yet been started.

Based on the planned architecture:

### Backend (when implemented)
```bash
# Install dependencies
pip install -e .

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest

# Linting and formatting
ruff check .
ruff format .
black .
mypy .
```

### Frontend (when implemented)
```bash
# Install dependencies
npm install

# Development server
npm run dev

# Build
npm run build

# Test
npm test

# Linting
npm run lint
npm run format
```

## Key Implementation Guidelines

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

## Project Structure (Planned)

```
/
├── docs/                     # Architecture documentation
├── packages/
│   ├── frontend/            # Svelte app
│   │   ├── src/components/
│   │   ├── src/lib/
│   └── backend/             # FastAPI app
│       ├── app/
│       │   ├── routers/     # REST endpoints
│       │   ├── models/      # Domain aggregates
│       │   └── events/      # Event definitions
```

## API Design (Planned)

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

**Current Phase**: Design and Documentation
- Comprehensive domain architecture defined
- Technical specifications complete
- Implementation not yet started

**Next Steps**:
1. Set up monorepo structure with frontend/backend packages
2. Implement core domain models and event sourcing infrastructure
3. Build basic ingredient store management
4. Integrate LLM for recipe planning
5. Develop real-time UI with WebSocket connections
