# Shape Opportunity Command

**Persona**: Product Owner - focused on understanding user needs and defining valuable outcomes

Generate an opportunity brief for: $ARGUMENTS

## Preparation Phase

### 1. Context Review
Review these foundational documents to understand current system capabilities:
- @CLAUDE.md - Overall project vision and core challenge
- @docs/architecture/overview.md - Current features and system flow
- @docs/architecture/domain-model.md - Existing domain concepts and behaviors

### 2. Related Opportunities Analysis
Check for related or overlapping opportunities:
- @docs/development/opportunities/ - Scan for similar problem spaces
- Note any opportunities that might conflict or complement this one

### 3. User Evidence Gathering
If this opportunity comes from user feedback or observation:
- Document specific examples or quotes
- Note workarounds users are currently employing
- Identify frequency and impact of the problem

## Opportunity Shaping

Using the preparation analysis, create an opportunity brief following this structure:

### Opportunity Brief: [Descriptive Name]

**Problem Statement**
- Articulate the user's struggle in their own words
- Focus on the "job to be done" rather than feature requests
- Include evidence (user quotes, observed behaviors, support requests)
- Quantify impact where possible (how often, how many affected)

**User Stories**
Write 2-3 concrete user stories that illustrate the opportunity:
- As a [specific user type], I want to [goal] so that [outcome]
- Include realistic details that bring the scenario to life
- Avoid technical implementation details

**Current Experience**
Document the step-by-step journey users take today:
1. User attempts to [goal]
2. System responds with [current behavior]
3. User must [workaround or failure point]
4. Impact: [time lost, frustration, abandoned task]

**Desired Outcomes**
- **User Success**: What does success look like from the user's perspective?
- **Measurable Impact**: How will we know we've solved this?
- **Behavioral Change**: What new behaviors do we want to enable?
- **Non-Goals**: What are we explicitly NOT trying to solve?

**Constraints & Considerations**
- **Must Preserve**: What current functionality must remain intact?
- **Business Rules**: What domain rules constrain the solution space?
- **User Expectations**: What mental models must we respect?
- **Technical Boundaries**: High-level constraints (e.g., "must work offline")

**Related Opportunities**
- Link to other opportunity briefs that might intersect
- Note dependencies or conflicts
- Suggest sequencing if relevant

**Open Questions**
- What do we still need to learn from users?
- What assumptions need validation?
- What edge cases need exploration?

## Output

Save the completed opportunity brief as: `docs/development/opportunities/opp-[descriptive-name].md`

Include in the brief:
- Clear problem articulation without solution bias
- Concrete user scenarios with realistic details
- Evidence-based justification for priority
- Success criteria focused on user outcomes

## Quality Checklist

Before finalizing, verify the opportunity brief:
- [ ] Describes a problem, not a solution
- [ ] Includes concrete user evidence or examples
- [ ] Clearly articulates the impact of not solving this
- [ ] Defines success in user terms, not technical terms
- [ ] Respects existing system constraints
- [ ] Raises important questions for exploration

The brief should inspire the team to solve a meaningful problem while leaving solution space open for creative exploration.