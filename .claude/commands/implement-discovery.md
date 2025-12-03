# Implement Discovery Command

Quickly implement a solution for: $ARGUMENTS

## Purpose

Rapid implementation of experiments to test pain point solutions. Speed over perfection.

**Key Principle**: YOLO coding. Get something working fast so the user can feel it.

---

## Path Reference Note

**IMPORTANT**: File paths reference the **project root** (`/Users/mcox/dev/harvest-hound/`). Since we work in `prototype/`, use `../` to reach project root files.

Example: `.scratch/pain-[topic].md` means `../.scratch/pain-[topic].md` from the prototype directory.

---

## Background Context

**Pain Analysis** (if exists):
- Check `.scratch/pain-[topic].md` for structured context from `/discover-pain` (use `../.scratch/` from prototype)

**Prototype Structure** (current working directory):
- `app.py` - FastAPI backend (in current dir)
- `templates/` - HTML templates (if exists, in current dir)
- `static/` - JS/CSS (if exists, in current dir)
- `baml_src/` - BAML prompts (in current dir)

**Domain Vocabulary** (for reference only):
- `docs/domain-model-reference.md` - Don't constrain implementation, but use consistent terms (use `../docs/` from prototype)

---

## Process

### Step 1: Gather Context

Check for pain analysis document:
```
Read .scratch/pain-[topic].md if it exists
```

If found:
"Found pain analysis for [topic]. Building on:
- **Pain**: [from document]
- **Experiment**: [proposed experiment]
- **Success Criteria**: [from document]"

If not found:
"No pain analysis found. Let me understand what we're building:
- What specific behavior are we implementing?
- What does success look like?"

Then WAIT for context (from document or user).

### Step 2: Targeted Code Exploration

Use direct tools (Read, Glob) to understand current prototype structure:

```
Glob: prototype/**/*.py
Glob: prototype/**/*.html
Glob: prototype/**/*.js
```

**Scope**: Find where to make changes, not exhaustive code review.
**Stop when**: You know which file(s) to modify and where.

Read key files to understand:
- Current endpoints (for backend changes)
- Current UI structure (for frontend changes)
- Where to add the new behavior

### Step 3: Acknowledge the Experiment

"Implementing: [what we're building]
Goal: Test if [hypothesis] helps with [pain point]

Based on current prototype structure:
- Backend changes: [where in app.py]
- Frontend changes: [where in templates/HTML]
- New files needed: [if any]"

### Step 4: Choose Simplest Approach

Pick the path of least resistance:
- Inline everything in app.py
- Add UI elements directly to templates
- Use global variables if needed
- Copy-paste liberally

**Scope control**:
- Single behavior change per experiment
- Minimal files touched (1-2 ideal, 3 max)
- First working solution, not best solution

### Step 5: Implement in Stages

1. **Backend first** (if needed)
   - Add endpoint/model change
   - Test with curl/print statements

2. **Frontend next**
   - Add UI elements
   - Wire up events
   - Show feedback to user

3. **Connect them**
   - Make sure data flows
   - Don't worry about error handling

### Step 6: Make It Demoable

Get to a state where user can:
- Click through the workflow
- See the new behavior
- Provide immediate feedback

"The experiment is ready to try. Run the prototype and [specific action to test]."

### Step 7: Gather Reaction

"Try this out and let me know:
1. Does this help with [pain point]?
2. What feels good/bad about it?
3. What surprised you?

When ready, use `/capture-learning [topic]` to document what we discovered."

---

## Implementation Patterns

### Pattern: Progressive Disclosure
```python
# Backend - return minimal then full data
@app.get("/recipes/summary")
async def recipe_summaries():
    return [{"id": r.id, "name": r.name, "key_ingredients": r.ingredients[:3]}]

@app.get("/recipes/{id}/full")
async def recipe_detail(id: str):
    return {"name": r.name, "all_ingredients": r.ingredients, "instructions": r.instructions}
```

### Pattern: Bulk Operations
```python
# One-click operations
@app.post("/recipes/{id}/cook")
async def cook_recipe(id: str):
    # Mark all ingredients as used
    # Update meal plan
    # Return confirmation
```

### Pattern: Smart Defaults
```javascript
// Frontend - sensible defaults
const quantity = document.getElementById('quantity').value || 1;
const unit = document.getElementById('unit').value || 'unit';
```

---

## Speed Hacks

### Database Changes
```python
# Just add columns, don't migrate
class Recipe(SQLModel, table=True):
    summary: str = ""  # New field, default value
```

### Quick UI
```javascript
// Inline styles for speed
elem.style.display = showDetails ? 'block' : 'none';
```

### Mock Complex Parts
```python
# TODO: Real BAML integration
async def generate_with_ai():
    await asyncio.sleep(1)  # Fake processing
    return mock_data
```

---

## Success Indicators

- User can see/try the new behavior
- Single behavior change (not feature set)
- Generates "oh!" or "hmm..." reaction
- Reveals something about the domain

---

## Anti-patterns

- Refactoring existing code
- Adding error handling
- Creating abstractions
- Worrying about performance
- Writing tests
- Building "for later"
- Touching more than 3 files

---

## Handoff

After implementation is demoable:

"The experiment is ready. Here's how to test:
1. [Specific steps to run/access]
2. [What to try]
3. [What to observe]

After testing, use `/capture-learning [topic]` to document insights."
