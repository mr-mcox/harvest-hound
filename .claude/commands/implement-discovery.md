# Implement Discovery Command

Quickly implement a solution for: $ARGUMENTS

## Purpose

Rapid implementation of experiments to test pain point solutions. Speed over perfection.

## Process

### Step 1: Acknowledge the Experiment

"Implementing: [what we're building]
Goal: Test if [hypothesis] helps with [pain point]"

### Step 2: Choose Simplest Approach

Pick the path of least resistance:
- Inline everything in app.py
- Add UI elements directly to index.html
- Use global variables if needed
- Copy-paste liberally

### Step 3: Implement in Stages

1. **Backend first** (if needed)
   - Add endpoint/model change
   - Test with curl/print statements

2. **Frontend next**
   - Add UI elements
   - Wire up events
   - Show feedback to user

3. **Connect them**
   - Make sure data flows
   - Don't worry about errors

### Step 4: Make It Demoable

Get to a state where user can:
- Click through the workflow
- See the new behavior
- Provide immediate feedback

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

## Success Indicators

✅ User can see/try the new behavior
✅ Takes < 30 minutes to implement
✅ Generates "oh!" or "hmm..." reaction
✅ Reveals something about the domain

## Anti-patterns

❌ Refactoring existing code
❌ Adding error handling
❌ Creating abstractions
❌ Worrying about performance

## Transition

After implementation:
"Try this out and let me know:
1. Does this help with [pain point]?
2. What feels good/bad about it?
3. What did we learn about the domain?"

Then use `capture-learning` to document insights.