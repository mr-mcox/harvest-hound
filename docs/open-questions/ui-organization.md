# UI Organization and View Management

**Discovered**: recipe-persistence experiment, 2025-12-01
**Uncertainty**: Medium (need emerging, but specific solution unclear)
**Architectural Impact**: Medium (affects information architecture, not data model)
**One-Way Door**: No (can evolve incrementally)

## The Question

How should the UI be organized as features grow? Single page is getting cluttered - what views/modes do we need?

## Context

User feedback after implementing recipe persistence:
> "I think we're going to want to have different views of the system for the MVP - this is getting quite cluttered. Having a compact version of the recipe prominent is fine."

**Current state**: Everything on one page
- Left panel: Stores & Inventory management
- Right panel: Recipe Planning (My Planned Recipes + Pitch Generation + Full Recipes)
- Successful so far: "Single-page prototype goes far"
- Breaking point reached: Too much information competing for attention

## Different Contexts Identified

### 1. Planning Mode (current focus)
**Goal**: Generate meal plan for the week

**Needs**:
- Browse pitches
- Select and flesh out recipes
- See what's planned (compact view)
- Manage inventory
- Generate more pitches

**Current UI**: Works but cluttered

### 2. Cooking Mode (future)
**Goal**: Follow recipe while cooking

**Needs**:
- Step-by-step instructions (large, readable)
- Timer integration
- Ingredient checklist
- Notes/substitutions
- Minimal distractions

**Current UI**: Not optimized for this

### 3. Review Mode (future)
**Goal**: See week overview, manage completed recipes

**Needs**:
- Planned vs cooked vs abandoned status
- Ingredient utilization (what's used, what's wasting)
- Week-level metrics (time spent, variety)
- Feedback capture

**Current UI**: Not built yet

### 4. Inventory Management Mode (existing)
**Goal**: Add/update/delete inventory

**Needs**:
- Bulk entry (CSA paste)
- Individual item editing
- Store management
- Claim visibility

**Current UI**: Works in left panel

## Options Considered

### Option A: Tab-Based Navigation
```
[Plan] [Cook] [Review] [Inventory]

When "Plan" selected:
  - My Planned Recipes (compact)
  - Pitch generation
  - Full recipe view

When "Cook" selected:
  - Recipe selector
  - Step-by-step mode
  - Timers

When "Review" selected:
  - Week summary
  - Ingredient usage
  - Recipe history
```

**Pros**:
- Clear context switching
- Each mode can be optimized
- Familiar pattern

**Cons**:
- More navigation overhead
- Might feel like separate apps
- Some info needed across contexts

### Option B: Progressive Disclosure (current + refinement)
Keep single page, collapse/expand sections:
```
Page layout:
  ┌─────────────────────────────────┐
  │ My Planned Recipes (compact)    │ ← Always visible
  ├─────────────────────────────────┤
  │ [▼ Generate More Recipes]       │ ← Collapsible
  │    Pitches, Flesh Out, etc      │
  ├─────────────────────────────────┤
  │ [▼ Manage Inventory]            │ ← Collapsible
  │    Stores, Bulk Entry, etc      │
  └─────────────────────────────────┘
```

**Pros**:
- Minimal change from current
- Still feels like one hub
- Progressive disclosure reduces clutter

**Cons**:
- Still cramped on small screens
- Cooking mode still not optimized

### Option C: Modal/Overlay for Context Switches
Main page + overlays for specific tasks:
```
Main page: My Planned Recipes + Quick Actions

Click "Cook this recipe" → Full-screen cooking mode
Click "Generate recipes" → Modal with pitch browsing
Click "Manage inventory" → Sidebar overlay
```

**Pros**:
- Focus on primary context (meal planning hub)
- Context switches are immersive
- Main page stays clean

**Cons**:
- Modals can feel disruptive
- Browser back button confusion
- Mobile considerations

### Option D: Hybrid - Modes + Progressive Disclosure
Combine tab-based modes with smart defaults:
```
Default view: Planning Hub
  - My Planned Recipes (compact)
  - Inventory status (claimed vs available)
  - Quick actions (Generate, Manage)

Mode switch buttons:
  - [📋 Plan] ← active by default
  - [🍳 Cook] → full-screen recipe view
  - [📊 Review] → week summary
```

**Pros**:
- Best of both approaches
- Default view serves most common use case
- Other modes available when needed

**Cons**:
- More UI complexity
- Needs clear mental model

## Current Pain Points

**Cluttered right panel**:
- My Planned Recipes (top)
- Additional Context field
- Browse Recipe Ideas / Generate buttons
- Recipe Pitches grid (10 cards)
- Full Recipes (fleshed out)
- Meal Plan section (unused)

**All competing for same vertical space**

## Hypothesis

**Start with Option B (Progressive Disclosure + Cleanup)**:
1. **Collapse by default**: Pitch generation section hidden until clicked
2. **Compact planned recipes**: Show just name + quick actions (expand for details)
3. **Remove unused sections**: "Meal Plan" section (redundant with My Planned Recipes)
4. **Sticky header**: Keep planned recipes visible while scrolling

**Later, add Option D modes** when cooking/review features are built:
- Planning mode (default) = current refined view
- Cooking mode = full-screen recipe with no distractions
- Review mode = week-level analytics

## Architectural Implications

**Frontend considerations**:
- State management across views (if using tabs/modes)
- Routing (if deep-linking to modes)
- Mobile responsiveness (collapsible vs tabs vs modals)

**No backend changes needed** - purely frontend UX

**Risk**: Over-engineering before understanding usage patterns

## Next Steps to Explore

1. **Immediate cleanup** (this week):
   - Remove "Meal Plan" section (redundant)
   - Collapse pitch generation by default
   - Make planned recipes more compact
   - Test if this reduces clutter enough

2. **Track usage patterns** (next 2 weeks):
   - How often do users generate multiple waves?
   - Do they jump between inventory and planning frequently?
   - Where do they get lost/frustrated?

3. **Build modes when needed** (later):
   - Cooking mode when user starts cooking from saved recipes
   - Review mode when week-end metrics become valuable

## Related Questions

- **Ingredient claim visibility** (`ingredient-claim-visibility.md`) - Might inform inventory view design
- **Week planning criteria** - Might add complexity to planning view
