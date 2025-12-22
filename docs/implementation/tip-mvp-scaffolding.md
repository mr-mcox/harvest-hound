
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

---

## Implementation Tasks

**TIP Reference**: Phases 1-6 above
**Task Sequencing**: Tasks follow TIP phase order. Each task should result in runnable/testable state.

---

## Task 1: Backend Foundation (TIP Phase 1)
**Goal**: FastAPI backend with SQLite connectivity and hello world endpoint
**Verification**: `curl http://localhost:8000/api/hello` returns JSON

### 1.1 Directory Structure - **SETUP ONLY**
- [x] Create `src/backend/` directory
- [x] Create `src/backend/static/` directory (empty, for future frontend build)
- [x] Create `src/backend/__init__.py` (empty)

### 1.2 SQLModel Setup - **SETUP ONLY**
- [x] Create `src/backend/models.py` with:
  - SQLite engine: `sqlite:///harvest.db`
  - `get_session()` dependency for FastAPI
  - Health check function: `def db_health() -> bool` that runs `SELECT 1`

### 1.3 FastAPI App - **SETUP ONLY**
- [x] Create `src/backend/app.py` with:
  - FastAPI app instance
  - CORS middleware (permissive: `allow_origins=["*"]`)
  - Static files mount at `/static` pointing to `static/` directory
  - Import and include router from `routes.py`
- [x] Reference pattern: `prototype/app.py:85-97`

### 1.4 Hello World Route - **NEW BEHAVIOR**
- [x] Create `src/backend/routes.py` with:
  - APIRouter instance
  - `GET /api/hello` endpoint returning `{"message": "Hello from Harvest Hound!", "db_ok": true}`
  - Call `db_health()` to verify SQLite works
- [x] Create `src/backend/pyproject.toml` with dependencies: fastapi, uvicorn, sqlmodel

### 1.5 Verification Checkpoint
- [x] Run: `cd src/backend && uv sync && uv run uvicorn app:app --reload`
- [x] Verify: `curl http://localhost:8000/api/hello` returns JSON with `db_ok: true`

---

## Task 2: BAML Integration (TIP Phase 2)
**Goal**: Working BAML function that names dishes using an ingredient
**Verification**: `curl "http://localhost:8000/api/dishes?ingredient=potato"` returns LLM-generated dishes

### 2.1 BAML Directory - **SETUP ONLY**
- [x] Create `src/backend/baml_src/` directory

### 2.2 BAML Client Config - **SETUP ONLY**
- [x] Create `src/backend/baml_src/clients.baml` with Anthropic client
  - Model: `claude-sonnet-4-5`
  - API key: `env.ANTHROPIC_HH_API_KEY`
- [x] Reference pattern: `prototype/baml_src/clients.baml`

### 2.3 BAML Generator Config - **SETUP ONLY**
- [x] Create `src/backend/baml_src/generators.baml` with Python output config
  - Output directory: `../` (generates `baml_client/` at backend root)

### 2.4 Dish Namer Function - **NEW BEHAVIOR**
- [x] Create `src/backend/baml_src/dishes.baml` with:
  - `class Dish { name: string, description: string }`
  - `function NameDishes(ingredient: string) -> Dish[]`
  - Prompt: "Name three creative dishes that feature {ingredient} as a key ingredient"
- [x] Run `uv run baml-cli generate` to create Python client

### 2.5 BAML Wrapper - **SETUP ONLY**
- [x] Create `src/backend/baml_functions.py` with:
  - `async def get_dishes(ingredient: str) -> list[Dish]`
  - Calls BAML client and returns dishes

### 2.6 Dishes Endpoint - **NEW BEHAVIOR**
- [x] Add to `src/backend/routes.py`:
  - `GET /api/dishes?ingredient=X` endpoint
  - Calls `get_dishes()` and returns JSON array
- [x] Add `baml-py` to `pyproject.toml` dependencies

### 2.7 Verification Checkpoint
- [x] Verify: BAML imports work, endpoint returns appropriate error when API key not set
- Note: Full LLM verification requires `ANTHROPIC_HH_API_KEY` environment variable

---

## Task 3: Frontend Scaffolding (TIP Phase 3)
**Goal**: SvelteKit + Skeleton v4 rendering with styled button
**Verification**: Browser shows Skeleton-styled page at `http://localhost:5173`

### 3.1 SvelteKit Project - **SETUP ONLY**
- [x] Run: `cd src && npx sv create --types ts frontend`
  - Select: SvelteKit minimal, TypeScript
- [x] Verify: `cd src/frontend && npm install && npm run dev` shows default page

### 3.2 Skeleton v4 Installation - **SETUP ONLY**
- [x] Run: `cd src/frontend && npm i -D @skeletonlabs/skeleton @skeletonlabs/skeleton-svelte`
- [x] Install Tailwind 4 if not present: `npm i -D tailwindcss`

### 3.3 Tailwind + Skeleton CSS Config - **SETUP ONLY**
- [x] Update `src/frontend/src/app.css`:
  ```css
  @import 'tailwindcss';
  @import '@skeletonlabs/skeleton';
  @import '@skeletonlabs/skeleton-svelte';
  @import '@skeletonlabs/skeleton/themes/cerberus';
  ```
- [x] Ensure `app.css` is imported in `+layout.svelte`

