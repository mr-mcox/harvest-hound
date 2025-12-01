# Pitch State Management

**Discovered**: ingredient-claiming-cognitive-load experiment, 2025-12-01
**Uncertainty**: Low
**Architectural Impact**: Low
**One-Way Door**: No

## The Question

What states should pitches have, and how do we manage transitions between them?

## Context

User insight:
> "There could be a state machine here but it could be quite light... I'm curious long term whether it's a pitch state machine or recipe state machine."

Currently pitches have implicit states:
- Generated (available to select)
- Selected (user clicked it)
- Invalid (ingredients claimed by another recipe)

But workflow suggests more explicit states needed:
- `available` (can be selected)
- `selected` (user picked it for fleshing out)
- `rejected` (user explicitly doesn't want it)
- `unavailable` (ingredients claimed, can't be made)

## Options Considered

### Option A: Minimal State (Current)
- Track only: selected pitches (Set)
- Compute: invalid pitches (Set) on render
- Everything else is available

**Pros**:
- Simple, minimal state
- Works for current workflow

**Cons**:
- Can't distinguish "haven't looked at" from "explicitly rejected"
- Regeneration can't avoid rejected pitches

### Option B: Explicit State Field
- Each pitch has state: available | selected | rejected | unavailable
- State transitions:
  - available → selected (user picks)
  - available → rejected (user explicitly dismisses)
  - available → unavailable (ingredients claimed)
  - selected → available (user deselects before fleshing out)

**Pros**:
- Clear state model
- Can avoid rejected pitches in future generations
- Better UX feedback

**Cons**:
- More state to manage
- Need UI for rejection action

### Option C: Lightweight State Tracking
- Track two sets: selected, rejected
- Compute invalid on demand
- available = not (selected | rejected | invalid)

**Pros**:
- Balance simplicity with functionality
- Supports "don't show me this again" workflow
- Minimal additional state

## Architectural Implications

**Frontend State**:
- Currently: `selectedPitches` (Set), `invalidPitches` (Set)
- Add: `rejectedPitches` (Set)?
- Or: `pitchStates` (Map<index, state>)?

**Persistence**:
- States are session-scoped (ephemeral)
- Don't need database persistence
- Reset on new generation batch

**Generation Flow**:
- When generating more pitches, avoid rejected ones?
- Or: user can always generate fresh batch to reset

**UI Interaction**:
- Click to select (toggle)
- Need explicit reject action? (X button? Right-click menu?)
- Or: rejected = "generated but never selected after seeing many batches"

**Removal Behavior**:
User feedback: "I'd like them removed" for invalid pitches
- Invalid pitches should disappear from UI
- Selected pitches persist until fleshed out
- Rejected pitches... keep or remove?

## Related Workflows

From LEARNINGS.md:
> **Pitch lifecycle management**: Invalid pitches should be removed automatically
> - User feedback: "I'd like them removed" - don't want to see unavailable options

Suggests:
- Invalid = remove from UI
- Selected = keep visible until fleshed out
- Rejected = TBD (probably remove or keep with visual indicator)

## Next Steps to Explore

1. **Test rejection UX**: Add "dismiss" button to pitches, see if user uses it
2. **Observe behavior**: Does user naturally avoid pitches or need explicit rejection?
3. **Track across sessions**: Do rejected pitches matter across generation batches?

## Current Decision

**Use Option A (Minimal State)** for now
- Selected and invalid are sufficient for current workflow
- Rejection might not be needed if generation quality is high
- Can add rejection state later if needed (not a one-way door)
- Focus on getting generation quality right first
