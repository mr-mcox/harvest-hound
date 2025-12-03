# Pantry Definition Learning

**Discovered**: store-based-claiming experiment, 2025-12-01
**Uncertainty**: Medium
**Architectural Impact**: Low
**One-Way Door**: No

## The Question

How does the system learn what the user considers "pantry staples" vs "need to buy from grocery"?

## Context

During store-based-claiming experiment, the LLM assigned honey, walnuts, and onion to "Cub foods" (grocery store), but the user considers these pantry staples that are always stocked.

This reveals that:
- Pantry definition is fuzzy and user-specific
- System's assumptions become visible through grocery assignments
- Gap between system's pantry model and user's reality creates friction

## The Opportunity

Each time LLM assigns an ingredient to grocery, it reveals a potential pantry assumption mismatch. Could use this signal to refine pantry definition over time.

## Options Considered

### Option 1: Manual Pantry Management
- User explicitly adds ingredients to pantry definition store
- Simple, direct control
- **Pro**: Clear, no magic behavior
- **Con**: Requires ongoing maintenance, friction when adding new ingredients

### Option 2: Feedback Loop on Grocery Assignments
- When LLM assigns ingredient to grocery, user can say "Actually, that's pantry"
- System adds to pantry definition
- **Pro**: Learn from corrections, low friction
- **Con**: Requires UI for corrections, state management

### Option 3: Implicit Learning from Inventory History
- If ingredient appears in inventory frequently → consider pantry
- If never tracked in inventory → probably pantry staple
- **Pro**: No explicit action needed
- **Con**: Indirect signal, may be inaccurate

### Option 4: Hybrid: Seed + Learn
- Start with common pantry definition (oils, spices, basics)
- Learn from corrections and inventory patterns
- **Pro**: Best of both worlds
- **Con**: Most complex

## Architectural Implications

**Low impact** - This is primarily about pantry store definition content, not data model changes.

- No new database tables needed
- Pantry definition is just text on definition store
- Learning mechanism would update store definition field
- Could be entirely prompt-based (no persistence) initially

## Next Steps to Explore

1. Test with current manual pantry editing - is it acceptable friction?
2. Observe how often grocery assignments feel wrong
3. If frequent, implement feedback UI ("Move to pantry")
4. Track if patterns emerge (certain ingredient types always pantry)
5. Consider LLM-assisted pantry definition expansion ("You marked honey as pantry. Should I also include maple syrup, agave?")

## Related Discoveries

- Likelihood-based claiming (open-questions/likelihood-based-claiming.md) - May reduce need for perfect pantry definition
- Multiple grocery stores (open-questions/multiple-grocery-stores.md) - Pantry vs which grocery to use
