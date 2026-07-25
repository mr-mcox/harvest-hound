# Learnings

Validated discoveries from prototype, MVP build, and production use.

## Files

- **`domain.md`** - Domain model, entities, boundaries, modeling decisions, core concepts
- **`workflows.md`** - Workflow patterns, user behaviors, what works/doesn't work, use cases
- **`technical.md`** - BAML prompts, API shapes, performance, LLM patterns
- **`ux.md`** - UI/UX patterns, interaction design, emerging needs
- **`architectural.md`** - Architecture decisions, patterns to keep/change, technical debt

## How to Use

(Phases refer to the pi-platform `coding-workflow` skill.)

**During problem-space / solution-space (writing a brief)**:
- Read `domain.md` for entity relationships and boundaries
- Read `workflows.md` for validated user behavior patterns
- Read `ux.md` for interaction patterns

**During implement**:
- Read `technical.md` for BAML patterns and API shapes
- Read `architectural.md` for patterns to follow
- Read `domain.md` for modeling constraints

**During compact**:
- Add discoveries to appropriate category file
- Use checkboxes `[x]` for validated learnings
- Include discovery context and date
- Annotate superseded entries in place (SUPERSEDED/REFINED + date) rather than deleting

## Cross-References by Topic

**Ingredient Claiming**:
- `domain.md`: Claiming mechanics, quantity-aware claiming, claim types
- `technical.md`: LLM/code separation, decremented inventory pattern
- `workflows.md`: Sequential claiming workflow, multi-wave generation

**Priority System**:
- `domain.md`: Priority drives recipe importance, orthogonal dimensions, priority gap
- `workflows.md`: Flat ingredient view, LLM-suggested priorities
- `ux.md`: Priority badge interaction patterns

**Recipe Generation**:
- `domain.md`: Recipe representations, pitch as projection, identity boundaries
- `technical.md`: BAML prompts, auto-pivot, technique diversity
- `workflows.md`: Two-phase browsing, iterative generation waves

**Shopping List**:
- `domain.md`: Three-tier ingredient sources, multiple grocery stores
- `technical.md`: Likelihood-based sourcing, claims aggregation endpoint
- `workflows.md`: Shopping list view fills workflow gap

**Recipe Persistence**:
- `domain.md`: Recipe lifecycle states, ingredient claim entity
- `workflows.md`: Recipe persistence transforms system feel
- `ux.md`: Different views for different contexts

## Format

Each learning follows this pattern:

```markdown
- [x] **[Discovery title]**: [Specific insight]
  - [Supporting detail or user reaction]
  - [Implementation note or consequence]
  - (discovered: [context], [date])
```

Use `[x]` for validated discoveries, `[ ]` for hypotheses being tested.
