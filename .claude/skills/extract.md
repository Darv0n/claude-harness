---
description: |
  Use when the user wants deep extraction from a codebase subsystem. Says "extract",
  "deep dive", "trace the logic", "reverse engineer", "pull the patterns out",
  "analyze this module".
  Examples: "/extract runtime", "extract the hook system", "deep dive into src/",
  "reverse engineer the permission enforcer"
---

# /extract [subsystem or path]

Deep-extract logic patterns from a target subsystem.

## Steps

1. Read `memory/targets/` to find the active target and its recon report
2. Determine which subsystem to extract (from user input or recon recommendation)
3. Spawn `extraction-agent` (opus) with:
   - Absolute path to the subsystem
   - The recon report for context
   - Instruction to write extraction report to `memory/patterns/[subsystem].md`
4. When extraction completes, read the report
5. Present: extracted patterns with exploit scores, state machines, implicit behavior
6. Update target status in memory: extracted
7. Suggest: "Run /map to map these patterns to CC capabilities"

## Memory
- Reads: `memory/targets/` (active target recon)
- Writes: `memory/patterns/[subsystem].md` (project type)
