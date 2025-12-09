# Frontend

## Package Manager

**Use `pnpm` only.** Never npm or yarn.

```bash
pnpm install        # Install dependencies
pnpm add <package>  # Add package
pnpm test           # Run tests
```

## Svelte 5

Use **runes** (`$state`, `$derived`, `$effect`), not legacy `$:` reactive statements.

## Development

From project root: `./dev` (runs both backend + frontend)

## Pre-commit

Run from **project root**, not from frontend/:

```bash
cd /Users/mcox/dev/harvest-hound  # Or just: cd ../..
pre-commit run --all-files
```
