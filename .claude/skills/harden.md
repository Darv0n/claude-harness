---
description: |
  Use when the user wants to audit and harden the CC environment. Says "harden",
  "audit", "security check", "lock down", "check permissions", "tighten up".
  Examples: "/harden", "audit the environment", "security check",
  "are our permissions too loose?"
---

# /harden

Audit and harden the Claude Code environment for security and minimality.

## Steps

1. Read all environment files:
   - `.claude/settings.json` (permissions, hooks)
   - `.claude/agents/*.md` (tool access)
   - `.claude/skills/*.md` (trigger patterns)
   - `CLAUDE.md` (rules, constraints)
   - `memory/MEMORY.md` (size, structure)
2. Spawn `auditor-agent` (sonnet) with:
   - All environment files
   - The full audit checklist (permissions, hooks, agents, memory, CLAUDE.md)
   - Instruction to write audit report to `memory/analytics/audit-report.md`
3. When audit completes, read the report
4. Present: risk level, findings by severity, recommendations
5. If fixes are available, ask to apply them
6. Suggest: "Run /recon on a new target, or /status for the current dashboard"

## Memory
- Reads: all environment files
- Writes: `memory/analytics/audit-report.md` (project type)
