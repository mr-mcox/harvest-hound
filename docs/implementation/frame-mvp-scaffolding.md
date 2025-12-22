# Feature Frame: MVP Scaffolding

**Date**: 2025-12-02
**Status**: Aligned

---

## Problem Statement

Before building any steel thread features, we need a runnable project structure that supports the MVP stack (FastAPI + Svelte + Skeleton v3 + BAML) with a single entrypoint. The prototype proved the domain model; now we need a foundation that's evolvable without being over-architected.

**From Prototype Discovery**:
- Single-page prototype goes surprisingly far
- FastAPI + SQLModel + SQLite works well
- BAML integration is straightforward
- Vanilla JS is showing friction (charter notes move to Svelte)

---

## User Stories

### Story 1: Single command to run the app
**As a** developer
**I want** one command to start the entire application
**So that** I can begin working without setup friction

**Acceptance Criteria**:
- [ ] Running `./dev` (or similar) starts both backend and frontend
- [ ] Backend serves the frontend (no separate servers in production)
- [ ] Hot reload works for both Python and Svelte changes in development
- [ ] App is accessible at `http://localhost:8000`

**From LEARNINGS.md**: Zero-click workflows validated - minimize friction

### Story 2: Hello world proves the stack
**As a** developer
**I want** a minimal working app that touches each layer
**So that** I know the integration works before building features

**Acceptance Criteria**:
- [ ] Svelte frontend renders with Skeleton v3 styling
- [ ] Frontend can call a FastAPI endpoint
- [ ] Backend can query SQLite (even just "SELECT 1")
- [ ] BAML is configured and can be called (even just echo)
- [ ] SSE streaming works from backend to frontend

**From MVP-CHARTER.md**: Stack is FastAPI + SQLModel + SQLite, BAML, Svelte + Skeleton v3

### Story 3: Obvious project structure
**As a** developer
**I want** a clear, simple directory layout
**So that** I know where to add code as features grow

**Acceptance Criteria**:
- [ ] Backend code in predictable location
- [ ] Frontend code in predictable location
- [ ] Shared types/contracts have a home
- [ ] Structure supports MVP Charter's split: `models.py`, `routes.py`, `baml_functions.py`

**From MVP-CHARTER.md**: Change from single `app.py` to modular structure

---

## Prototype Contrast

| Aspect | Prototype | MVP | Why Change |
|--------|-----------|-----|------------|
| Frontend | Vanilla JS + static HTML | Svelte + Skeleton v3 | Charter decision - better state management |
| Backend structure | Single `app.py` (~700 LoC) | `models.py`, `routes.py`, `baml_functions.py` | Evolvability without 700 LoC blast radius |
| Location | `prototype/` subdirectory | `src/` at project root | Fresh start, cleaner structure |
| Server setup | `cd prototype && uv run uvicorn` | Single `./dev` script | Reduce friction |

**Preserve from Prototype**:
- FastAPI + SQLModel + SQLite (works great)
- BAML integration pattern
- SSE streaming approach
- Static file serving pattern (backend serves frontend)

**Fix from Prototype**:
- Vanilla JS → Svelte (state management)
- Monolithic file → modular structure

**Change from Prototype**:
- New location at project root
- Proper Vite build for frontend
- Single dev script entrypoint

---

## Out of Scope (Deferred)

Explicitly NOT part of this scaffolding:

- **Any domain models**: No Recipe, Store, InventoryItem - just hello world
- **Any real UI**: Just enough to prove Skeleton renders
- **Tests**: Deferred - "me running is a test"
- **Database migrations**: Blow away DB during development (per charter)
- **Production deployment**: Dev-only for now

**Future Features This Enables**:
- Steel thread: Inventory entry
- Steel thread: Recipe generation
- All MVP features

---

## Technical Decisions (Confirmed)

1. **Directory structure**: `src/` at project root
   ```
   src/
   ├── backend/
   │   ├── app.py          # FastAPI entrypoint
   │   ├── models.py       # SQLModel models
   │   ├── routes.py       # API routes
   │   └── baml_functions.py
   ├── frontend/
   │   ├── src/
   │   │   └── App.svelte
   │   ├── package.json
   │   └── vite.config.js
   └── dev                  # Single entrypoint script
   ```

2. **Dev script**: Shell script (`./dev`) that runs uvicorn + vite in parallel

3. **Production build**: Vite builds to `src/backend/static/`, FastAPI serves it

4. **Backend naming**: Standard/obvious names (app.py, models.py, routes.py)
