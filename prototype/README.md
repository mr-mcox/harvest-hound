# Harvest Hound Prototype

## Quick Start

```bash
# Install dependencies (creates venv automatically)
uv sync

# Run the app
uv run uvicorn app:app --reload

# Open browser to http://localhost:8000
```

## What This Is

A throwaway prototype to discover:
- The supple domain model
- Real vs imagined complexity
- Natural workflows
- What features spark joy

## What This Isn't

- Production code
- Well-architected
- Tested
- Something to maintain

## Key Files

- `app.py` - Everything in one file (for now)
- `static/index.html` - Simple UI
- `static/app.js` - Frontend logic
- `baml_project/` - BAML prompts (from old system)

## Discovery Goals

1. Test SSE streaming for recipes - is it worth it?
2. Figure out ingredient claiming - complex or simple?
3. Find natural meal planning workflow
4. Determine if stores need polymorphism
5. Test BAML prompts with real scenarios

## Next Steps

After 1-2 weeks of exploration:
1. Document learnings in docs/LEARNINGS.md
2. Identify 5-7 core use cases
3. Save working BAML prompts
4. Throw away this code
5. Build clean MVP with discoveries