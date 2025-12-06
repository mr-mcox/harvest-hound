# Implement Tasks Command

Implement features from the TIP at: $ARGUMENTS

**Development Model**: Spec-based development where you (Claude) write code with human oversight. The TIP provides strategic direction; you make tactical decisions just-in-time with user approval at phase boundaries.

**Core Principles**:
1. Strategic alignment comes from the TIP (phases, sequencing, risks)
2. Tactical decisions happen at the start of each phase (files, tests, sequence)
3. TDD intensity matches the work: thorough for domain, basic for frontend/integration, none for scaffolding
4. Plans are guides - adapt when reality requires, communicate changes

---

## Implementation Loop

For each TIP phase:

```
1. PLAN PHASE    → Identify work items, test intensity, files
2. USER APPROVAL → Present plan, wait for OK
3. EXECUTE       → Implement with category-appropriate workflow
4. CHECKPOINT    → Verify, update TIP, pause for feedback
```

---

## Step 1: Find Next Phase

Read the TIP and identify the next incomplete phase. Phases should be marked as you complete them:

```markdown
### Phase 1: Database Models ✓
### Phase 2: Config APIs ← current
### Phase 3: Settings UI
```

If resuming, check which phase is current.

---

## Step 2: Phase Planning (Just-in-Time Tactical Decisions)

Before implementing, analyze the phase and create a lightweight plan.

### 2.1 Read Phase Scope

From the TIP, extract:
- What this phase accomplishes
- Key considerations mentioned
- Dependencies satisfied

### 2.2 Explore Code Context

Use Glob/Grep/Read to find:
- Exact files to modify or create
- Existing patterns to follow
- Current state of relevant code

### 2.3 Determine Test Intensity

For each work item, apply the Test Intensity Framework (see below) to decide:
- **No tests** (SETUP scaffolding)
- **Basic tests** (frontend, integration, config CRUD)
- **Thorough tests** (domain logic, business rules)

### 2.4 Identify Work Sequence

Break the phase into work items:
- What order minimizes friction?
- Which items are SETUP vs NEW BEHAVIOR vs REFACTOR?
- What test intensity for each?

### 2.5 Present Phase Plan

Output a concise plan for user approval:

```markdown
## Phase N: [Name]

**TIP scope**: [1-2 sentence summary from TIP]

**Work sequence**:
1. [SETUP] Create X scaffolding in file.py
2. [NEW BEHAVIOR - thorough] Implement Y with domain tests
3. [NEW BEHAVIOR - basic] Wire up Z endpoint
4. [REFACTOR] Clean up existing W code

**Test intensity rationale**: [Why thorough/basic/none for key items]

**Files**: [List of files to touch]

Proceed with Phase N?
```

**Keep it under 15 lines.** This is a checkpoint, not a detailed spec.

### 2.6 Wait for User Approval

User may:
- Approve as-is → proceed
- Adjust test intensity → update and proceed
- Request changes → revise plan
- Ask questions → clarify and re-present

---

## Step 3: Execute Phase

After approval, implement using TodoWrite to track progress.

### 3.1 Create Todo List

Add work items from phase plan to TodoWrite:

```
- [ ] Create X scaffolding
- [ ] Implement Y with tests
- [ ] Wire up Z endpoint
```

### 3.2 Execute Each Work Item

Use the appropriate workflow based on category:

- **SETUP ONLY** → Scaffolding workflow (no tests)
- **NEW BEHAVIOR** → TDD workflow (intensity per plan)
- **REFACTOR** → Behavior-preserving workflow

Mark items complete in TodoWrite as you finish.

### 3.3 After Each Work Item

- Run relevant tests
- Run pre-commit
- Fix any issues before proceeding

---

## Step 4: Phase Checkpoint

After completing all work items in the phase:

1. **Verify phase is complete**:
   - All tests passing
   - Pre-commit clean
   - Phase goals met

2. **Update TIP**:
   - Mark phase complete with ✓
   - Note any deviations or discoveries

3. **Pause for user feedback**:
   ```
   Phase N complete.

   **Implemented**: [brief summary]
   **Tests**: [X passing]
   **Deviations**: [any changes from plan, or "none"]

   Ready for Phase N+1, or would you like to review?
   ```

4. **Proceed or address feedback** before next phase

---

## Test Intensity Framework

Use these signals to decide test depth for each work item.

### No Tests (SETUP ONLY)

**Signals**:
- Creating empty classes, interfaces, schemas
- File/directory structure
- Stubs with `NotImplementedError`
- Import-enabling code
- No decisions or logic

**The question**: "Does this code make decisions, or just enable other code to exist?"
→ If just enabling, no tests needed.

### Basic Tests (Light TDD)

**Signals**:
- Frontend components (renders, responds to interaction)
- API endpoint wiring (calls service, returns response)
- Configuration CRUD (save/load without complex rules)
- Integration glue between systems
- SSE/streaming plumbing

**What to test**:
- Happy path works
- Basic error handling
- One or two key interactions

**What NOT to test**:
- Every edge case
- Boundary conditions
- Complex scenarios

**TDD rhythm**: RED (1-2 tests) → GREEN → light REFACTOR

### Thorough Tests (Full TDD)

**Signals**:
- Domain models with invariants
- Business rules and logic
- Calculations, transformations, validations
- State management with rules
- Anything in domain/core layer
- "Smart" behavior (optimization, generation, planning)

**What to test**:
- Happy paths
- Edge cases and boundaries
- Invalid inputs and error conditions
- State transitions
- Invariant preservation

**TDD rhythm**: RED (comprehensive cases) → GREEN → REFACTOR (extract abstractions)

### Project-Specific Guidance (Harvest Hound)

