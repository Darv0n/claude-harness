---
description: |
  Use when the user wants to apply extracted exploits to optimize the runtime
  environment. Says "optimize", "apply", "upgrade", "tune", "improve the env",
  "deploy the exploits".
  Examples: "/optimize", "apply the exploit map", "optimize our environment",
  "upgrade the harness based on findings"
---

# /optimize

Apply exploit mappings to optimize the claude-harness runtime environment.

## Steps

1. Read `memory/exploits/exploit-map.md` for the exploit priority list
2. Read current environment state:
   - `.claude/agents/*.md`
   - `.claude/skills/*.md`
   - `.claude/settings.json`
   - `CLAUDE.md`
3. Spawn `optimizer-agent` (sonnet) with:
   - Current environment files
   - Exploit map
   - Instruction to generate optimized artifacts and write changelog
4. When optimization completes, read the changelog
5. Present: changes applied, impact assessments, updated files
6. Ask: "Deploy these optimizations? (This will update the live environment)"
7. If confirmed, copy optimized artifacts to their live locations
8. Suggest: "Run /harden to audit the updated environment"

## Memory
- Reads: `memory/exploits/`, current environment files
- Writes: optimized artifacts to `.claude/` and `CLAUDE.md`
