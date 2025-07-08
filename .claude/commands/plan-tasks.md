Create a detailed implementation task plan for: $ARGUMENTS

## Input Requirements

**REQUIRED**: Reference the Technical Implementation Plan (TIP) at: $ARGUMENTS
- Use the TIP's architecture decisions and sequencing to inform task breakdown
- Leverage the TIP's work stream organization and effort estimates
- Follow the TIP's integration points and testing strategy

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

Follow this hierarchical approach:

```markdown
## Task [N]: [High-Level Feature/Component] (TIP Reference)
**Goal**: [Overall objective from TIP work stream]

### [N.1] [Sub-Component Name] - **[SETUP ONLY|NEW BEHAVIOR|REFACTOR]**
- [ ] **[Specific deliverable]** - [Brief description]
- [ ] **[Specific deliverable]** - [Brief description]
- [ ] **[Specific deliverable]** - [Brief description]

### [N.2] [Sub-Component Name] - **[SETUP ONLY|NEW BEHAVIOR|REFACTOR]**
- [ ] **[Specific deliverable]** - [Brief description]
- [ ] **[Specific deliverable]** - [Brief description]
```

**Key Principles**:
- **High-level tasks** align with TIP work streams and provide architectural context
- **Sub-tasks** group related work with clear testing classification
- **Checkboxes** are specific, actionable deliverables within each sub-task
- **Classification** applies to the sub-task level, not individual checkboxes

## Task Sequencing Principles

**From TIP Analysis**:
- Follow the TIP's dependency chain and work stream organization
- Prioritize SETUP tasks that enable subsequent NEW BEHAVIOR tasks
- Group REFACTOR tasks to minimize context switching
- Sequence tasks to enable incremental testing and validation

**Testing Flow**:
- SETUP tasks first → enable importing and referencing
- NEW BEHAVIOR tasks next → implement and test core functionality
- REFACTOR tasks last → optimize and clean up

## Quality Guidelines

### SETUP ONLY Tasks
- **Be Extremely Specific**: "Create class with these exact fields, methods return NotImplementedError"
- **No Business Logic**: If it requires thinking about domain rules, it's NEW BEHAVIOR
- **Import/Reference Focus**: "Enables X to import Y" or "Allows Z to reference W"

### NEW BEHAVIOR Tasks
- **Concrete Test Cases**: Specify exact inputs and expected outputs
- **Single Behavior**: One test case per task, avoid complex scenarios
- **Observable Outcomes**: Focus on what users see or systems produce

### REFACTOR Tasks
- **Behavior Preservation**: Be explicit about what behavior must stay the same
- **Test Guidance**: Specify which existing tests should guide the work
- **Small Steps**: Break large refactorings into small, safe steps

## Success Criteria for Task Plan

- [ ] All tasks clearly categorized with appropriate testing approach
- [ ] SETUP tasks enable subsequent work without business logic
- [ ] NEW BEHAVIOR tasks have specific, testable outcomes
- [ ] REFACTOR tasks preserve existing behavior while achieving improvement goals
- [ ] Task sequence follows TIP's architecture and reduces implementation risk
- [ ] Total effort aligns with TIP's size estimate and confidence level

Save the plan as `docs/development/tasks-ACTIVE.md` with clear task categories and TIP references.
