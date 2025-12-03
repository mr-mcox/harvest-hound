
date: 2025-12-03
feature: mvp-scaffolding
status: draft
frame: .scratch/frame-mvp-scaffolding.md
estimated_effort: M
confidence: High
tags: [scaffolding, infrastructure, svelte, fastapi, baml]
---

# TIP: MVP Scaffolding

## Context

### Problem Statement

Before building any steel thread features, we need a runnable project structure that supports the MVP stack (FastAPI + Svelte + Skeleton v4 + BAML) with a single entrypoint. The prototype proved the domain model; now we need a foundation that's evolvable without being over-architected.

### User Stories

**Essential:**
1. **Single command to run the app** - `./dev` starts backend + frontend with hot reload
2. **Hello world proves the stack** - Minimal app touches each layer (Svelte → FastAPI → SQLite → BAML)
3. **Obvious project structure** - Clear locations for backend, frontend, and BAML code

### Acceptance Criteria (TDD Seeds)

- [ ] Running `./dev` starts both backend and frontend
- [ ] Backend serves the frontend in production mode
- [ ] Hot reload works for both Python and Svelte changes
- [ ] App accessible at `http://localhost:8000`
- [ ] Svelte frontend renders with Skeleton v4 styling
- [ ] Frontend can call a FastAPI endpoint
- [ ] Backend can query SQLite (even just "SELECT 1")
- [ ] BAML configured and callable (fun: "name three dishes that use X")
- [ ] SSE streaming works from backend to frontend

### Scope Boundaries

**In Scope:**
- Project directory structure at `src/`
- Dev script with `concurrently`
- Hello world endpoints and UI
- BAML client configuration
- Vite + SvelteKit setup with Skeleton v4

**Out of Scope:**
- Any domain models (Recipe, Store, InventoryItem)
- Real UI beyond proving Skeleton renders
- Tests (deferred per charter)
- Database migrations
- Production deployment

### Prototype Patterns to Preserve

- FastAPI + SQLModel + SQLite stack
- BAML integration pattern (`from baml_client import b`)
- SSE streaming with `StreamingResponse`
- Static file serving (backend serves frontend build)
- CORS middleware configuration

### Key Learnings Informing This Feature

- Single-page prototype goes surprisingly far
- Zero-click workflows validated - minimize friction
- SSE streaming value confirmed for recipe generation UX

---

## Implementation Phases

### Phase 1: Backend Foundation

**Purpose**: Establish FastAPI backend structure with SQLite connectivity. This comes first because the frontend will need API endpoints to call.

**Scope**:
- Create `src/backend/` directory structure
- `app.py` - FastAPI entrypoint with CORS, static mounting
- `models.py` - Empty SQLModel setup with engine, "SELECT 1" health check
- `routes.py` - Hello world endpoint (`/api/hello`)

**TDD Focus**:
- Acceptance: Backend can query SQLite
- Test approach: Manual verification (GET /api/hello returns JSON)

**Key Considerations**:
- Use same SQLite/SQLModel pattern as prototype
- Keep CORS permissive for development
- Mount `/static` for future frontend build output

**Dependencies**: None

**Complexity**: S

---

### Phase 2: BAML Integration

**Purpose**: Configure BAML with a fun "dish namer" function. This validates LLM integration before frontend exists.

**Scope**:
- Create `src/backend/baml_src/` directory
- `clients.baml` - Anthropic client configuration
- `generators.baml` - BAML generator config for Python
- `dishes.baml` - Fun function: "Name three dishes that use ingredient X"
- `baml_functions.py` - Thin wrapper exposing BAML to routes

**TDD Focus**:
- Acceptance: BAML configured and callable
- Test approach: Manual curl to endpoint that calls BAML

**Key Considerations**:
- Copy client config pattern from prototype
- Use environment variable for API key (`ANTHROPIC_HH_API_KEY`)
- Keep the BAML function playful but real (actual LLM call)

**Dependencies**: Phase 1 (needs FastAPI routes to expose)

**Complexity**: S

---

### Phase 3: Frontend Scaffolding

**Purpose**: Set up SvelteKit + Skeleton v4 + Tailwind 4 with minimal hello world. This is the largest phase due to tooling setup.

**Scope**:
- Create `src/frontend/` with SvelteKit project
- Install Skeleton v4 (`@skeletonlabs/skeleton`, `@skeletonlabs/skeleton-svelte`)
- Configure Tailwind 4 integration
- Create minimal `+page.svelte` with Skeleton button component
- Configure Vite to proxy API calls to FastAPI backend

**TDD Focus**:
- Acceptance: Svelte frontend renders with Skeleton v4 styling
- Test approach: Visual verification in browser

**Key Considerations**:
- Skeleton v4 requires Tailwind 4 (different from v2/v3)
- Use Cerberus theme (default, can change later)
- Vite proxy config for `/api/*` to avoid CORS in dev

**Dependencies**: Phase 1 (needs backend for proxy target)

**Complexity**: M

---

### Phase 4: Frontend-Backend Integration

**Purpose**: Prove the full stack by having frontend call backend API and display result.

**Scope**:
- Add fetch call to `/api/hello` from Svelte
- Display response in UI with Skeleton styling
- Add BAML endpoint to routes (`/api/dishes?ingredient=X`)
- Wire frontend to call dish namer and display results

**TDD Focus**:
- Acceptance: Frontend can call a FastAPI endpoint
- Test approach: Manual - click button, see dishes appear

