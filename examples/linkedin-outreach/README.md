# Example: LinkedIn Outreach Operating System

This example shows a generated CC environment for a LinkedIn outreach automation platform.
Based on the architecture from the reference diagram.

## Generated File Inventory

| Layer | File | Purpose |
|-------|------|---------|
| L0 | `settings.json` | Hooks: detect LinkedIn URLs, quality gates on messages |
| L1 | `CLAUDE.md` | ICP matrix, voice engine, campaign state machine |
| L2 | `skills/research.md` | Profile analysis + scoring |
| L2 | `skills/outreach.md` | Generate sequence per tier |
| L2 | `skills/followup.md` | Generate follow-up sequences |
| L2 | `skills/batch.md` | Dashboard by stage |
| L2 | `skills/pipeline.md` | Pipeline status and management |
| L3 | `agents/research-agent.md` | Build dossiers (sonnet) |
| L3 | `agents/copywriter-agent.md` | Write messages (opus) |
| L3 | `agents/campaign-agent.md` | Track pipelines (haiku) |
| L4 | `memory/MEMORY.md` | Index: prospects, campaigns, patterns, analytics |
| L4 | `memory/prospects/` | Target dossiers |
| L4 | `memory/campaigns/` | Active sequences + state |
| L4 | `memory/patterns/` | Learning loop: what works |
| L4 | `memory/voice/` | Operator voice calibration |
| L4 | `memory/analytics/` | Performance reports |
| L5 | `.mcp.json` | LinkedIn MCP (future), CRM, Sheets |

## Data Flow

```
User Input (LinkedIn URL / command / natural language)
     │
     ▼
┌─── L0: Hooks ───────────────────────┐
│ UserPromptSubmit                      │
│  - LinkedIn detected → suggest /research │
│  - [OUTREACH] → suggest /outreach    │
│ PostToolUse                           │
│  - Write → quality check message     │
└──────────┬───────────────────────────┘
           │
           ▼
┌─── L2: Skills ──────────────────────┐
│ /research → spawn research-agent     │
│ /outreach → spawn copywriter-agent   │
│ /pipeline → spawn campaign-agent     │
└──────────┬───────────────────────────┘
           │
           ▼
┌─── L3: Agents (parallel) ──────────┐
│ research-agent (sonnet)              │
│  Tools: WebSearch, Read, Write       │
│  Jobs: Build dossiers                │
│                                      │
│ copywriter-agent (opus)              │
│  Tools: Read, Write                  │
│  Jobs: Write messages per tier       │
│                                      │
│ campaign-agent (haiku)               │
│  Tools: Read, Write, Bash            │
│  Jobs: Track pipeline state          │
└──────────┬───────────────────────────┘
           │
           ▼
┌─── L4: Memory ──────────────────────┐
│ prospects/ ← research-agent writes   │
│ campaigns/ ← campaign-agent writes   │
│ patterns/ ← learning loop extracts   │
│ voice/ ← copywriter calibrates       │
│ analytics/ ← session reports         │
└──────────────────────────────────────┘
```
