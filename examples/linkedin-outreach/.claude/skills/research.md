---
description: |
  Use when the user provides a LinkedIn URL, asks to "research" a prospect,
  wants to "build a dossier", or needs ICP scoring on a person.
  Examples: "/research https://linkedin.com/in/someone", "research this prospect",
  "build a dossier on John Smith", "score this lead"
---

# /research [LinkedIn URL or name]

## What This Does
Researches a prospect and builds a comprehensive dossier with ICP scoring.

## Steps

1. **Extract input** — get the LinkedIn URL or name from user input
2. **Spawn research-agent** — delegate to the research specialist
   - Pass the URL/name as the research target
   - Agent will: search web, analyze profile, detect communication style, score ICP
3. **Review dossier** — read the agent's output from `memory/prospects/`
4. **Quality check**:
   - [ ] ICP score has reasoning (not just a number)
   - [ ] Communication style is detected (formal/casual/technical/executive)
   - [ ] At least 3 engagement hooks identified
   - [ ] Company intel is current (check dates on news/funding)
5. **Present dossier** — show the prospect summary with ICP tier and recommended approach
6. **Suggest next step** — based on ICP tier, suggest `/outreach [name]`

## Memory
- Writes: `memory/prospects/{name-slug}.md`
- Reads: `memory/patterns/` (if prior research patterns exist)