**Key Considerations**:
- Keep it simple - no complex state management yet
- Prove the round-trip works before adding complexity

**Dependencies**: Phase 2, Phase 3

**Complexity**: S

---

### Phase 5: SSE Streaming Proof

**Purpose**: Validate that SSE streaming pattern from prototype works with new stack.

**Scope**:
- Add streaming endpoint (`/api/dishes/stream?ingredient=X`)
- Modify BAML function to return dishes one at a time
- Add EventSource handling in Svelte
- Display dishes as they stream in

**TDD Focus**:
- Acceptance: SSE streaming works from backend to frontend
- Test approach: Visual - see dishes appear one by one

**Key Considerations**:
- Reuse `StreamingResponse` pattern from prototype
- EventSource API in browser for SSE consumption
- This validates the core UX pattern for recipe generation

**Dependencies**: Phase 4

**Complexity**: S

---

### Phase 6: Dev Script & Production Build

**Purpose**: Single `./dev` command and production build configuration.

**Scope**:
- Create `./dev` script using `concurrently`
- Configure Vite build output to `src/backend/static/`
- Ensure FastAPI serves built frontend at `/`
- Document usage in README or CLAUDE.md

**TDD Focus**:
- Acceptance: `./dev` starts both backend and frontend with hot reload
- Acceptance: Backend serves frontend in production mode
- Test approach: Run `./dev`, make changes, see hot reload

**Key Considerations**:
- `concurrently` shows both outputs with color coding
- Vite build must output to location FastAPI mounts
- Production: single uvicorn serves everything

**Dependencies**: Phase 3, Phase 4

**Complexity**: S

---

## Sequencing Logic

**Why this order:**
1. **Backend first** - Frontend needs something to talk to; easier to test API in isolation
2. **BAML early** - Validates LLM integration independently, fun to play with
3. **Frontend third** - Largest setup, benefits from having real endpoints to call
4. **Integration fourth** - Quick win after frontend setup, proves the stack
5. **SSE fifth** - Key UX pattern, but requires working integration first
6. **Dev script last** - Ties everything together, needs all pieces working

**Parallel work possible:**
- Phase 2 (BAML) and Phase 3 (Frontend) could run in parallel after Phase 1
- But sequential is fine for single developer

**Dependencies constrain:**
- Frontend integration (4) requires both backend routes (1) and BAML (2)
- SSE (5) requires working integration (4)
- Dev script (6) requires both backend and frontend functional

---

## High-Level Test Strategy

**Approach**: Manual verification for scaffolding phase (no automated tests per charter)

**By phase:**
- Phase 1-2: curl/httpie to test endpoints
- Phase 3-4: Browser visual verification
- Phase 5: Browser visual verification (streaming behavior)
- Phase 6: Run `./dev`, verify hot reload

**Key scenarios from acceptance criteria:**
- App starts with single command
- Skeleton button renders with proper styling
- API call returns JSON
- BAML returns actual LLM-generated dishes
- SSE streams data progressively

---

## Integration Points

**Backend:**
- FastAPI app structure (`app.py`, `routes.py`, `models.py`)
- SQLModel engine and session management
- BAML client integration (`baml_functions.py`)
- Static file serving configuration

**Frontend:**
- SvelteKit project structure
- Skeleton v4 + Tailwind 4 CSS configuration
- Vite proxy for development API calls
- Vite build output location

**BAML:**
- Client configuration (Anthropic)
- Generator configuration (Python output)
- At least one function (`NameDishes`)

**Tooling:**
- `concurrently` for parallel process management
- npm/pnpm for frontend dependencies
- uv for Python dependencies

---

## Risk Assessment

### High Risks

**Skeleton v4 + Tailwind 4 setup complexity**
- *Risk*: New version may have undocumented quirks
- *Mitigation*: Follow official docs exactly, have fallback to v2 if blocking
- *Likelihood*: Low (docs look solid)

### Medium Risks

**Vite proxy configuration**
- *Risk*: Proxy config may conflict with SvelteKit routing
- *Mitigation*: Test early, can fall back to CORS if needed

**BAML Python client generation**
- *Risk*: baml-cli generate may have path issues in new structure
- *Mitigation*: Test generation early, copy working config from prototype

### Low Risks

**concurrently installation**
- *Risk*: npm dependency in primarily Python project
- *Mitigation*: Single dev dependency, well-maintained package

### Steering Likelihood

- Phase 3 (Frontend): May need input on Skeleton theme choice
- Phase 6 (Dev script): May need input on preferred package manager (npm vs pnpm)

---

## Implementation Notes

**TDD**: Manual verification throughout (automated tests deferred per charter)

**Prototype patterns to follow:**
- `prototype/app.py:85-97` - FastAPI setup with CORS and static mounting
- `prototype/app.py:418-493` - SSE streaming pattern
- `prototype/baml_src/clients.baml` - BAML client configuration

**Prototype patterns to change:**
- Single `app.py` → modular `models.py`, `routes.py`, `baml_functions.py`
- Vanilla JS → SvelteKit
- `prototype/` location → `src/` at project root

**Quality gates:**
- Each phase should result in runnable state
- Don't proceed to next phase until current phase works

---

## Overall Complexity Estimate

**Overall**: M (Moderate)

**Confidence**: High

**Justification**:
- Most patterns exist in prototype (low novelty)
- Skeleton v4 setup is the main unknown, but well-documented
- Six small phases with clear boundaries
- Single developer, no coordination overhead
- Steering unlikely beyond theme/tooling preferences
