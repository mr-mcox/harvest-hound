# Backend CLAUDE.md

This file provides backend-specific guidance for the Harvest Hound FastAPI application.

## Technology Stack

- **Framework**: FastAPI with SQLModel/Pydantic
- **Language**: Python 3.11+
- **AI/LLM**: BAML for completion engine
- **Database**: SQLite (development), event store pattern
- **Package Manager**: uv

## Development Setup

```bash
# From packages/backend directory
# Install dependencies
uv sync --all-groups

# Run development server
uv run uvicorn api:app --reload --port 8000

# Run tests
uv run pytest

# Linting and formatting
uv run ruff check .
uv run ruff format .
uv run mypy .
```

## Key Backend Guidelines

### Development Approach
- **Red/Green TDD**: Test-driven development with focus on observable behavior
- **Meaningful Testing**: Test at a level low enough to isolate behavior but high enough to avoid implementation details
- **Class Definitions vs Behavior**: Distinguish between basic class definitions (no tests needed) and meaningful behavior (tests required)
- **Concrete Task Planning**: Tasks should be specific and actionable, not abstract concepts

### Test Construction Preferences
- **Test Organization**: Use pytest test classes to group related behaviors logically (e.g., `TestInventoryStoreCreation`, `TestInventoryItemAddition`)
- **Focused Tests**: Each test should verify one specific behavior - avoid multiple assertions testing different concepts
- **Roundtrip Testing**: For event sourcing, prefer roundtrip tests (create → events → rebuild → compare) over field-by-field assertions
- **Data Integrity**: Test aggregate equality rather than individual field assertions - this validates the complete behavior that matters

### Domain Model Principles
- Keep schemas lean, rely on LLM for validation/transformation
- Immutable events over complex state
- Recipe state transitions create new versions
- All ingredient claims are tracked as immutable objects

### Event Sourcing Implementation
- Every domain change emits events
- Event streams partitioned by aggregate (Store, MealPlan, Recipe)
- Projections materialize query models
- Outbox pattern for reliable event publishing

### Read Models & CQRS
- **Commands modify aggregates, queries read denormalized views**
- Read models in `app/models/read_models.py` (e.g., `InventoryItemView`, `StoreView`)
- View stores in `app/infrastructure/view_stores.py` handle database operations
- Projection handlers in `app/projections/handlers.py` update views on events
- Register handlers: `projection_registry.register(EventType, handler.method)`
- API endpoints return denormalized data directly (no frontend merging)

### AI Integration
- RecipePlanner handles all recipe generation and adaptation
- Natural language MealPlanSpec inputs
- Ingredient substitution and conflict resolution
- Context management for planning sessions

## Code Quality Guidelines

- Add `# type: ignore[...]` when design is solid but adding type checking would make the code unnecessarily complex
- Prefer explicit type annotations for public APIs
- Use SQLModel for database models to ensure type safety
- Follow FastAPI best practices for dependency injection

## Testing Guidelines

- BAML functions are costly to run in tests, so wrap them in clients that we can swap out via dependency injection
- Use pytest fixtures for common test setup
- Mock external dependencies (LLM calls, file system operations)
- Test event sourcing with roundtrip patterns

## Workflow Guidelines

- When running tests, be sure to prepend `uv run`
- When installing packages, run `uv sync --all-groups` to avoid uninstalling existing packages
- Use `uv run` for all Python commands to ensure proper virtual environment usage

## Package Structure

```
packages/backend/
├── api.py                    # FastAPI application entry point
├── app/
│   ├── events/              # Domain events
│   ├── infrastructure/      # External concerns (DB, BAML, etc.)
│   ├── models/              # Domain models and aggregates
│   └── services/            # Domain services
├── tests/                   # Test files
├── scripts/                 # Utility scripts
└── pyproject.toml           # Project configuration
```

## Development Notes

- Use dependency injection for services to enable testing
- Keep domain models pure - separate from infrastructure concerns
- Use event sourcing patterns consistently across aggregates
- Prefer immutable data structures where possible