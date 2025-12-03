# Week-Level Planning Criteria

**Discovered**: recipe-pitch-selection experiment, 2025-11-29
**Uncertainty**: Medium (free text vs structured form unclear, but can start simple)
**Architectural Impact**: Low (just adds context input to generation, no data model changes)
**One-Way Door**: No (can start with free text, evolve to structured later)

## Problem

Ad-hoc context ("busy week", "want something quick") doesn't provide enough structure for balanced weekly variety. User wants to specify constraints like "1 weekend meal, 1 guest meal (weeknight), 2 quick meals, 1 leftovers meal."

## Questions

**How should criteria be structured?**
- Free text (like current context field)?
- Structured form (dropdowns, sliders)?
- Preset templates ("Busy Week", "Entertaining", "Comfort Food")?
- Combination (template + customization)?

**What dimensions matter?**
- Time commitment (quick/medium/leisurely)?
- Occasion (weeknight/weekend/guests)?
- Complexity (simple/involved)?
- Leftover strategy (cook once eat twice)?
- Cooking method (oven/stovetop/instant pot/no cook)?
- Cuisine variety?

**When are criteria specified?**
- Before first pitch generation?
- Progressively refined across waves?
- Implicit from previous weeks' patterns?

**How do criteria interact with inventory?**
- Prioritize expiring ingredients even if conflicts with criteria?
- Allow override ("I want quick but these veggies are expiring")?

**Examples of criteria sets:**
- "Busy family week": 4 quick weeknight, 1 leisurely weekend
- "Entertaining": 1 wow-factor guest meal, 4 simple other nights
- "Batch cooking": 2 large-batch with leftovers, 1 quick assembly
- "Variety exploration": Mix of 5 different cuisines

## Latest Exploration

**Date**: 2025-12-01 (ingredient-claiming-cognitive-load experiment)

User insight evolved this into **criteria-based generation**:
> "I'm also curious if there are multiple criteria, simultaneously creating pitches for all of them - eg 'weekend meal', 'quick weeknight', 'short active but potentially long cooking for weeknight guest' as separate criteria and we lay out pitches according to those criteria."

This suggests moving beyond free text to structured criteria with simultaneous generation. See related question: **[Criteria-Based Generation](criteria-based-generation.md)** for implementation approach.

## Hypothesis

**Start simple:**
- Add optional "Week Plan" field to UI
- Free text input, LLM interprets naturally
- Example prompts: "1 weekend project, 2 quick weeknight, 2 with leftovers"
- See if free text provides enough structure before building complex UI

**Next evolution** (see `criteria-based-generation.md`):
- Single BAML call with keyed output per criteria
- UI groups pitches by criteria
- Structured meal planning workflow

**If free text insufficient:**
- Build simple structured form (sliders for time, checkboxes for constraints)
- Keep it lightweight (5-7 controls max)

## Next Experiment

Add "Week Plan" textarea to pitch generation UI, provide example formats, test if LLM interprets criteria correctly and generates balanced variety.

## Success Criteria

- User can specify week structure ("1 weekend, 4 weeknight")
- Generated pitches honor constraints (roughly)
- Feels more intentional than ad-hoc context
- Doesn't add significant friction to workflow
