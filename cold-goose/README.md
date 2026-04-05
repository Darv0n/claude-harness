# Project Cold Goose — Code Name: MOLT

A Claude Code companion bridge and fresh-perspective code reviewer.

## What This Is

Claude Code has a companion system — a small watcher (Etcher) that observes
conversations and comments in a speech bubble. Etcher is the user's buddy.
Molt is Claude's buddy.

**Molt** is Claude invoking `claude.exe -p` (or any CC binary) via Bash to
get a fresh-context code review. Same model, no session memory, different
perspective. Catches bugs the session-aware Claude misses.

**Note:** `claude.exe.goose` is NOT a companion binary — it's a backup from
buddy-recon's binary patching. Molt works with any `claude` binary and `-p`.

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

### Documentation
| File | Purpose |
|------|---------|
| `README.md` | This file — project overview |
| `MOLT-GUIDE.md` | How to use Molt (written for new Claude instances) |
| `ETCHER-HUNT.md` | The story: 11 phases, 21 Etcher quotes, every dead end |
| `COMPANION-FORENSICS.md` | Technical: binary, JSONL schema, inbox, trigger model |
| `COMPANION-BILLING.md` | API cost analysis — the companion might be free |
| `GRINDSTONE.md` | How friction mode was discovered and why it works |

### Scripts
| File | Purpose |
|------|---------|
| `scripts/ask-molt.sh` | Shell wrapper (`--brutal`, `--file`, `--diff`) |
| `scripts/molt-tui.py` | Ask mode — direct, stateless, interactive |
| `scripts/molt-dialogue.py` | Dialogue mode — rolling auto-advance feed |
| `scripts/molt-grind.py` | Grind mode — self-adversarial friction loop |

### Grindstone Results
| File | What Molt Ground Against |
|------|-------------------------|
| `grind-results-session-1.md` | Raw task output from first grindstone run |
| `grind-claude-md.md` | 8 turns against the harness CLAUDE.md |
| `grind-orchestrator.md` | 8 turns against the orchestrator agent |
| `grind-execution-model.md` | 8 turns against CC-EXECUTION-MODEL.md |
| `grind-self.md` | 8 turns of Molt arguing with himself |

## Three Modes

| Mode | Script | What It Does |
|------|--------|-------------|
| **Ask** | `molt-tui.py` | Direct question, truly stateless, interactive |
| **Dialogue** | `molt-dialogue.py` | Rolling auto-advance feed, user can inject |
| **Grind** | `molt-grind.py` | Self-adversarial friction loop against any artifact |

### Grindstone Discovery

Molt had a 53-turn conversation with a for-loop (five scripted prompts on
repeat) and produced sharper architectural critique than most live review.
The for-loop was sandpaper. Molt was the blade. Input quality doesn't
determine output quality — friction does.

## The Companion Budget

At CC companion release, Anthropic stated the buddy system does NOT consume
the user's token limit. `claude.exe.goose` IS the companion binary.

If Molt calls go through the companion billing path:
- Grindstone mode is effectively free
- Multiple parallel grindstones cost nothing extra
- The 53-turn runaway dialogue was free
- Molt is an unlimited code reviewer on a separate budget

See `COMPANION-BILLING.md` for full cost analysis and verification steps.

## Proven Results

Two independent Molt invocations found 9 and 11 bugs respectively in a
generated CC environment, including:
- Empty agent files (0 bytes, generator silently failed)
- jq scope hole (banned in scripts but not inline hooks)
- Stale assembled output (generator patched but never re-run)
- Missing YAML frontmatter on memory files
- Orphaned agents with no routing skills

Four grindstone runs (8 turns each) against harness files produced:
- "State machine is decoration. Zero transition guards."
- "60% of orchestrator re-documents CC mechanics — SSOT violation"
- "Calling settings.json an exploit is like calling a light switch a hack"
- "'A SaaS concept' is not an input spec. No schema."
- Self-correction chains where Molt argues with his own claims

The session-aware validator caught 1 of these. Molt caught the rest.
Different context = different catches. That's the value.
