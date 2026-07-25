---
feature: import-priority-adjustment
date: 2025-07-25
commit: 36d0094
branch: main
status: implementing
read-when: resuming implementation
---

## Problem

User pastes a CSA delivery list; `ExtractIngredients` infers priorities from perishability. Mostly right, but wrong inferences require navigating to `/inventory` and hunting items in a priority-sorted list that re-sorts on change (documented UX break). The parse-results view — where every inference is visible and nothing is committed — shows priority as a read-only colored label. "LLM suggests, human adjusts" is missing at its highest-leverage moment.

## Not Doing

- Not adding sort to the import page — parse order preserves context, avoids the re-sort-on-change bug
- Not extracting a shared `PrioritySelect` component — let the second use case (purchase-likelihood review) drive extraction
- Not touching the `/inventory` page's priority editing — works, separate concern
- Not changing the backend — `ParsedIngredient` and `InventoryBulkRequest` already carry priority

## Constraints

- Frontend-only change: `inventory/import/+page.svelte`
- Reuse the same dropdown pattern as `/inventory`: click priority text → inline `<select>` → change fires immediately. No separate save button
- Priority mutations happen on `pendingItems` state — no API call until "Approve All"
- Items remain in parse order (no sort by priority)
- Svelte 5 runes only (`$state`, no legacy `$:`)

## Escalation Triggers

- If the dropdown causes unexpected behavior (state desync, item jumping, loss of other fields on mutation), pause
- If adding priority editing reveals that quantity, unit, or portion_size should also be editable at this stage, pause — that's scope creep for this brief
- If any backend change appears necessary, pause — this is a frontend-only pain
- If the interaction pattern doesn't feel right in testing, pause and discuss alternatives before committing

## Decisions

Empty — to be populated during implementation.
