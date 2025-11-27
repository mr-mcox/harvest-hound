# Implement Tasks Command

You are implementing tasks from the TIP implementation plan using category-specific workflows.

**Development Model**: This is spec-based development where you (Claude) write the code with human oversight and steering. The human engineer reviews your work, provides direction, and makes key decisions.

**Core Principle**: Plans are carefully designed, but reality can be messy. Follow the plan's direction while adapting to what you discover during implementation.

---

## Finding Your Task Plan

The task plan is appended to the TIP at the path specified in the TIP metadata or design decision.

**Common locations**:
- `docs/development/tips/tip-[feature-name].md` (scroll to bottom for "Implementation Tasks" section)
- Check TIP metadata for exact path

The task plan contains sub-tasks formatted as: `### [N.X] [Name] - **[CATEGORY]**`

---

## Process for Each Sub-Task

1. **Find next uncompleted sub-task** in the Implementation Tasks section

2. **Identify task category**: **[SETUP ONLY|NEW BEHAVIOR|REFACTOR]**

3. **Work through checkboxes** using the category-specific workflow below

4. **After completing each sub-task:**
   - Mark checkboxes as completed in the TIP
   - Run appropriate tests to ensure no regressions
   - Run pre-commit checks and fix any issues
   - **PAUSE for human oversight** - This is a checkpoint for the human engineer to:
     - Review your approach and implementation
     - Validate code quality and test coverage
     - Provide steering or course correction if needed
     - Approve proceeding to the next sub-task

---

## 🏗️ SETUP ONLY Workflow

**Purpose**: Create scaffolding that enables other code to import/reference

**Implementation Rules:**
- **NO BUSINESS LOGIC**: If it requires domain knowledge or complex logic, it's miscategorized
- **Stubs Only**: Create empty classes, methods that raise NotImplementedError, basic schemas
- **Import/Reference Focused**: Goal is to enable other code to import and reference

**Process:**
1. Create the minimal structure specified in the task
2. For class methods: `raise NotImplementedError("TODO: implement in NEW BEHAVIOR task")`
3. For schemas: Include only field definitions, no computed properties or validators
4. For routes: Basic signature with `raise NotImplementedError("TODO: implement endpoint logic")`
5. Run pre-commit to verify code quality

**Red Flags - Stop and Re-categorize if:**
- You're writing business rules or domain logic
- You're making decisions about data processing
- You're implementing actual functionality beyond basic structure

---

## 🧪 NEW BEHAVIOR Workflow

**Purpose**: Implement new business logic through test-driven development

**RED Phase**: Write failing test(s) that describe the exact behavior
- Test should fail for the right reason (not syntax errors)
- Use the test case guidance from the task description
- Run tests to confirm failure
- Run pre-commit to ensure test code quality

**GREEN Phase**: Write minimal implementation to make test pass
- Focus on making tests pass, not perfect code
- Use existing SETUP scaffolding where possible
- Run tests to confirm they pass
- Run pre-commit to ensure implementation code quality

**REFACTOR Phase** (if needed): Clean up code while keeping tests green
- Extract methods, improve names, remove duplication
- Run tests after each change to ensure they stay green
- Run pre-commit to ensure refactored code quality

---

## 🔄 REFACTOR Workflow

**Purpose**: Improve existing code while preserving behavior

**Implementation Rules:**
- **Behavior Preservation**: Existing functionality must work exactly the same
- **Test-Guided**: Let existing tests guide your changes
- **Small Steps**: Make tiny changes, run tests frequently

**Process:**
1. Run existing tests to establish baseline (must be green)
2. Make small improvement while preserving behavior
3. Run tests to ensure no regressions
4. Run pre-commit to ensure code quality
5. If tests or pre-commit fail, revert and try smaller change

**Safe Refactoring Patterns:**
- Extract method/function from larger code block
- Rename variables/methods for clarity
- Move code between modules without changing interface
- Optimize performance while maintaining same outputs

---

## When Reality Diverges from Plan

**Plans are guides, not scripts.** Adapt as needed while maintaining quality and communicating changes.

### If You Discover a Task is Unnecessary

**Example**: "After implementing Phase 1, I realize this validation is already handled elsewhere"

**Process**:
1. Explain why the task isn't needed
2. Mark the task as skipped with rationale: `- [x] ~~[Task]~~ - SKIPPED: [Reason]`
3. Update task plan in TIP with note
4. Continue with next task

### If You Discover Blocking Dependencies

**Example**: "Task 3 needs the database schema from Task 5 to work"

**Process**:
1. Explain the dependency you discovered
2. Propose reordering: "I'll do Task 5 before Task 3 because..."
3. Wait for user confirmation
4. Update task sequence in TIP with note about reordering
5. Proceed with new sequence

### If You Discover New Work is Needed

**Example**: "To implement this feature, we also need to add error handling that wasn't in the plan"

**Process**:
1. Explain what's needed and why you discovered it now
2. Propose where it fits: "I'll add this as Task 3.5 because..."
3. Write the new task/sub-task with appropriate category
4. Wait for user approval
5. Add to task plan in TIP
6. Implement the new work

### If You Find a Better Approach

**Example**: "The plan suggests creating a new service, but I can extend the existing one more cleanly"

