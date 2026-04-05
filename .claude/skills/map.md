---
description: |
  Use when the user wants to map extracted patterns to CC capabilities. Says "map",
  "find exploits", "what CC capabilities apply", "map to claude code",
  "capability mapping", "exploit analysis".
  Examples: "/map", "map these patterns to CC", "what can we exploit",
  "show me the capability mapping"
---

# /map

Map extracted patterns to Claude Code capabilities and score exploit potential.

## Steps

1. Read all extraction reports from `memory/patterns/`
2. Read CC registry files from `registry/` (tools, hooks, agents, skills, memory, etc.)
3. Spawn `mapping-agent` (opus) with:
   - All extraction reports
   - Registry file paths
   - Instruction to write exploit map to `memory/exploits/exploit-map.md`
4. When mapping completes, read the exploit map
5. Present: pattern→CC mappings, coverage matrix, gaps, unused capabilities, priority list
6. Suggest: "Run /optimize to apply the highest-value exploits to the runtime environment"

## Memory
- Reads: `memory/patterns/`, `registry/`
- Writes: `memory/exploits/exploit-map.md` (project type)