### 3.4 Hello World Page - **NEW BEHAVIOR**
- [x] Update `src/frontend/src/routes/+page.svelte`:
  - Add Skeleton button component
  - Display "Harvest Hound" heading with Skeleton typography
  - Simple layout proving Skeleton styling works

### 3.5 Vite Proxy Config - **SETUP ONLY**
- [x] Update `src/frontend/vite.config.ts`:
  - Add proxy for `/api/*` to `http://localhost:8000`
  - This avoids CORS issues in development

### 3.6 Verification Checkpoint
- [x] Run frontend: `cd src/frontend && npm run dev`
- [x] Verify: Browser shows Skeleton-styled button at `http://localhost:5173`

---

## Task 4: Frontend-Backend Integration (TIP Phase 4)
**Goal**: Frontend calls backend API and displays result
**Verification**: Click button, see dishes appear in UI

### 4.1 API Fetch in Svelte - **NEW BEHAVIOR**
- [x] Update `src/frontend/src/routes/+page.svelte`:
  - Add text input for ingredient
  - Add "Get Dishes" button
  - On click: fetch `/api/dishes?ingredient=X`
  - Display returned dishes in a Skeleton-styled list/cards

### 4.2 Loading State - **NEW BEHAVIOR**
- [x] Add loading indicator while fetching
- [x] Display error message if API call fails

### 4.3 Verification Checkpoint
- [x] Run backend: `cd src/backend && uv run uvicorn app:app --reload`
- [x] Run frontend: `cd src/frontend && npm run dev`
- [x] Verify: Enter "carrot", click button, see 3 dishes appear

---

## Task 5: SSE Streaming Proof (TIP Phase 5)
**Goal**: Dishes stream in one at a time
**Verification**: See dishes appear progressively (not all at once)

### 5.1 Streaming Endpoint - **NEW BEHAVIOR**
- [x] Add to `src/backend/routes.py`:
  - `GET /api/dishes/stream?ingredient=X` endpoint
  - Returns `StreamingResponse` with `text/event-stream` media type
- [x] Reference pattern: `prototype/app.py:418-493`

### 5.2 BAML Streaming Function - **NEW BEHAVIOR**
- [x] Update `src/backend/baml_functions.py`:
  - Add `async def stream_dishes(ingredient: str)` generator
  - Yields dishes one at a time as SSE events
- [x] Format: `data: {"name": "...", "description": "..."}\n\n`

### 5.3 EventSource in Svelte - **NEW BEHAVIOR**
- [x] Update `src/frontend/src/routes/+page.svelte`:
  - Add "Stream Dishes" button
  - Use `EventSource` API to connect to `/api/dishes/stream`
  - Append each dish to list as it arrives
  - Close connection on completion event

### 5.4 Verification Checkpoint
- [x] Verify: Click "Stream Dishes", see dishes appear one by one with visible delay

---

## Task 6: Dev Script & Build (TIP Phase 6)
**Goal**: Single `./dev` command, plus built frontend served by uvicorn
**Verification**: `./dev` starts everything, hot reload works

### 6.1 Vite Build Config - **SETUP ONLY**
- [x] Update `src/frontend/svelte.config.js`:
  - Set adapter-static output to `../backend/static`
  - Note: SvelteKit uses adapter config, not vite.config.ts for build output

### 6.2 Dev Script - **SETUP ONLY**
- [x] Create `src/dev` (executable shell script):
  ```bash
  #!/bin/bash
  npx concurrently \
    --names "api,web" \
    --prefix-colors "cyan,magenta" \
    "cd backend && uv run uvicorn app:app --reload" \
    "cd frontend && npm run dev"
  ```
- [x] Run: `chmod +x src/dev`

### 6.3 Root Index Route - **SETUP ONLY**
- [x] Update `src/backend/app.py`:
  - Add route for `/` that serves `static/index.html` (built frontend)
  - Mount static files with `html=True` for SPA fallback

### 6.4 Build and Run Mode - **NEW BEHAVIOR**
- [x] Test build: `cd src/frontend && npm run build`
- [x] Verify files appear in `src/backend/static/`
- [x] Test run mode: `cd src/backend && uv run uvicorn app:app`
- [x] Verify: `http://localhost:8000` serves built frontend

### 6.5 Documentation - **SETUP ONLY**
- [x] Update `src/CLAUDE.md` (create if needed):
  - Development: `./dev`
  - Build: `cd frontend && npm run build`
  - Run: `cd backend && uv run uvicorn app:app`

### 6.6 Verification Checkpoint
- [x] Run `./dev` from `src/` directory
- [x] Verify: Both outputs visible with colors
- [x] Verify: Backend hot reload configured (uvicorn --reload)
- [x] Verify: Frontend hot reload configured (vite dev)

---

## Success Criteria for Implementation

- [x] All tasks completed and marked as done
- [x] Manual verification passed for each checkpoint
- [x] Integration points validated:
  - [x] Vite proxy works (frontend → backend)
  - [x] BAML client generates correctly
  - [x] Static files serve from backend
- [x] Risk mitigations confirmed:
  - [x] Skeleton v4 renders properly
  - [x] SSE streaming works end-to-end

**Implementation Note**: Tasks may be reordered, skipped, or added during implementation as reality requires. This task plan is a guide, not a script. Use `implement-tasks` to begin implementation.
