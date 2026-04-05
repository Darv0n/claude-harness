---
description: |
  Use when the user wants to generate an outreach message sequence for a prospect.
  Requires the prospect to have a dossier (run /research first).
  Examples: "/outreach John Smith", "write outreach for this prospect",
  "generate a sequence", "compose messages for the whale tier lead"
---

# /outreach [prospect name]

## What This Does
Generates a personalized outreach message sequence based on the prospect's dossier and ICP tier.

## Steps

1. **Load dossier** — read `memory/prospects/{name-slug}.md`
   - If no dossier exists, tell user to run `/research` first
2. **Determine sequence length** — from ICP tier:
   - Whale: 5 touches
   - High: 4 touches
   - Mid: 3 touches
   - Low: 2 touches
3. **Read voice patterns** — check `memory/voice/` and `memory/patterns/` for calibration
4. **Spawn copywriter-agent** — delegate sequence generation
   - Pass: dossier, ICP tier, sequence length, voice calibration
   - Agent produces: personalized message sequence
5. **Quality gates** (all must pass):
   - [ ] Language matches prospect's communication style
   - [ ] Zero template energy — feels hand-written
   - [ ] Specific details referenced (min 1 per message)
   - [ ] First 2 lines hook on mobile preview
   - [ ] No banned phrases
6. **Save sequence** — write to `memory/campaigns/{name-slug}.md` with status SEQUENCED
7. **Present** — show all messages with quality gate results

## Memory
- Reads: `memory/prospects/`, `memory/voice/`, `memory/patterns/`
- Writes: `memory/campaigns/{name-slug}.md`
