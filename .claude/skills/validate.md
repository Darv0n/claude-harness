---
description: |
  Use when the user wants to validate an existing Claude Code environment.
  Checks structure, completeness, cross-layer coherence, and capability utilization.
  Trigger on: "validate environment", "check my CC setup", "audit", "validate"
  Examples: "/validate ./my-project/", "check if my CC environment is complete"
---

# /validate [path]

Audit an existing Claude Code environment.

## Steps

1. Get target directory from user (default: current directory)
2. Scan for CC artifacts:
   - `settings.json` or `.claude/settings.json` → L0 Hooks
   - `CLAUDE.md` → L1 Instructions
   - `.claude/skills/*.md` → L2 Skills
   - `.claude/agents/*.md` → L3 Agents
   - Memory directories → L4 Memory
   - `.mcp.json` → L5 MCP
3. Read each found artifact
4. Spawn `environment-validator` — pass all found artifacts and tell it to:
   - Read `registry/*.json` for constraint validation
   - Check per-layer format compliance
   - Check cross-layer reference resolution
   - Calculate capability coverage
5. Present findings:
   - Layer-by-layer health (present / missing / issues)
   - Cross-layer coherence score
   - Capability coverage metric
   - Specific improvement recommendations
   - Missing opportunities (unused CC capabilities that fit the domain)
