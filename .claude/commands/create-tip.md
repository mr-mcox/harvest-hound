Generate a Technical Implementation Plan (TIP) for: $ARGUMENTS

## Preparation Phase

### 1. Architecture Review
Review these key architectural documents to understand current patterns and constraints:
- @docs/architecture/domain-model.md - Core DDD patterns and bounded contexts
- @docs/architecture/overview.md - System architecture and technology decisions
- @docs/architecture/interface.md - API patterns and communication protocols
- @CLAUDE.md - Project overview and development principles
- @packages/backend/CLAUDE.md - Backend-specific patterns and guidelines
- @packages/frontend/CLAUDE.md - Frontend patterns and architecture rules

### 2. Decision History Analysis
Review relevant architectural decisions that might impact this work:
- @docs/development/decisions/ - Scan all ADRs for relevant patterns and constraints
- Look for decisions about event sourcing, domain boundaries, testing approaches
- Note any established patterns that must be followed or anti-patterns to avoid

### 3. Current State Assessment
Examine existing codebase to understand current implementation patterns:
- Identify existing domain models, services, and API endpoints that relate to this use case
- Review current event sourcing patterns and event schemas
- Check existing testing patterns and quality standards
- Look for similar features already implemented that can inform approach

### 4. Library Documentation Review
Use Context7 to get current documentation for key libraries that will be used:
- Identify which libraries/frameworks will be central to implementation
- Retrieve current documentation for critical APIs and patterns
- Note any recent changes or deprecations that might affect approach
- Document key APIs and usage patterns to be aware of during implementation

### 5. Risk and Complexity Analysis
Assess potential technical challenges:
- Identify integration points that could introduce complexity
- Evaluate event schema design decisions and migration concerns
- Consider frontend/backend coordination challenges
- Assess LLM integration complexity and error handling needs
- Note any library API changes or deprecations that might affect implementation

## TIP Generation

Using the preparation analysis, generate a comprehensive Technical Implementation Plan following this structure:

1. **Context & Problem Analysis**
   - Synthesize current state from codebase review
   - Document architecture fit based on DDD patterns
   - Identify any conflicts with existing decisions

2. **Technical Approach & Design Decisions**
   - Propose specific approach informed by current library documentation
   - Document key decisions with alternatives considered
   - Map to established project patterns from architecture review
   - Note key library APIs and patterns to leverage
   - **Research Recommendations**: List specific areas where additional research might be valuable

3. **Implementation Architecture**
   - Define bounded context impacts based on domain model
   - Design event flows following existing event sourcing patterns
   - Plan integration points (API, WebSocket, database, LLM)

4. **Testing & Quality Strategy**
   - Apply testing patterns from backend/frontend guidelines
   - Define quality gates based on performance requirements
   - Plan TDD approach following project testing principles

5. **Implementation Sequencing**
   - Sequence work to minimize risk based on complexity analysis
   - Plan incremental delivery following established patterns
   - Consider rollback needs for database/event schema changes

6. **Task Breakdown Preview**
   - Estimate effort using t-shirt sizes (XS/S/M/L/XL)
   - Identify major work streams and dependencies

The output should follow the template @docs/templates/technical-implementation-plan.md

## Output

Save the completed TIP as: `docs/development/tips/tip-[feature-name].md`

Include in the TIP:
- References to specific architecture documents that influenced decisions
- Links to relevant code examples that inform the approach
- Key library APIs and patterns identified from current documentation
- **Research Recommendations**: Specific areas worth investigating further
- Clear rationale for all major technical decisions
- Specific quality gates and success criteria
- Realistic effort estimates with confidence levels

## Quality Checklist

Before finalizing the TIP, verify:
- [ ] Aligns with established DDD and event sourcing patterns
- [ ] Follows container/presentation separation for frontend work
- [ ] Respects bounded context boundaries from domain model
- [ ] Includes proper event schema design considerations
- [ ] Plans for both unit and integration testing appropriately
- [ ] Considers performance implications and optimization strategies
- [ ] Addresses error handling and edge cases
- [ ] Provides clear success criteria and validation approach

The TIP should be detailed enough to inform confident task breakdown while remaining focused on architectural decisions rather than implementation details.
