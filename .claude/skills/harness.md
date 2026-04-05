---
description: |
  Use when the user wants to generate a complete Claude Code environment for a SaaS concept.
  Trigger on: "generate environment for", "harness", "build CC environment",
  "create operating system for", "set up Claude Code for", or any SaaS concept description.
  Examples: "/harness LinkedIn outreach automation", "/harness DevOps incident response",
  "build me a CC environment for e-commerce analytics"
---

# /harness [SaaS concept]

Generate a complete Claude Code operating environment for the given SaaS concept.

## Pipeline

Execute these stages in order using the Agent tool:

### Stage 1: DECOMPOSE + SCAN (parallel)
Spawn TWO agents simultaneously:
1. `domain-decomposer` — pass the SaaS concept description. Tell it to read the registry
   files and write output to `engine/output/decomposition.md`.
2. `integration-scanner` — pass the SaaS concept. Tell it to write output to
   `engine/output/integrations.md`.

Wait for both. Present the decomposition to the user for review.

### Stage 2: MAP
After user approves decomposition, spawn `capability-mapper`. Tell it:
- Read `engine/output/decomposition.md` and `engine/output/integrations.md`
- Read all `registry/*.json` files for CC capabilities
- Write output to `engine/output/capability-map.md`

Present the capability map. This is the blueprint — get user approval.

### Stage 3: GENERATE
Spawn `layer-generator`. Tell it:
- Read `engine/output/capability-map.md` and `engine/output/decomposition.md`
- Read all `registry/*.json` files and `templates/` directory
- Study `examples/linkedin-outreach/` as the quality reference
- Generate ALL 6 layers to `engine/output/` subdirectories
- Wire cross-layer references and generate data flow diagram

### Stage 4: VALIDATE
Spawn `environment-validator`. Tell it:
- Read all generated artifacts in `engine/output/`
- Read `registry/*.json` for constraint validation
- Write validation report to `engine/output/validation-report.md`

### Stage 5: DELIVER
Read the validation report. If READY:
1. Present complete file inventory with layer assignments
2. Show the data flow diagram
3. Report capability coverage metric
4. Ask if user wants to deploy to a target project directory

If NEEDS_WORK:
1. Present specific issues
2. Ask user how to proceed (fix and regenerate, or accept as-is)

## Deploying Generated Environments

When user provides a target directory:
1. Create `.claude/agents/` and `.claude/skills/` directories in target
2. Copy generated agents, skills, and memory structure
3. Write the generated CLAUDE.md to target root
4. Write settings.json with hooks
5. Write .mcp.json if MCP servers are needed
6. Report what was deployed
