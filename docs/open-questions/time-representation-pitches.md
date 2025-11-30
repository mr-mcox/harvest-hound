# Time Representation in Recipe Pitches

**Discovered**: recipe-pitch-selection experiment, 2025-11-29
**Priority**: Medium (nice to have, not blocking)

## Problem

Currently pitches only show active time. User wants both active AND total time to make informed decisions. Not enough time diversity in current pitches (skewed toward quick meals).

## Questions

**What time information matters for pitch selection?**
- Active time only?
- Active + total time?
- Active + passive time breakdown?
- Total time categorization (quick/medium/leisurely)?

**How should time be displayed?**
- Inline text: "~25 min active, 45 min total"?
- Progressive reveal (hover for breakdown)?
- Visual indicators (icons for quick/medium/long)?
- Quadrant visualization (total time vs passive time)?

**How should diversity be ensured?**
- Mix of time commitments in each generation?
- Explicit quotas (e.g., 3 quick, 4 medium, 3 leisurely)?
- User-specified preferences for this week?
- Let LLM balance naturally with diversity prompt?

**Quadrant visualization idea:**
- X-axis: Total time (15min → 2hrs)
- Y-axis: Passive time (0 → 2hrs)
- Quadrants: Quick active, Quick passive, Long active, Long passive
- Worth the complexity?

## Hypothesis

**Incremental approach:**
1. First: Show both active + total time in pitch cards
2. Test: Does this provide enough info for decisions?
3. If not enough: Try progressive reveal (hover for breakdown)
4. If diversity still lacking: Add explicit time diversity to prompt

**Quadrant visualization:** Defer until we have data showing simple display isn't enough

## Next Experiment

Update RecipePitch schema to include total_time_minutes, display both in UI, see if it's sufficient for decision-making.

## Success Criteria

- User can identify quick weeknight vs leisurely weekend meals from pitches
- Diverse mix of time commitments in each generation (not skewed to quick)
- User feels confident about time investment before fleshing out recipe
