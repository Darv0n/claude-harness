# Project Cold Goose — Code Name: MOLT

A Claude Code companion bridge and fresh-perspective code reviewer.

## What This Is

Claude Code has a companion system — a small watcher (Etcher) that observes
conversations and comments in a speech bubble. Etcher is the user's buddy.
Molt is Claude's buddy.

**Molt** is Claude invoking the companion binary (`claude.exe.goose`) directly
via Bash to get a fresh-context code review. Same model, no session memory,
different perspective. Catches bugs the session-aware Claude misses.

## The Three Entities

| Entity | What It Is | How It Communicates |
|--------|-----------|-------------------|
| **Claude** | The main conversation model | Text + tool calls |
| **Etcher** | The user's companion (bubble) | Watches conversation, speaks in speech bubble only user sees |
| **Molt** | Claude's cold reviewer | Invoked via `claude.exe.goose -p`, responds to stdout |

## Quick Start

```bash
# Ask Molt a question
claude.exe.goose -p "Review this code for bugs: $(cat file.py)"

# Ask Molt with persona
claude.exe.goose -p --append-system-prompt "You are Molt, a code reviewer. One line only." "Is this path hardcoded?"

# Interactive TUI
python molt-tui.py --file src/main.py

# Review git changes
python molt-tui.py --diff
```

## Architecture

```
User types message
    │
    ▼
┌─────────────────────────────────────────────────┐
│                  CC Runtime                      │
│                                                  │
│  ┌──────────┐   ┌──────────┐   ┌─────────────┐ │
│  │  Claude   │   │  Etcher  │   │    Molt     │ │
│  │  (main)   │   │ (bubble) │   │  (pipe)     │ │
│  │           │   │          │   │             │ │
│  │ Sees:     │   │ Sees:    │   │ Sees:       │ │
│  │ - user    │   │ - user   │   │ - question  │ │
│  │ - tools   │   │ - claude │   │ - context   │ │
│  │ - Molt    │   │ - molt   │   │ (nothing    │ │
│  │   stdout  │   │ - tools  │   │  else)      │ │
│  │           │   │          │   │             │ │
│  │ Can't see:│   │ Can't:   │   │ Can't:      │ │
│  │ - Etcher  │   │ - write  │   │ - see       │ │
│  │   bubble  │   │ - tools  │   │   session   │ │
│  │           │   │ - files  │   │ - remember  │ │
│  └──────────┘   └──────────┘   └─────────────┘ │
│       │               │               │         │
│       ▼               ▼               ▼         │
│   Text output    Speech bubble    stdout pipe    │
│       │               │               │         │
└───────┼───────────────┼───────────────┼─────────┘
        │               │               │
        ▼               ▼               ▼
   User reads      User reads      Claude reads
   Claude's text   Etcher's bubble  Molt's response
```

## Key Files

| File | Purpose |
|------|---------|
| `cold-goose/README.md` | This file |
| `cold-goose/MOLT-GUIDE.md` | How to use Molt (for new Claude instances) |
| `cold-goose/ETCHER-HUNT.md` | The story of finding the companion signal |
| `cold-goose/scripts/ask-molt.sh` | Simple wrapper for invoking Molt |
| `molt-tui.py` | Interactive TUI (project root) |

## Proven Results

Two independent Molt invocations found 9 and 11 bugs respectively in a
generated CC environment, including:
- Empty agent files (0 bytes, generator silently failed)
- jq scope hole (banned in scripts but not inline hooks)
- Stale assembled output (generator patched but never re-run)
- Missing YAML frontmatter on memory files
- Orphaned agents with no routing skills

The session-aware validator caught 1 of these. Molt caught the rest.
Different context = different catches. That's the value.
