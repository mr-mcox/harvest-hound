You are implementing tasks from the implementation plan  @docs/development/tasks-ACTIVE.md using category-specific workflows.

## Process for Each Sub-Task:

1. **Open @docs/development/tasks-ACTIVE.md** and identify the next uncompleted sub-task (format: "### [N.X] [Name] - **[CATEGORY]**")

2. **Identify task category** from the sub-task heading: **[SETUP ONLY|NEW BEHAVIOR|REFACTOR]**

3. **Work through all checkboxes** in that sub-task using the category-specific workflow

4. **After completing each sub-task:**
   - Mark all checkboxes as ✓ completed
   - Run appropriate tests to ensure no regressions
   - Commit the progress: "Complete [sub-task name]"
   - **PAUSE** and ask for user review/feedback

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
5. Commit immediately: "SETUP: Add [component] scaffolding"

**Red Flags - Stop and Re-categorize if:**
- You're writing business rules or domain logic
- You're making decisions about data processing
- You're implementing actual functionality beyond basic structure

## 🧪 NEW BEHAVIOR Workflow

**Purpose**: Implement new business logic through test-driven development

**RED Phase**: Write failing test(s) that describe the exact behavior
- Test should fail for the right reason (not syntax errors)
- Use the specific test case from the task description
- Run tests to confirm failure
- Commit failing tests: "RED: Add test for [specific behavior]"

**GREEN Phase**: Write minimal implementation to make test pass
- Focus on making tests pass, not perfect code
- Use existing SETUP scaffolding where possible
- Run tests to confirm they pass
- Commit passing implementation: "GREEN: Implement [specific behavior]"

**REFACTOR Phase** (if needed): Clean up code while keeping tests green
- Extract methods, improve names, remove duplication
- Run tests after each change to ensure they stay green
- Commit refactoring: "REFACTOR: Clean up [component]"

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
4. If tests pass, commit: "REFACTOR: [specific improvement]"
5. If tests fail, revert and try smaller change

**Safe Refactoring Patterns:**
- Extract method/function from larger code block
- Rename variables/methods for clarity
- Move code between modules without changing interface
- Optimize performance while maintaining same outputs

## Sub-Task Categories Quick Reference

| Category | Tests | Implementation | Commit Pattern |
|----------|-------|----------------|----------------|
| **SETUP ONLY** | None needed | Stubs + NotImplementedError | "SETUP: Complete [sub-task name]" |
| **NEW BEHAVIOR** | TDD (RED/GREEN) | Full implementation | "Complete [sub-task name] with tests" |
| **REFACTOR** | Keep existing green | Preserve behavior | "REFACTOR: Complete [sub-task name]" |

## Quality Gates

- **SETUP ONLY**: All checkboxes create importable scaffolding without errors
- **NEW BEHAVIOR**: All checkboxes implemented with tests, specified behaviors work
- **REFACTOR**: All existing tests remain green, improvements achieved

## Error Recovery

**If you realize a sub-task is miscategorized:**
1. Stop current work
2. Explain the category mismatch to user
3. Suggest correct category and approach
4. Wait for user confirmation before proceeding

**If checkboxes become too complex:**
1. Focus on one checkbox at a time
2. Break complex behaviors into smaller pieces
3. Ask user if sub-task needs to be split

## Important Rules

- **NEVER** add business logic to SETUP ONLY sub-tasks
- **NEVER** skip tests for NEW BEHAVIOR sub-tasks
- **NEVER** change test behavior during REFACTOR sub-tasks
- **ALWAYS** run tests before committing each sub-task
- **ALWAYS** pause for user feedback after each completed sub-task

Following these workflows ensures clean implementation with appropriate testing coverage and minimal course correction.
