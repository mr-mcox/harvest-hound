# Prototype Phase Guidelines

## Mission

Rapid discovery of the **supple domain model** through user-centered iteration.

## Development Philosophy

- **YOLO Coding**: No tests, no abstractions, just exploration
- **User-Driven**: Real pain points drive implementation
- **Fast Iteration**: Change anything in < 30 minutes
- **Document Insights**: Learning matters more than code quality

## Discovery Workflow

### 1. Express Pain Point
User describes friction in current prototype:
"I want to see recipe overviews before full details"

### 2. Implement Solution  
Quick and dirty implementation to test the idea

### 3. Capture Learning
Document what worked, what didn't, what we discovered

## Stack Decisions

### Backend
- **FastAPI** - Simple and familiar
- **SQLModel** - Direct ORM usage, no repositories
- **BAML** - For LLM prompt iteration
- **uv** - Virtual environment management

### Frontend Options
- **Current**: Vanilla JS (fastest start)
- **If needed**: Minimal Svelte (better state management)
- **Decision point**: When clicking buttons for inventory becomes painful

## Key Discovery Questions

1. **Recipe Generation**
   - Batch vs iterative generation?
   - How much detail upfront vs progressive disclosure?
   - Streaming value vs complexity cost?

2. **Ingredient Management**
   - Is claiming just decrement or complex negotiation?
   - How important is normalization?
   - Substitution patterns?

3. **User Workflow**
   - Natural flow: CSA arrival → planning → shopping → cooking?
   - Where do users want control vs automation?
   - What delights vs annoys?

## Success Metrics

- Can demo new idea to someone in same day
- Can completely pivot approach in < 2 hours
- User says "oh that's nice!" not "hmm, what if..."

## Anti-patterns to Avoid

- Building abstractions "for later"
- Worrying about data models
- Adding error handling
- Writing tests
- Optimizing anything

## Commands

- `discover-pain` - Explore a friction point
- `implement-discovery` - Code a solution
- `capture-learning` - Document insights

## Running the Prototype

```bash
cd prototype
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://localhost:8000 and start discovering!