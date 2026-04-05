---
description: |
  Use when the user wants to see campaign status, pipeline dashboard, track outreach progress,
  or check which prospects need follow-up.
  Examples: "/pipeline", "show me the dashboard", "campaign status",
  "which prospects need follow-up?", "pipeline overview"
---

# /pipeline

## What This Does
Displays a pipeline dashboard showing all prospects by campaign stage, with metrics and action items.

## Steps

1. **Spawn campaign-agent** — delegate to the operations tracker
   - Agent reads all files in `memory/campaigns/`
   - Produces pipeline dashboard with stage counts and metrics
2. **Enhance with actions** — for each flagged item:
   - Stale campaigns (7+ days no activity) → suggest `/followup`
   - Researched but not sequenced → suggest `/outreach`
   - High conversion patterns → highlight in patterns section
3. **Present dashboard** — show the formatted pipeline view
4. **Update analytics** — write session metrics to `memory/analytics/`

## Memory
- Reads: `memory/campaigns/`, `memory/prospects/`
- Writes: `memory/analytics/weekly-report.md`
