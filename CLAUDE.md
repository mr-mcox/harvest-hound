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

## Running the Application

**For USER (authentic use with real data):**
```bash
./run                    # Uses harvest.db (your real kitchen inventory)
./run --fork experiment  # Creates and uses experiment.db for testing scenarios
./run --db dev.db        # Use safe dev.db for testing
```

This runs both frontend (http://localhost:5173) and backend (http://localhost:8000) together.

**For Claude Code (development/testing):**
```bash
cd src/backend && uv run uvicorn app:app --reload
```

This defaults to `dev.db` and **cannot touch the user's real data**. Claude should NEVER run `./run` as it uses `harvest.db` by default.

### Database Safety

- `dev.db` - Safe default for Claude Code and testing
- `harvest.db` - Live production data (real kitchen inventory)
- `experiment.db` or `fork-*.db` - Copies for testing scenarios

The separation exists because Claude Code once wiped live data during investigation. The `./run` script is **exclusively for user operation**.

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