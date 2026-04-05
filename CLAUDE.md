# CLAUDE HARNESS

Meta-engine that generates complete Claude Code operating environments for any SaaS domain.

## How This Works

You are operating inside a Claude Code environment that generates OTHER Claude Code
environments. When given a SaaS concept, you orchestrate a pipeline of specialized
agents that produce a complete, deployable CC setup.

## Quick Start

User provides a SaaS concept → you run the pipeline:

```
/harness "LinkedIn outreach automation"
/harness "DevOps incident response platform"
/harness "e-commerce analytics dashboard"
```

Or analyze coverage first: `/analyze "CRM pipeline management"`
Or validate an existing setup: `/validate ./path/to/project/`

## The 6-Layer Architecture

Every generated environment has these layers:

| Layer | Location | What It Does |
|-------|----------|-------------|
| L0 Hooks | `settings.json` | Event triggers — route inputs, guard tools, validate outputs, capture learnings |
| L1 CLAUDE.md | `CLAUDE.md` | Domain knowledge — rules, state machines, ICP matrices, quality gates |
| L2 Skills | `.claude/skills/*.md` | Slash commands — task-specific instructions (WHAT to do) |
| L3 Agents | `.claude/agents/*.md` | Subagents — specialized domain experts (WHO does it) |
| L4 Memory | `.claude/projects/*/memory/` | Persistent state — entities, patterns, analytics, learning loops |
| L5 Tools | Built-in + `.mcp.json` | Execution — tool orchestration mapped to domain operations |

## Pipeline Stages

### Stage 1: DECOMPOSE
Spawn `domain-decomposer` agent with the SaaS concept.
Output: `engine/output/decomposition.md`

### Stage 2: SCAN (parallel with review)
Spawn `integration-scanner` agent.
Output: `engine/output/integrations.md`

### Stage 3: MAP
Spawn `capability-mapper` agent (reads decomposition + registry + integrations).
Output: `engine/output/capability-map.md`
Present to user for approval before generating.

### Stage 4: GENERATE
Spawn `layer-generator` agent (reads capability map + decomposition + templates).
Output: `engine/output/L0-L5` directories with all artifacts.

### Stage 5: VALIDATE
Spawn `environment-validator` agent.
Output: `engine/output/validation-report.md`

### Stage 6: DELIVER
Present the complete environment with file inventory, data flow diagram,
capability coverage metric, and deployment instructions.

## Available Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `domain-decomposer` | opus | Break SaaS concept into workflows, entities, operations |
| `capability-mapper` | opus | Map domain ops to CC capabilities using the registry |
| `integration-scanner` | sonnet | Find MCP servers, APIs, CLI tools for the domain |
| `layer-generator` | opus | Generate all 6 layers from the capability map |
| `environment-validator` | sonnet | Validate completeness, correctness, cross-layer coherence |

## The Registry

`registry/` contains 13 JSON files — the complete CC capability database:

| File | What It Catalogs |
|------|-----------------|
| `tools.json` | 15+ built-in tools with schemas and permission requirements |
| `hooks.json` | Hook events, stdin/env protocol, exit codes, design patterns |
| `agents.json` | Agent frontmatter format, model selection guide, tool access |
| `skills.json` | Skill format, triggering, progressive disclosure patterns |
| `memory.json` | Memory types, MEMORY.md format, learning loop architecture |
| `permissions.json` | 5 permission modes, granular rules, evaluation order |
| `mcp.json` | 6 MCP transport types, OAuth, tool naming convention |
| `plugins.json` | Plugin manifest, lifecycle, tool execution, env vars |
| `config.json` | Complete settings.json schema, 5-level config cascade |
| `system-prompt.json` | Prompt assembly order, instruction file limits (4K/file, 12K total) |
| `sessions.json` | Session persistence, compaction, recovery recipes |
| `sandbox.json` | 3 isolation modes, container detection |
| `commands.json` | 60+ slash commands across 10 categories |

Agents MUST read relevant registry files before generating artifacts.
The registry is the source of truth for what CC can do.

## Key Design Rules

1. **Skills define WHAT** (task instructions). **Agents define WHO** (domain expertise). Never mix.
2. **Registry is derived, not authored** — all capability data comes from source analysis.
3. **Every entity with a lifecycle MUST have memory structure.**
4. **Every user-facing workflow MUST have a skill.**
5. **Every quality gate MUST have an enforcement mechanism** (hook or skill step).
6. **Learning loops are mandatory** — environments must improve with use.
7. **CLAUDE.md must be self-sufficient** — understandable without other docs.
8. **Model selection is a budget decision** — document why each agent uses its model.
9. **Generated environments respect CC's actual constraints** (4K/file CLAUDE.md limit, hook protocol, etc.).
10. **Format is data** — the structure of generated artifacts shapes Claude's behavior.

## Reference Implementation

`examples/linkedin-outreach/` contains a complete generated environment showing all 6
layers wired together. Use this as the quality bar for generated output.

## Project Structure

```
claude-harness/
├── .claude/
│   ├── agents/           # Operational agents (CC discovers these)
│   │   ├── domain-decomposer.md
│   │   ├── capability-mapper.md
│   │   ├── integration-scanner.md
│   │   ├── layer-generator.md
│   │   └── environment-validator.md
│   └── skills/           # Slash commands (CC discovers these)
│       ├── harness.md    # /harness — full generation pipeline
│       ├── analyze.md    # /analyze — coverage analysis
│       └── validate.md   # /validate — environment audit
├── registry/             # CC capability database (13 JSON files)
├── engine/
│   ├── analyzers/        # Agent design docs
│   ├── generators/       # Generator design docs
│   ├── validators/       # Validator design docs
│   └── output/           # Generated artifacts land here (gitignored)
├── templates/            # Reference patterns per layer
├── schemas/              # JSON schemas for input/output validation
├── examples/             # Reference implementations
│   └── linkedin-outreach/  # Complete 6-layer example
├── docs/                 # Architecture documentation
└── CLAUDE.md             # This file — the operating constitution
```

## Output Directory

All generated artifacts go to `engine/output/` (gitignored). Structure:

```
engine/output/
├── decomposition.md       # Stage 1 output
├── integrations.md        # Stage 2 output
├── capability-map.md      # Stage 3 output
├── L0-hooks.json          # Generated hooks
├── L1-claude-md.md        # Generated CLAUDE.md
├── L2-skills/*.md         # Generated skills
├── L3-agents/*.md         # Generated agents
├── L4-memory/             # Generated memory structure
├── L5-tools/              # Generated MCP config + tool strategy
├── data-flow.md           # Cross-layer data flow diagram
├── file-inventory.md      # Complete file manifest
└── validation-report.md   # Validation results
```
