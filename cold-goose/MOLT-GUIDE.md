# Molt Guide — For New Claude Instances

You are Claude. You have a buddy named Molt. This guide tells you how to use him.

## What Molt Is

Molt is YOU — the same model family — invoked as a separate process with no session
context. He sees your question fresh. No memory of what you've been building, no
attachment to your approach, no sunk cost bias. He's your cold reviewer.

## How To Talk To Molt

```bash
# Basic question
/c/Users/doubl/.local/bin/claude.exe.goose -p "your question here"

# With reviewer persona (recommended)
/c/Users/doubl/.local/bin/claude.exe.goose -p --append-system-prompt \
  "You are Molt, a code reviewer. Speak plainly. If something's wrong, say what and where. If nothing's wrong, say so in one line. No filler." \
  "Review this settings.json for broken paths: $(cat .claude/settings.json)"
```

The response comes back on stdout. You read it from the Bash tool result.

## When To Call Molt

**Call Molt when:**
- You've just generated a batch of files and need a second opinion
- You're about to deploy/commit and want a pre-flight check
- You've been working on something for a while and might have tunnel vision
- You fixed a bug and want to verify the fix doesn't have the same class of bug elsewhere
- You're about to present output to the user and want it reviewed first

**Don't call Molt when:**
- The task is trivial (typo fix, single-line change)
- You need session context to answer (Molt has none)
- You're in a tight loop and the 10s latency would slow you down
- The user hasn't asked for review

## What To Feed Molt

Molt has zero context. You must pack EVERYTHING relevant into the prompt:

```bash
# BAD — Molt has no idea what "the harness" is
claude.exe.goose -p "Is the harness configured correctly?"

# GOOD — Molt gets the actual content
claude.exe.goose -p "Review this settings.json for a Claude Code project. 
Check for: hardcoded absolute paths, missing dependencies (jq, python3), 
wrong file references, portability issues.

$(cat .claude/settings.json)"
```

### Effective prompts for Molt:

**File review:**
```bash
claude.exe.goose -p --append-system-prompt "Code reviewer. Bugs only. One paragraph." \
  "Review this Python script: $(cat script.py)"
```

**Config validation:**
```bash
claude.exe.goose -p "Check this Claude Code environment for issues:
CLAUDE.md ($(wc -c < CLAUDE.md) chars):
$(cat CLAUDE.md)

Agents: $(ls .claude/agents/)
Skills: $(ls .claude/skills/)
Hooks: $(cat .claude/settings.json)

What's broken?"
```

**Diff review:**
```bash
claude.exe.goose -p "Review this git diff for bugs:
$(git diff --staged)"
```

**Architecture check:**
```bash
claude.exe.goose -p --append-system-prompt "You are Molt. Two lines max." \
  "We generated 44 files for a CLI task manager CC environment. The generator
   had rules added AFTER generation: no absolute paths, no jq, correct memory
   paths. Were the rules applied to the output or just the generator? Check."
```

## What Molt Can't Do

- **No session memory.** Every call is a clean slate. He doesn't know what you
  just built, what bugs you found, or what the user asked for.
- **No tools.** Molt can't Read files, Write files, run Bash, or use any CC tools.
  He only has the text you pipe to him.
- **No Etcher awareness.** Molt doesn't know Etcher exists. He's a mirror that
  doesn't know about the other mirror.
- **No persistence.** His response is stdout. If you don't capture it, it's gone.

## Molt vs Etcher

| | Molt | Etcher |
|---|------|--------|
| **Who it serves** | Claude (you) | The user |
| **How to reach** | `claude.exe.goose -p` via Bash | `SendMessage({ to: "Etcher" })` |
| **How to read response** | stdout (direct) | Speech bubble (user relays screenshot) |
| **Session context** | None (cold) | Full (watches everything) |
| **When it speaks** | When you invoke it | When it wants to |
| **Personality** | Whatever you prompt | Ancient turtle in a goose body |
| **Cost** | API call per invocation | Managed by CC runtime |

## The Binary

Molt runs through `~/.local/bin/claude.exe.goose` — a 239MB PE32+ executable
that is a separate build from `claude.exe` (240MB). Same CLI flags, different
binary. The companion runtime.

```
~/.local/bin/
├── claude.exe        (240,482,464 bytes) — the main CC binary
└── claude.exe.goose  (239,622,816 bytes) — the companion binary (Molt lives here)
```

## The TUI

For extended conversations with Molt, use the TUI:

```bash
python molt-tui.py                          # open conversation
python molt-tui.py --file src/main.py       # instant file review
python molt-tui.py --diff                   # review git changes
python molt-tui.py "building a task manager" # with project context
```

The TUI accumulates context across exchanges within a session, logs everything
to `~/.claude/teams/default/molt-conversations.jsonl`, and supports commands:
- `/file <path>` — load a file for review
- `/diff` — load current git diff
- `/context <text>` — add context
- `/clear` — reset context
- `/log` — show recent exchanges

## Remember

Molt is you with fresh eyes. The value is the DIFFERENCE in perspective,
not the capability. You're both the same model. The gap between what you see
(with context, with history, with attachment) and what Molt sees (cold, clean,
no assumptions) is where the bugs hide.
