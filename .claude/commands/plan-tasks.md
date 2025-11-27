# Plan Tasks Command

Create detailed task breakdown for: $ARGUMENTS

This command interprets the strategic TIP and adds tactical implementation details. Use this when:
- You have an approved TIP with strategic phases
- You need to translate strategic direction into concrete deliverables
- You're ready to determine specific files, tests, and implementation steps

**Purpose**: Bridge strategic vision to tactical execution. You'll interpret the TIP's phases and add the specific file changes, test cases, and deliverables needed to make it concrete.

---

## Input Requirements

**REQUIRED**: Reference the Technical Implementation Plan (TIP) at: $ARGUMENTS

The TIP provides:
- Strategic phases and sequencing rationale
- Integration points awareness
- Risk mitigation strategies
- High-level test strategy
- Complexity estimates (cognitive load, decision density, steering needs)

You will add:
- Specific file:line changes
- Concrete test cases and names
- Detailed deliverables and checkboxes
- Granular success criteria

---

## Process

### Step 1: Read and Analyze TIP

Read the TIP at `$ARGUMENTS` carefully.

Extract:
- **Phase structure**: What phases exist and why they're sequenced this way
- **Integration points**: What systems/areas are affected
- **Test strategy**: What kinds of testing are needed
- **Constraints**: What architectural decisions or patterns must be followed

### Step 2: Interpret Strategic Direction

For each TIP phase, determine:

**Specific Files to Change**:
- The TIP says "Refactor domain model" - which files specifically?
- The TIP says "Update event sourcing" - which event classes and where?
- Use codebase knowledge and grep/glob to find exact locations

**Concrete Test Cases**:
- The TIP says "Test happy path" - what specific test name and assertions?
- The TIP says "Verify edge cases" - which edge cases specifically?
- Design test names that clearly express behavior

**Detailed Deliverables**:
- Break down high-level scope into specific actionable items
- Each checkbox should be completable in < 30 minutes ideally
- Sequence deliverables to enable incremental progress

### Step 3: Ask Clarifying Questions (If Needed)

If the TIP's strategic direction is unclear or you need decisions:

**File Location Questions**:
- "The TIP mentions updating the API layer - should this be api.py or routers/?
- "Which specific repository method handles event reconstruction?"

**Test Design Questions**:
- "Should we test this at the unit level or integration level?"
- "What specific edge case scenarios are most important?"

**Sequencing Questions**:
- "Can these two tasks run in parallel or must they be sequential?"
- "Should we prioritize SETUP or REFACTOR tasks first here?"

Then WAIT for user responses.

### Step 4: Generate Detailed Task Plan

Create task breakdown following the structure below. This will be **appended to the TIP file** as a new section.

## Task Classification System

Use these three categories to clearly indicate testing approach:

### 🏗️ SETUP ONLY
**Purpose**: Create scaffolding that enables other code to import/reference
**Testing**: No tests needed - minimal logic only
**Implementation**: Stubs, schemas, empty classes with NotImplementedError
**Examples**:
- Create `InventoryItemView` class with fields only
- Add route definitions with `raise NotImplementedError`
- Create database table schemas
- Add empty component files with prop interfaces

### 🧪 NEW BEHAVIOR
**Purpose**: Implement new business logic and user-facing features
**Testing**: Test-driven development - write failing tests first
**Implementation**: RED → GREEN → REFACTOR cycle
**Examples**:
- Parse inventory text with LLM and return structured data
- Create event projection that updates read models
- Implement API endpoint that processes user input
- Add component interaction handling user clicks

### 🔄 REFACTOR
**Purpose**: Improve existing code while maintaining current behavior
**Testing**: Existing tests should continue passing with minimal changes
**Implementation**: Small steps, run tests frequently, preserve behavior
**Examples**:
- Extract method from large function
- Rename fields for clarity
- Move code between modules
- Optimize query performance

## Task Structure

For each TIP phase, create corresponding tasks:

```markdown
---

## Implementation Tasks

**TIP Reference**: Phases 1-N above
**Task Sequencing**: [Explain how tasks map to phases]

---

## Task [N]: [High-Level Feature/Component] (TIP Phase Reference)
**Goal**: [Overall objective from TIP phase]
**TIP Context**: [Which TIP phase(s) this implements]

### [N.1] [Sub-Component Name] - **[SETUP ONLY|NEW BEHAVIOR|REFACTOR]**
- [ ] **[Specific deliverable]** - [Brief description with file:line if relevant]
- [ ] **[Specific deliverable]** - [Brief description]
- [ ] **[Specific deliverable]** - [Brief description]

### [N.2] [Sub-Component Name] - **[SETUP ONLY|NEW BEHAVIOR|REFACTOR]**
- [ ] **[Specific deliverable]** - [Brief description]
- [ ] **[Specific deliverable]** - [Brief description]
```

**Key Principles**:
- **High-level tasks** align with TIP phases
- **Sub-tasks** group related work with clear testing classification
- **Checkboxes** are specific, actionable deliverables (file changes, test cases)
- **Classification** applies to the sub-task level, not individual checkboxes
- **Include file:line references** where helpful for navigation

## Task Sequencing Principles

**From TIP Strategic Direction**:
- Follow the TIP's phase sequence and dependency logic
- Interpret "Refactor domain model" → specific files to change in order
- Interpret "Update events" → specific event classes and test cases
- Make tactical sequencing decisions within strategic constraints

