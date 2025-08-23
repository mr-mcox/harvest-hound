# Design Concepts Command

**Persona**: UX Designer - focused on user mental models and interaction design

Generate concept designs for opportunity: $ARGUMENTS

## Preparation Phase

### 1. Opportunity Understanding
Review the source opportunity to deeply understand the problem:
- @$ARGUMENTS - The opportunity brief driving this design work
- Extract key user needs, constraints, and success criteria
- Note any specific user quotes or scenarios to design against

### 2. System Context Review
Understand current patterns and constraints:
- @docs/architecture/interface.md - Current UI patterns and interactions
- @packages/frontend/CLAUDE.md - Frontend architecture patterns
- @docs/architecture/domain-model.md - Domain concepts users might encounter

### 3. Design Pattern Inventory
Identify relevant existing patterns:
- Current interaction patterns that work well
- UI components that could be reused or extended
- Mental models users already understand in the system

### 4. Competitive Inspiration (Optional)
If relevant, note how similar problems are solved elsewhere:
- What mental models do users bring from other tools?
- What patterns should we intentionally avoid?

## Concept Design Process

Create 2-3 distinct concept directions that explore different approaches:

### Concept Design: [Opportunity Name]

**Design Challenge**
Reframe the opportunity as a "How might we..." question that opens solution space

**Success Criteria Recap**
- [Key outcome from opportunity]
- [Key outcome from opportunity]
- [Key outcome from opportunity]

---

### Concept A: [Descriptive Name]

**Core Insight**
One sentence capturing the key idea behind this concept

**Mental Model**
- How users would understand and describe this feature
- What metaphor or analogy guides the design
- How it fits with their existing mental models

**Key Behaviors Enabled**
- [Specific user action] → [System response] → [User benefit]
- [Specific user action] → [System response] → [User benefit]
- Focus on the most important/frequent interactions

**Information Architecture**
- What new concepts/objects are exposed to users?
- How do these relate to existing concepts?
- What vocabulary would users see?

**Interaction Flow**
```
1. User sees [entry point/trigger]
2. User can [primary action]
3. System shows [feedback/state]
4. User can then [follow-up actions]
5. Result: [end state]
```

**Key UI Moments**
Describe 2-3 critical screens or interactions:
- [Moment 1]: What makes this feel intuitive?
- [Moment 2]: How does this reduce friction?
- [Moment 3]: What provides confidence/clarity?

**Trade-offs**
- **Gains**: What becomes easier/better?
- **Losses**: What becomes harder/more complex?
- **Risks**: What could confuse users?

---

### Concept B: [Descriptive Name]

[Repeat same structure as Concept A, exploring a meaningfully different approach]

---

### Concept C: [Descriptive Name] *(if needed)*

[Repeat same structure, only if truly distinct third approach exists]

---

## Concept Comparison

| Aspect | Concept A | Concept B | Concept C |
|--------|-----------|-----------|-----------|
| Mental Model Fit | [How natural?] | [How natural?] | [How natural?] |
| Learning Curve | [How easy?] | [How easy?] | [How easy?] |
| Feature Completeness | [What's possible?] | [What's possible?] | [What's possible?] |
| Technical Complexity | [Relative effort] | [Relative effort] | [Relative effort] |

## Recommendation

**Recommended Concept**: [A/B/C]

**Rationale**
- Why this concept best serves user needs
- How it balances simplicity with capability
- Why it fits our system's design philosophy

**Enhancement Opportunities**
- Elements from other concepts worth incorporating
- Future iterations that could build on this

**Validation Needs**
- What aspects need user testing?
- What technical feasibility needs verification?
- What edge cases need exploration?

## Domain Implications Preview

Brief notes on how this concept might affect the domain:
- New domain concepts that might emerge
- Existing concepts that need evolution
- Behavioral changes required

## Output

Save the completed concept design as: `docs/development/concepts/concept-[opportunity-name].md`

Include in the design:
- Clear connection to user needs from opportunity brief
- Distinct approaches that explore the solution space
- Enough detail to understand user experience
- Honest assessment of trade-offs
- Clear recommendation with rationale

## Quality Checklist

Before finalizing, verify the concept design:
- [ ] Each concept offers a meaningfully different approach
- [ ] Mental models are explained in user terms
- [ ] Interaction flows are concrete and specific
- [ ] Trade-offs are honestly assessed
- [ ] Recommendation is clearly justified
- [ ] Validation needs are identified

The design should give enough clarity for domain design while maintaining flexibility for implementation details.