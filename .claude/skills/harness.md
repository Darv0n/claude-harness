---
description: |
  Use when the user wants to generate a complete Claude Code environment for a SaaS concept.
  Trigger on: "generate environment for", "harness", "build CC environment",
  "create operating system for", "set up Claude Code for", or any SaaS concept description.
  Examples: "/harness LinkedIn outreach automation", "/harness DevOps incident response",
  "build me a CC environment for e-commerce analytics"
---

# /harness [SaaS concept]

Generate a complete Claude Code operating environment autonomously.

## Execution

1. Clean any previous output: delete contents of `engine/output/` if present
2. Spawn the `orchestrator` agent with the user's SaaS concept
3. The orchestrator runs the FULL pipeline autonomously:
   - DECOMPOSE + SCAN (parallel) → domain decomposition + integration scan
   - MAP → capability mapping against the registry
   - GENERATE → all 6 layers (hooks, CLAUDE.md, skills, agents, memory, tools/MCP)
   - VALIDATE → completeness, correctness, cross-layer coherence
   - ASSEMBLE → deployment-ready directory structure
   - DELIVER → present results with metrics and deployment instructions
4. No human checkpoints until final delivery

## Agent Prompt

When spawning the orchestrator, pass it:
- The SaaS concept (user's exact words)
- The absolute path to this project directory (so it can find registry/, templates/, examples/)
- Instruction to run the full cascade without stopping

The orchestrator knows what to do — it reads CLAUDE.md and the registry on boot.
