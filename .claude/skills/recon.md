---
description: |
  Use when the user drops a repository URL, mentions a codebase to analyze, says
  "recon", "scan this repo", "map the structure", "analyze this codebase", or
  provides a GitHub/GitLab link.
  Examples: "/recon https://github.com/org/repo", "scan this codebase",
  "what's the attack surface of this repo", "map the structure"
---

# /recon [URL or path]

Run a full reconnaissance sweep on a target codebase.

## Steps

1. Determine target: URL (clone it) or local path (use directly)
2. If URL: `git clone --depth 1` to `targets/[repo-name]/` via Bash
3. Spawn `recon-agent` with:
   - Target path (absolute)
   - Instruction to write recon report to `memory/targets/[name].md`
4. When recon completes, read the report
5. Present: surface area stats, architecture overview, recommended extraction order
6. Auto-save target to memory with status: recon'd
7. Suggest: "Run /extract [subsystem] to deep-dive the highest-value subsystem"

## Memory
- Writes: `memory/targets/[name].md` (project type)
