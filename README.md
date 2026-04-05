# CLAUDE HARNESS

A meta-engine that analyzes Claude Code's full capability surface and generates
complete CC operating environments for any SaaS domain.

## What This Does

Given a SaaS concept (e.g., "LinkedIn outreach automation", "e-commerce analytics",
"DevOps incident response"), CLAUDE HARNESS generates a production-ready Claude Code
environment across all 6 architectural layers:

| Layer | Location | Purpose |
|-------|----------|---------|
| L0: Hooks | `settings.json` | Event-driven triggers (PreToolUse, PostToolUse, UserPromptSubmit, Stop) |
| L1: CLAUDE.md | `CLAUDE.md` | Domain knowledge, ICP matrices, quality gates, state machines |
| L2: Skills | `~/.claude/skills/*.md` | Task-specific slash commands with progressive disclosure |
| L3: Agents | `~/.claude/agents/*.md` | Specialized subagents with model selection and tool access |
| L4: Memory | `~/.claude/projects/*/memory/` | Persistent state, learning loops, analytics, patterns |
| L5: Tools | Built-in + MCP | Tool orchestration strategy mapped to domain operations |

## Architecture

```
claude-harness/
├── registry/                  # CC capability registry (extracted from source)
│   ├── tools.json             # All 38+ built-in tools with schemas
│   ├── hooks.json             # Hook types, triggers, config format
│   ├── agents.json            # Agent frontmatter, model options, isolation
│   ├── skills.json            # Skill format, triggering, disclosure patterns
│   ├── memory.json            # Memory types, MEMORY.md format, lifecycle
│   ├── permissions.json       # Permission modes and enforcement
│   ├── mcp.json               # MCP server integration patterns
│   └── system-prompt.json     # Prompt assembly order and injection points
│
├── engine/                    # Generation engine
│   ├── analyzers/             # Domain analysis (decompose SaaS into CC patterns)
│   │   ├── domain-decomposer.md    # Break SaaS into workflows, entities, operations
│   │   ├── capability-mapper.md    # Map domain ops to CC capabilities
│   │   └── integration-scanner.md  # Identify external service touchpoints
│   ├── generators/            # Layer-specific generators
│   │   ├── hook-generator.md       # Generate settings.json hooks
│   │   ├── claude-md-generator.md  # Generate CLAUDE.md with domain knowledge
│   │   ├── skill-generator.md      # Generate skill files
│   │   ├── agent-generator.md      # Generate agent definitions
│   │   ├── memory-generator.md     # Generate memory structure
│   │   └── mcp-generator.md        # Generate MCP configurations
│   └── validators/            # Validate generated environments
│       ├── layer-validator.md      # Validate each layer independently
│       └── integration-validator.md # Validate cross-layer interactions
│
├── templates/                 # Reference templates per layer
│   ├── hooks/                 # Hook configuration templates
│   ├── agents/                # Agent definition templates
│   ├── skills/                # Skill file templates
│   ├── memory/                # Memory structure templates
│   ├── claude-md/             # CLAUDE.md section templates
│   └── mcp/                   # MCP server config templates
│
├── schemas/                   # JSON schemas for all artifacts
│   ├── harness-input.json     # Input schema (SaaS description)
│   ├── harness-output.json    # Output schema (generated environment)
│   └── layer-schemas/         # Per-layer validation schemas
│
├── docs/                      # Architecture documentation
│   ├── ARCHITECTURE.md        # System design
│   ├── LAYER-REFERENCE.md     # Detailed layer-by-layer reference
│   └── GENERATION-PIPELINE.md # How the engine works
│
├── examples/                  # Example generated environments
│   └── .claude/               # Example output structure
│
└── CLAUDE.md                  # This project's own CC instructions
```

## How It Works

```
SaaS Concept (natural language)
        │
        ▼
┌─────────────────────┐
│  Domain Decomposer  │  Break into workflows, entities, operations
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Capability Mapper   │  Map operations → CC capabilities
└────────┬────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Layer Generators (parallel)      │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌────────┐ │
│  │Hooks │ │Skills│ │Agents│ │CLAUDE.md│ │
│  └──────┘ └──────┘ └──────┘ └────────┘ │
│  ┌──────┐ ┌──────┐                      │
│  │Memory│ │ MCP  │                      │
│  └──────┘ └──────┘                      │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────┐
│  Integration Weaver  │  Wire cross-layer dependencies
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│    Validator Suite    │  Validate completeness + correctness
└────────┬────────────┘
         │
         ▼
    Generated CC Environment
    (ready to deploy)
```

## The Registry

The capability registry (`registry/`) is extracted directly from the Claude Code
source code (claw-code). It contains the complete, machine-readable specification
of every tool, hook type, agent pattern, skill format, memory type, and configuration
option available in Claude Code. This is the engine's knowledge base.

## Usage

```
# From within this project directory with Claude Code:

# Generate a CC environment for a SaaS concept
/harness "LinkedIn outreach automation platform"

# Generate with specific focus areas
/harness "DevOps incident response" --focus agents,hooks,memory

# Validate an existing CC environment
/validate ./path/to/project/.claude/

# Show capability coverage for a domain
/analyze "e-commerce analytics dashboard"
```

## Built With

- Claude Code (the tool this project generates environments for)
- Source analysis of [claw-code](https://github.com/ultraworkers/claw-code)
- Zero external dependencies — pure CC-native architecture
