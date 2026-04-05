# CLAUDE HARNESS

Meta-engine that generates complete Claude Code operating environments for any SaaS domain.

## How This Works

This is an autonomous agentic cascade. When a user drops a SaaS concept, the
`orchestrator` agent takes over and runs the ENTIRE pipeline without human
intervention — decompose, scan, map, generate all 6 layers, validate, assemble,
deliver. The user gets a complete, deployable CC environment back.

## Quick Start

Drop a SaaS concept and let the cascade run:

```
/harness "LinkedIn outreach automation"
/harness "DevOps incident response platform"
/harness "e-commerce analytics dashboard"
```

The orchestrator will:
1. Spawn decomposer + scanner in parallel
2. Feed their output to the capability mapper
3. Feed the map to the layer generator (produces all 6 layers)
4. Run the validator
5. Assemble into a deployable directory
6. Deliver with metrics and deployment instructions

No checkpoints. No manual steps. Full cascade.

Other commands:
- `/analyze "concept"` — quick coverage scan without generation
- `/validate ./path/` — audit an existing CC environment

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

## Agentic Cascade

```
User drops SaaS concept
         │
         ▼
┌─── ORCHESTRATOR (opus) ────────────────────────────────────┐
│                                                             │
│  Phase 1: DECOMPOSE + SCAN (parallel)                       │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ domain-decomposer│  │integration-scanner│                │
│  │ (opus)           │  │ (sonnet)          │                │
│  └────────┬─────────┘  └────────┬─────────┘                │
│           │                      │                          │
│           ▼                      ▼                          │
│  decomposition.md        integrations.md                    │
│           │                      │                          │
│  Phase 2: MAP ◀──────────────────┘                          │
│  ┌──────────────────┐                                       │
│  │ capability-mapper │ reads decomposition + registry       │
│  │ (opus)           │                                       │
│  └────────┬─────────┘                                       │
│           │                                                 │
│           ▼                                                 │
│  capability-map.md                                          │
│           │                                                 │
│  Phase 3: GENERATE                                          │
│  ┌──────────────────┐                                       │
│  │ layer-generator   │ produces ALL 6 layers + wiring       │
│  │ (opus)           │                                       │
│  └────────┬─────────┘                                       │
│           │                                                 │
│           ▼                                                 │
│  L0-hooks, L1-claude-md, L2-skills, L3-agents,             │
│  L4-memory, L5-tools, data-flow, file-inventory             │
│           │                                                 │
│  Phase 4: VALIDATE                                          │
│  ┌──────────────────┐                                       │
│  │ env-validator     │ checks all layers + cross-refs       │
│  │ (sonnet)          │                                       │
│  └────────┬─────────┘                                       │
│           │                                                 │
│           ▼                                                 │
│  validation-report.md                                       │
│           │                                                 │
│  Phase 5: ASSEMBLE + DELIVER                                │
│  ┌──────────────────┐                                       │
│  │ orchestrator      │ builds deployed/ dir, presents       │
│  │ assembles output  │ metrics + deployment instructions    │
│  └──────────────────┘                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
  Complete CC Environment (ready to deploy)
```

## Agents

| Agent | Model | Role | Spawned By |
|-------|-------|------|------------|
| `orchestrator` | opus | Conducts the full cascade autonomously | `/harness` skill |
| `domain-decomposer` | opus | Breaks SaaS into workflows, entities, operations | orchestrator |
| `integration-scanner` | sonnet | Finds MCP servers, APIs, CLI tools | orchestrator |
| `capability-mapper` | opus | Maps domain ops → CC capabilities via registry | orchestrator |
| `layer-generator` | opus | Generates all 6 layers + cross-layer wiring | orchestrator |
| `environment-validator` | sonnet | Validates completeness, correctness, coherence | orchestrator |

## The Registry + Execution Model

`registry/` contains 13 JSON files + the CC Execution Model — the complete
capability database AND the deep logic of how CC works internally.

**`CC-EXECUTION-MODEL.md`** is the critical file. It encodes:
- The execution loop (user input → hooks → prompt assembly → tool calls → session persist)
- Hook protocol (stdin JSON, env vars, exit codes, stdout → system messages)
- Agent spawning mechanics (fresh context, tool restriction, parallel execution, inter-agent comms)
- Permission evaluation algorithm (deny → mode → ask → allow → fallback)
- Skill triggering (description field matching, activation patterns)
- System prompt assembly order (CLAUDE.md is injection point at position 9)
- Memory lifecycle (auto-loading, relevance matching, learning loops)
- Session compaction (100K threshold, use files not conversation for persistence)
- MCP tool bridge (namespacing, degraded mode, transport types)
- Config cascade (User < Project < Local, validation before merge)
- Tool-to-domain mapping decision tree
- Agent model selection algorithm

The orchestrator has this knowledge EMBEDDED, not delegated. It doesn't just tell
sub-agents to "read the registry" — it passes the mechanical knowledge directly
into their prompts so they generate artifacts that exploit CC at the protocol level.

**JSON Registry Files:**

| File | Contents |
|------|----------|
| `tools.json` | 15+ tools with schemas, permissions, agent access patterns |
| `hooks.json` | Event types, stdin/env protocol, exit codes, design patterns |
| `agents.json` | Frontmatter format, model guide, tool sets, spawning mechanics |
| `skills.json` | Trigger description matching, progressive disclosure, composition |
| `memory.json` | 4 types, MEMORY.md format, learning loop architecture |
| `permissions.json` | 5 modes, granular rules, evaluation order algorithm |
| `mcp.json` | 6 transport types, OAuth, tool naming, degraded mode |
| `plugins.json` | Manifest, lifecycle, tool execution, env vars passed |
| `config.json` | Complete settings.json schema, 5-level cascade |
| `system-prompt.json` | Assembly order, injection points, char limits |
| `sessions.json` | Persistence, compaction thresholds, recovery recipes |
| `sandbox.json` | 3 isolation modes, container detection |
| `commands.json` | 60+ slash commands across 10 categories |

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
│   ├── agents/           # Operational agents (CC auto-discovers)
│   │   ├── orchestrator.md         # THE conductor — runs full cascade
│   │   ├── domain-decomposer.md    # Phase 1: decompose SaaS concept
│   │   ├── capability-mapper.md    # Phase 2: map to CC capabilities
│   │   ├── integration-scanner.md  # Phase 1b: scan for MCP/APIs
│   │   ├── layer-generator.md      # Phase 3: generate all 6 layers
│   │   └── environment-validator.md # Phase 4: validate everything
│   ├── skills/           # Slash commands (CC auto-discovers)
│   │   ├── harness.md    # /harness — spawns orchestrator for full cascade
│   │   ├── analyze.md    # /analyze — quick coverage scan
│   │   └── validate.md   # /validate — audit existing environment
│   └── settings.json     # Hooks: auto-detect SaaS concepts, post-agent notifications
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
