# CLAUDE HARNESS Architecture

## System Overview

CLAUDE HARNESS is a meta-engine. It generates Claude Code operating environments.

```
┌─────────────────────────────────────────────────────────┐
│                    CLAUDE HARNESS                        │
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────┐   │
│  │ Registry │───▶│  Engine  │───▶│ Generated Output │   │
│  │ (what CC │    │ (how to  │    │ (complete CC env │   │
│  │  can do) │    │  apply)  │    │  for a SaaS)     │   │
│  └──────────┘    └──────────┘    └──────────────────┘   │
│       ▲               │                                  │
│       │               ▼                                  │
│  ┌──────────┐    ┌──────────┐                           │
│  │claw-code │    │Templates │                           │
│  │ (source) │    │(patterns)│                           │
│  └──────────┘    └──────────┘                           │
└─────────────────────────────────────────────────────────┘
```

## The Three Pillars

### 1. Registry (Knowledge)
**What:** Machine-readable catalog of every CC capability.
**Source:** Extracted from claw-code source analysis.
**Format:** JSON files in `registry/`.

The registry answers: "What can Claude Code do?"

Every entry includes:
- Name and description
- Schema (parameters, types, constraints)
- Source location (file, line number)
- Relationships (what it interacts with)
- Examples (real usage patterns)

### 2. Engine (Intelligence)
**What:** Agent swarm that analyzes a domain and generates CC environments.
**Location:** `engine/` subdirectories.
**Format:** Markdown agent/skill definitions.

The engine answers: "How should CC capabilities be applied to THIS domain?"

Pipeline stages:
1. **Decompose** — Break the SaaS concept into workflows, entities, operations
2. **Map** — Match domain operations to CC capabilities using the registry
3. **Generate** — Produce each layer's artifacts (6 generators, parallelizable)
4. **Weave** — Wire cross-layer dependencies (hooks trigger skills, skills spawn agents, agents read/write memory)
5. **Validate** — Verify completeness, correctness, and coherence

### 3. Templates (Structure)
**What:** Reference patterns for each layer.
**Location:** `templates/`.
**Format:** Markdown/JSON with `{{placeholder}}` syntax.

Templates answer: "What does a well-formed CC artifact look like?"

## Layer Interaction Model

```
L0 Hooks ──────────▶ Trigger routing decisions
    │                    │
    ▼                    ▼
L1 CLAUDE.md ────────▶ Provides domain knowledge + rules
    │                    │
    ▼                    ▼
L2 Skills ───────────▶ Execute specific tasks
    │                    │
    ▼                    ▼
L3 Agents ───────────▶ Specialized execution (parallel)
    │                    │
    ▼                    ▼
L4 Memory ───────────▶ Persist state + accumulate patterns
    │                    │
    ▼                    ▼
L5 Tools ────────────▶ Actual operations (read, write, search, fetch)
```

### Cross-Layer Data Flows

| From | To | Mechanism | Example |
|------|----|-----------|---------|
| L0 → L2 | Hook output suggests skill | Hook echoes `/research` suggestion | "Consider using /research first" |
| L1 → L3 | CLAUDE.md rules constrain agents | Agent reads domain rules from context | ICP matrix determines research depth |
| L2 → L3 | Skill spawns agent | Skill uses Agent tool | /outreach spawns research-agent |
| L3 → L4 | Agent writes to memory | Agent uses Write tool on memory dir | Research agent saves dossier |
| L4 → L2 | Skill reads memory state | Skill reads memory for context | /followup reads campaign state |
| L3 → L3 | Agent spawns agent | Parallel agent execution | Research spawns sub-researchers |

## Capability Coverage Metric

A generated environment's quality is measured by **capability coverage** — the ratio
of CC capabilities meaningfully utilized to the total available. Higher is not always
better. The goal is **maximal relevant utilization**, not exhaustive application.

```
Coverage = (capabilities_used / capabilities_available) * relevance_weight
```

Where `relevance_weight` penalizes capabilities that are forced rather than natural fits.

## Design Constraints

1. **Registry is derived, never authored** — All capability data comes from claw-code analysis
2. **Templates are patterns, not content** — They define structure, generators fill in domain specifics
3. **Engine agents specialize** — Each generator owns exactly one layer
4. **Cross-layer wiring is explicit** — The weaver stage makes all inter-layer references concrete
5. **Output is self-documenting** — The generated CLAUDE.md must make the environment understandable without external docs
6. **Dogfooding** — This project IS a CC environment. It uses the same patterns it generates.
