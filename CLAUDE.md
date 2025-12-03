# Harvest Hound

## Project Vision

An agentic meal planning application for families receiving **CSA deliveries** (Community Supported Agriculture). 

**Core Problem**: Mental overhead of optimizing meals to use fresh CSA produce before it spoils while managing mixed inventories (freezer, pantry, grocery).

**Solution**: AI agent that handles complex decision-making around ingredient availability, substitutions, and recipe iteration through greedy optimization.

## Project Context

- **Type**: Single-player hobby project
- **User**: One person/family (myself)
- **Scale**: Personal use, not enterprise
- **Focus**: Delightful UX that reduces meal planning stress

## Current Phase: Prototype Discovery

See `prototype/CLAUDE.md` for discovery methodology.

## Key Technical Decisions

- **LLM Integration**: BAML for prompt management
- **Streaming**: Server-Sent Events (SSE) for recipe generation
- **Frontend**: Testing between vanilla JS and minimal Svelte
- **Backend**: FastAPI + SQLModel + SQLite

## Project Structure

```
/src             # MVP application (FastAPI + SvelteKit)
/prototype       # Rapid discovery phase
/old            # Archived over-engineered attempt
/docs           # Learnings and documentation
/.claude        # Development commands
```

## Code Quality

Pre-commit hooks enforce:
- **Python**: ruff (lint + format, line-length 88, complexity 10)
- **Frontend**: prettier + svelte-check

Run at end of each implementation phase:
```bash
pre-commit run --all-files
```

## After Discovery

Once domain model is understood (1-2 weeks of prototype), rebuild with:
- Simple architecture (no event sourcing)
- Just enough structure for maintainability
- Focus on features that sparked joy during discovery