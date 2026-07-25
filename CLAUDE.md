# Harvest Hound

Agentic meal planning for CSA deliveries.

## Critical: Database Safety

- `harvest.db` = **LIVE USER DATA** - Never modify directly
- `dev.db` = Safe for testing (default)
- **Never run `./run` during development** (uses harvest.db by default)

## Development

```bash
./dev              # SAFE: Uses dev.db, runs backend + frontend
./run              # DANGER: User only, uses harvest.db
./run --db dev.db  # Override to use safe database
```

## Project Structure

- `/src` - Current MVP (see `src/backend/CLAUDE.md` and `src/frontend/CLAUDE.md`)
- `/prototype` - Discovery phase (reference only)
- `/old` - Archived over-engineered attempt

## Orientation

- `docs/README.md` - Documentation map and workflow
- `docs/PROJECT.md` - Standing constraints, stack, architectural principles
- `docs/roadmap/PRIORITIES.md` - Current focus; `docs/roadmap/phase-*.md` - phase strategy and tensions

## Code Quality

Run before completing work:
```bash
pre-commit run --all-files
```