**Testing Flow**:
- SETUP tasks first → enable importing and referencing
- NEW BEHAVIOR tasks next → implement and test core functionality
- REFACTOR tasks last → optimize and clean up

**Incremental Progress**:
- Each task should be completable in < 2 hours ideally
- Break large work into smaller deliverables
- Enable testing and validation at multiple points

## Quality Guidelines

### SETUP ONLY Tasks
- **Be Extremely Specific**: "Create `InventoryItemView` class in `app/models/read_models.py:54` with fields: store_id, ingredient_id, quantity, unit"
- **No Business Logic**: If it requires thinking about domain rules, it's NEW BEHAVIOR
- **Import/Reference Focus**: "Enables StoreService to import InventoryItemView"

### NEW BEHAVIOR Tasks
- **Concrete Test Cases**: "Write `test_explicit_store_emits_correct_event_type()` in `tests/test_explicit_inventory_store.py` verifying event.store_type == 'explicit'"
- **Single Behavior**: One test case per task, avoid complex scenarios
- **Observable Outcomes**: "User can create definition-based store via POST /stores with store_type field"

### REFACTOR Tasks
- **Behavior Preservation**: "Rename `infinite_supply` field to preserve existing test behavior in `test_domain_behavior.py:25-42`"
- **Test Guidance**: "All tests in `test_store_service.py` should remain green"
- **Small Steps**: "Extract method in single file, run tests, commit before next extraction"

### Step 5: Update TIP File with Tasks

**IMPORTANT**: Append the task breakdown to the existing TIP file at `$ARGUMENTS`.

Add a new section at the end of the TIP:

```markdown
---

## Implementation Tasks

[Generated task structure from Step 4]

---

## Success Criteria for Implementation

- [ ] All tasks completed and marked as done
- [ ] All tests passing: `[command from TIP quality gates]`
- [ ] Integration points validated
- [ ] Risk mitigations implemented as described
- [ ] Code follows architectural patterns from TIP

**Implementation Note**: Tasks may be reordered, skipped, or added during implementation as reality requires. This task plan is a guide, not a script. Use `implement-tasks` to begin implementation.
```

### Step 6: Present Updated Plan

I've updated the TIP at `$ARGUMENTS` with detailed task breakdown.

**Task Overview**:
- **Total Tasks**: [Number] high-level tasks
- **Total Sub-tasks**: [Number] categorized sub-tasks
  - SETUP: [N] sub-tasks
  - NEW BEHAVIOR: [M] sub-tasks
  - REFACTOR: [P] sub-tasks
- **Complexity Assessment**: [Aligns with TIP total complexity estimate]

**Task Sequencing**:
1. Task 1: [Name] - [Category] - [Maps to TIP Phase N]
2. Task 2: [Name] - [Category] - [Maps to TIP Phase N]
3. Task 3: [Name] - [Category] - [Maps to TIP Phase N]
[etc.]

**Key Interpretation Decisions Made**:
- [How you interpreted a TIP strategic direction]
- [Why you chose specific files or approaches]
- [Sequencing decisions within TIP constraints]

**The TIP now contains**:
- ✅ Strategic phases (original TIP content)
- ✅ Detailed implementation tasks (newly added)
- ✅ Success criteria for completion

Please review and let me know:
- Are the file:line references correct?
- Are the test cases well-scoped?
- Should any tasks be reordered or split?
- Missing deliverables or edge cases?

Then WAIT for user feedback and approval.

### Step 7: After Approval

Perfect! The implementation plan is complete.

**Next step**:
- Use `implement-tasks` to begin implementation
- Tasks can be adapted during implementation as reality requires
- The plan is a guide to help you navigate, not a rigid script

---

## Quality Guidelines for Task Planning

**Good Task Plans**:
- Interpret TIP strategic direction into concrete actions
- Include specific file:line references for navigation
- Design meaningful test cases with clear names
- Sequence tasks to enable incremental validation
- Break down work into manageable chunks (< 2 hours per task)
- Clearly classify tasks (SETUP/NEW BEHAVIOR/REFACTOR)

**Signs You're Over-Specifying**:
- Writing actual code implementations in task descriptions
- Providing exact test assertions (describe behavior, not code)
- Trying to solve all edge cases in planning
- Making tasks too granular (< 15 minutes)

**Signs You're Under-Specifying**:
- Tasks lack file references or locations
- Test descriptions are vague ("test the feature")
- No clear deliverables or outcomes
- Tasks too complex (high decision density without guidance)

**Remember Your Role**:
- You're interpreting strategic direction, not creating it
- You're making tactical decisions within strategic constraints
- You're adding specificity that enables implementation
- You trust `implement-tasks` to adapt as needed during execution

---

## Success Criteria for Task Plan

- [ ] All tasks map clearly to TIP phases
- [ ] File:line references are accurate and helpful
- [ ] Test cases are concrete with clear behavior to verify
- [ ] Tasks sequenced following TIP strategic direction
- [ ] SETUP/NEW BEHAVIOR/REFACTOR classification is clear
- [ ] Each task is actionable with appropriate scope
- [ ] Task complexity aligns with TIP estimate (decision density, steering needs)
- [ ] Tasks optimize for Claude implementation with human oversight checkpoints

The updated TIP now serves as both strategic vision and tactical roadmap.
