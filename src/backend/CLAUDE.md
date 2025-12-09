# Backend

## Environment Variables

- `ANTHROPIC_HH_API_KEY` - Required for BAML/LLM features
- `DATABASE_URL` - Override database (default: `sqlite:///dev.db`)

## Database Migrations

**Development (dev.db):**
```bash
cd src/backend
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```

**Production (harvest.db) - ⚠️ CAUTION:**
```bash
cd src/backend
# Backup first!
DATABASE_URL=sqlite:///harvest.db uv run alembic upgrade head
```

## Development

From project root: `./dev`
