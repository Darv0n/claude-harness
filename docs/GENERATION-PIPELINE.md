# Generation Pipeline

## Overview

The pipeline transforms a natural language SaaS concept into a complete Claude Code
operating environment. It runs as a sequence of agent-driven stages.

## Stages

### Stage 1: DECOMPOSE

**Agent:** domain-decomposer
**Input:** SaaS concept (natural language) + optional structured input (harness-input.json)
**Output:** Domain decomposition document

Breaks the SaaS concept into:
- **Workflows** — ordered sequences of operations (e.g., "prospect research → scoring → outreach")
- **Entities** — domain objects that must be tracked (e.g., "prospects", "campaigns", "sequences")
- **Operations** — atomic actions the system performs (e.g., "search web", "write message", "update score")
- **Triggers** — events that initiate workflows (e.g., "LinkedIn URL pasted", "timer fires")
- **Quality criteria** — what makes output "good" in this domain
- **State transitions** — how entities move through lifecycle stages

### Stage 2: MAP

**Agent:** capability-mapper
**Input:** Domain decomposition + CC capability registry
**Output:** Capability mapping document

Maps every domain operation to CC capabilities:
- Operations → Tools (which built-in or MCP tools execute each operation)
- Workflows → Skills (which workflows become slash commands)
- Entities → Memory types (which entities persist across sessions)
- Triggers → Hooks (which events become settings.json hooks)
- Domain expertise → Agents (which specializations need dedicated agents)
- Rules → CLAUDE.md sections (which domain knowledge goes in the constitution)

### Stage 3: GENERATE (6 parallel generators)

Each generator takes the capability mapping and produces one layer's artifacts.

#### L0 Hook Generator
- Reads: triggers, quality criteria
- Produces: `settings.json` hooks section
- Key decisions: which events to intercept, what to route where

#### L1 CLAUDE.md Generator
- Reads: full decomposition, rules, entities, state transitions
- Produces: Complete CLAUDE.md with domain knowledge, state machines, ICP matrices
- Key decisions: what to front-load vs. defer to skills/agents

#### L2 Skill Generator
- Reads: workflows, operations, quality criteria
- Produces: `skills/*.md` files
- Key decisions: granularity (one skill per workflow vs. composable micro-skills)

#### L3 Agent Generator
- Reads: domain expertise areas, operations, cost constraints
- Produces: `agents/*.md` files
- Key decisions: model selection (opus/sonnet/haiku), tool access, specialization boundaries

#### L4 Memory Generator
- Reads: entities, state transitions, learning patterns
- Produces: MEMORY.md + initial memory file structure
- Key decisions: what persists, learning loop design, analytics structure

#### L5 Tool/MCP Generator
- Reads: operations, integrations
- Produces: `.mcp.json` + tool orchestration strategy document
- Key decisions: which operations need MCP servers vs. built-in tools

### Stage 4: WEAVE

**Agent:** integration-weaver
**Input:** All 6 layer outputs
**Output:** Wired environment with explicit cross-references

Connects the layers:
- Skills reference agents they spawn
- Agents reference memory files they read/write
- Hooks reference skills they suggest
- CLAUDE.md references all other layers
- Memory structure references entities from all workflows
- Data flow diagram generated

### Stage 5: VALIDATE

**Agent:** environment-validator
**Input:** Complete wired environment
**Output:** Validation report + corrected environment

Checks:
- **Completeness** — every workflow has a skill, every entity has memory, every trigger has a hook
- **Correctness** — tool names are valid, model names are valid, file paths are consistent
- **Coherence** — cross-layer references resolve, no orphaned artifacts
- **Coverage** — capability utilization metric calculated
- **Self-documentation** — CLAUDE.md alone is sufficient to understand the environment

## Pipeline Execution

```
┌──────────┐     ┌──────────┐     ┌──────────────────────────────────┐
│ DECOMPOSE│────▶│   MAP    │────▶│          GENERATE                │
│ (serial) │     │ (serial) │     │  ┌────┐┌────┐┌────┐┌────┐┌────┐ │
└──────────┘     └──────────┘     │  │ L0 ││ L1 ││ L2 ││ L3 ││ L4 │ │
                                  │  └────┘└────┘└────┘└────┘└────┘ │
                                  │  ┌────┐                          │
                                  │  │ L5 │  (all parallel)         │
                                  │  └────┘                          │
                                  └───────────────┬──────────────────┘
                                                  │
                                  ┌───────────────▼──────────────────┐
                                  │           WEAVE                   │
                                  │         (serial)                  │
                                  └───────────────┬──────────────────┘
                                                  │
                                  ┌───────────────▼──────────────────┐
                                  │          VALIDATE                 │
                                  │         (serial)                  │
                                  └──────────────────────────────────┘
```

## Invocation

The pipeline is invoked via the `/harness` skill, which orchestrates all stages.
Each stage is implemented as a custom agent that reads the registry and templates.
