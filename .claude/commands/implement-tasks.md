You are implementing tasks from the implementation plan using a self-managing red/green TDD workflow.

## Process for Each Task:

1. **Open @docs/development/tasks-ACTIVE.md** and identify the next uncompleted task (not marked with ✓)

2. **For tasks marked "No tests needed - setup only":**
   - Create minimal setup work: stubs, schemas, route definitions, basic UI components
   - For class stubs: use `raise NotImplementedError("TODO: implement in tests")` for method bodies
   - Goal: Enable testing/development, not functional implementation
   - Commit setup immediately with clear message
   - Mark as completed with ✓ in @paste.txt

3. **For tasks marked "Tests needed":**
   - **RED Phase**: Write failing test(s) that describe the exact behavior
     - Test should fail for the right reason
     - Run tests to confirm failure
     - Commit failing tests: "RED: Add test for [behavior]"

   - **GREEN Phase**: Write minimal implementation to make test pass
     - Focus on making tests pass, not perfect code
     - Run tests to confirm they pass
     - Commit passing implementation: "GREEN: Implement [behavior]"

   - **REFACTOR Phase** (if needed): Clean up code while keeping tests green
     - Extract methods, improve names, remove duplication
     - Run tests after each change
     - Commit refactoring: "REFACTOR: Clean up [component]"

4. **For tasks marked "Modify existing tests" or "Update existing tests":**
   - **ADJUST Phase**: Modify existing tests for new data structures/interfaces
     - Update test data/mocks to match new response shapes
     - Modify assertions to expect new field names or structures
     - Ensure existing behavior is preserved through refactor
     - Run tests to confirm they pass with new implementation
     - Commit test updates: "UPDATE: Modify tests for [new structure]"

5. **After completing each task:**
   - Update @tasks-ACTIVE.md to mark task as ✓ completed
   - Run full test suite to ensure no regressions
   - Commit the progress update: "Progress: Complete [task name]"
   - **PAUSE** and ask for user review/feedback

6. **Quality Gates:**
   - All tests must pass before moving to next task
   - Code must follow project conventions (use existing patterns)
   - Commit messages must be clear and descriptive
   - Each test should focus on ONE specific behavior

7. **Context Management:**
   - If a task seems too large, break it into smaller steps
   - If unclear about requirements, ask for clarification before coding
   - If tests become complex, simplify the behavior being tested

## Important Rules:
- NEVER skip the RED phase for test-required tasks
- NEVER write implementation code before tests for test-required tasks
- ALWAYS run tests before committing
- ALWAYS update progress in @tasks-ACTIVE.md
- ALWAYS pause for user feedback after each completed task