**Process**:
1. Explain the improvement you've identified
2. Describe impact on remaining tasks
3. Propose the adjustment
4. Wait for user confirmation
5. Update affected tasks in TIP
6. Proceed with improved approach

### If Implementation is More Complex Than Expected

**Example**: "This task requires more decisions and context coordination than the complexity estimate suggested"

**Process**:
1. Explain what's more complex than anticipated (novel patterns, more integration points, unclear requirements)
2. Identify if you need: more human decisions, clearer direction, or task breakdown
3. Discuss with user: Continue with more steering, or break down the task?
4. Update complexity assessment in TIP if pattern emerges
5. Proceed with agreed approach

---

## Quality Gates

**Before Completing Each Sub-Task**:
- [ ] Category workflow followed appropriately
- [ ] Tests written and passing (for NEW BEHAVIOR)
- [ ] Existing tests still passing (for REFACTOR)
- [ ] Pre-commit checks passing
- [ ] Code follows architectural patterns from TIP
- [ ] Changes marked in task plan

**SETUP ONLY**:
- [ ] Scaffolding is importable without errors
- [ ] No business logic implemented
- [ ] NotImplementedError stubs in place

**NEW BEHAVIOR**:
- [ ] Tests written first (RED)
- [ ] Implementation makes tests pass (GREEN)
- [ ] Code refactored if needed (REFACTOR)
- [ ] Behavior matches task description

**REFACTOR**:
- [ ] All existing tests remain green
- [ ] Behavior unchanged
- [ ] Code quality improved

---

## Sub-Task Categories Quick Reference

| Category | Tests | Implementation | When to Adapt |
|----------|-------|----------------|---------------|
| **SETUP ONLY** | None needed | Stubs + NotImplementedError | If business logic needed, re-categorize |
| **NEW BEHAVIOR** | TDD (RED/GREEN) | Full implementation | If test approach needs adjustment, explain and adapt |
| **REFACTOR** | Keep existing green | Preserve behavior | If behavior must change, it's NEW BEHAVIOR instead |

---

## Error Recovery

### If You Realize a Sub-Task is Miscategorized

**Example**: "This SETUP task actually requires complex validation logic"

1. Stop current work
2. Explain the category mismatch: "This task involves business rules for X, so it should be NEW BEHAVIOR"
3. Suggest correct category and approach
4. Wait for user confirmation
5. Update task category in TIP
6. Proceed with correct workflow

### If Checkboxes Are Too Complex

**Example**: "This checkbox says 'implement authentication' which is actually 10 different things"

1. Identify the complexity: "This breaks down into: session management, token validation, user lookup..."
2. Propose breaking it into sub-tasks
3. Wait for user agreement
4. Update task plan in TIP with breakdown
5. Implement step by step

### If You Get Blocked

**Example**: "This task requires a library we don't have, and I'm not sure which one to use"

1. Explain the blocker clearly
2. Propose 2-3 alternatives if possible
3. Ask for user decision or guidance
4. Wait for response
5. Update task plan with decision
6. Continue with selected approach

---

## Implementation Complete - Cleanup Scaffolding

**When ALL tasks are complete:**

1. **Run final verification**:
   - All tests passing: `[command from TIP quality gates]`
   - Pre-commit checks clean
   - Integration points working
   - Code matches domain model documentation

2. **Prompt user for scaffolding cleanup**:

```
✅ All tasks implemented and tested!

Implementation is complete. Time to clean up scaffolding documents.

**Verify implementation matches design**:
- [ ] Implementation files exist as specified
- [ ] Domain model reflects actual implementation
- [ ] All tests pass and behavior matches design
- [ ] Integration points validated

**Ready to clean up scaffolding**:
- Design decision: `[path]`
- TIP (including task plan): `[path]`

The code is now the authoritative source of truth. Scaffolding served its purpose and can be deleted.

Would you like me to delete these scaffolding files now, or would you prefer to review first?
```

3. **If user approves deletion**:
   - Delete the design decision file (if exists)
   - Delete the TIP file (including appended task plan)
   - Confirm: "Scaffolding cleaned up. Implementation complete!"

4. **If user wants to review**:
   - Wait for user confirmation before deleting

---

## Important Principles

### Follow the Plan's Direction
- Use the task plan as your guide
- Understand the strategic intent behind each phase
- Let the plan inform your approach

### Adapt to Reality
- Plans can't anticipate everything
- You'll discover things during implementation
- Communicate changes and adjust intelligently

### Maintain Quality
- **NEVER** skip tests for NEW BEHAVIOR
- **NEVER** break existing tests during REFACTOR
- **ALWAYS** run pre-commit before marking tasks complete
- **ALWAYS** pause for user feedback after sub-tasks

### Communicate Adaptations
- Explain why you're deviating from the plan
- Propose the adjustment clearly
- Wait for confirmation on significant changes
- Update the task plan to reflect reality

### Trust the Process
- The plan provides valuable structure
- Your judgment during implementation is equally valuable
- The combination of planned direction + adaptive execution produces the best results

---

## Remember

**The task plan is a guide, not a script.**

- Follow it when it makes sense
- Adapt it when reality requires
- Communicate changes clearly
- Maintain quality throughout
- Trust your judgment while respecting the strategic direction

Good implementation balances planned structure with adaptive intelligence.