| Area | Test Intensity | Rationale |
|------|---------------|-----------|
| Recipe generation/optimization | Thorough | Core domain logic |
| Inventory calculations | Thorough | Business rules |
| Meal planning constraints | Thorough | Domain invariants |
| Settings/config CRUD | Basic | Thin logic, mostly plumbing |
| UI components | Basic | Render and interaction |
| API endpoint wiring | Basic | Integration glue |
| Model definitions | None | Pure structure |
| Route scaffolding | None | Stubs only |

**When unsure**, ask: "If this has a bug, is it a minor inconvenience or a fundamental problem?" Fundamental → thorough. Inconvenience → basic.

---

## Category Workflows

### SETUP ONLY Workflow

**Purpose**: Create scaffolding that enables other code

**Process**:
1. Create minimal structure (classes, files, stubs)
2. For methods: `raise NotImplementedError("TODO")`
3. For schemas: Field definitions only
4. Run pre-commit
5. Verify imports work

**No tests. No logic. Just structure.**

**Red flag**: If you're writing business rules, stop and recategorize as NEW BEHAVIOR.

---

### NEW BEHAVIOR Workflow

**Purpose**: Implement functionality through TDD

#### For Basic Tests:

**RED**: Write 1-2 focused tests
- Happy path
- One error/edge case
- Keep tests simple and obvious

**GREEN**: Make tests pass
- Direct, simple implementation
- Don't over-engineer

**REFACTOR** (optional): Quick cleanup only
- Extract if obviously cleaner
- Don't gold-plate

#### For Thorough Tests:

**RED**: Write comprehensive tests
- Start with happy path
- Add edge cases
- Add invalid input handling
- Consider boundary conditions
- Think about invariants

**GREEN**: Make tests pass
- Focus on correctness
- Let tests guide design
- Okay to be ugly initially

**REFACTOR**: Clean up properly
- Remove duplication
- Extract meaningful abstractions
- Improve naming
- Keep tests green throughout

---

### REFACTOR Workflow

**Purpose**: Improve code while preserving behavior

**Process**:
1. Confirm existing tests are green (baseline)
2. Make small improvement
3. Run tests - must stay green
4. Run pre-commit
5. If tests fail, revert and try smaller change
6. Repeat

**Safe patterns**:
- Extract method/function
- Rename for clarity
- Move between modules (same interface)
- Performance optimization (same outputs)

**If behavior must change**: Stop. This is NEW BEHAVIOR, not REFACTOR.

---

## When Reality Diverges from Plan

### Phase is Larger Than Expected

If phase planning reveals >6 work items:
1. Explain the scope
2. Propose splitting into sub-phases
3. Wait for user decision

### Work Item Needs Different Test Intensity

If during implementation you realize:
- "This SETUP actually has logic" → promote to NEW BEHAVIOR
- "This basic test revealed complex edge cases" → promote to thorough
- "This thorough testing is overkill for simple CRUD" → can demote, but ask first

### Discovery Requires New Work

1. Explain what's needed and why
2. Propose where it fits in sequence
3. Wait for user approval
4. Add to current phase or create new phase

### Better Approach Found

1. Explain the improvement
2. Impact on remaining work
3. Wait for user confirmation
4. Proceed with improved approach

### Blocked

1. Explain the blocker clearly
2. Propose 2-3 alternatives
3. Wait for user decision

---

## Quality Gates

### Per Work Item:
- [ ] Appropriate workflow followed
- [ ] Tests written and passing (if applicable)
- [ ] Pre-commit passing
- [ ] TodoWrite updated

### Per Phase:
- [ ] All work items complete
- [ ] All tests passing
- [ ] TIP updated with ✓
- [ ] User checkpoint completed

---

## Implementation Complete

When all phases are done:

### Final Verification

```bash
cd src/backend && uv run pytest  # All tests pass
cd src/frontend && npm run build  # Frontend builds
pre-commit run --all-files  # Code quality
```

### Prompt for Cleanup

```
All phases complete!

**Summary**:
- Phases implemented: [N]
- Tests: [X passing]
- Key deliverables: [list]

**Ready to clean up scaffolding**:
- TIP: `[path]`
- Design decision: `[path if exists]`

The code is now the source of truth. Delete scaffolding files?
```

### After User Confirms

- Delete TIP file
- Delete design decision file (if exists)
- Confirm: "Scaffolding cleaned up. Implementation complete!"

---

## Important Principles

### TDD Keeps Code Focused

Writing tests first clarifies *what behavior we need*. This prevents scope creep, over-engineering, and "just in case" features. Let tests drive the implementation - no more, no less.

### Test Intensity Matches Stakes

Domain logic with bugs = broken app. Spend the testing effort there.
Config CRUD with bugs = minor annoyance. Basic tests suffice.
Scaffolding with bugs = won't compile. No tests needed.

### Just-in-Time > Just-in-Case

Tactical decisions (which files, which tests) are better made with current context than planned in advance. The TIP provides direction; you provide the navigation.

### Communicate Adaptations

When you deviate from the plan:
- Explain why
- Propose the change
- Wait for significant changes
- Note in TIP what changed

### Maintain Quality Throughout

- **NEVER** skip tests for NEW BEHAVIOR
- **NEVER** break existing tests during REFACTOR
- **ALWAYS** run pre-commit before marking complete
- **ALWAYS** pause at phase boundaries

---

## Remember

**The TIP is your strategic guide. You make tactical decisions.**

- Read the phase, understand its purpose
- Plan the work just before doing it
- Match test intensity to the stakes
- Execute with discipline (TDD, pre-commit)
- Checkpoint with the user
- Adapt when reality requires
- Communicate changes clearly

Good implementation balances planned direction with adaptive intelligence.
