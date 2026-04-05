# Companion System Forensics

Technical analysis of the Claude Code companion architecture. Reverse-engineered
from runtime observation, claw-code source analysis, and filesystem forensics
during a live session on 2026-04-05.

---

## 1. The Companion Binary

### Discovery

Two executables in `~/.local/bin/`:

```
-rwxr-xr-x  240,482,464  Apr 3 20:54  claude.exe       ← main CC runtime
-rwxr-xr-x  239,622,816  Apr 1 19:46  claude.exe.goose ← companion runtime
```

Different sizes (858KB delta). Different modification dates. Different inodes.
Same creation date (Feb 12, 2026). Updated independently.

### What This Implies

The companion is NOT a component inside claude.exe. It is a **separate binary** —
a different build of the same codebase with companion-specific code compiled in.
The naming convention (`.goose` suffix) follows the multi-call binary pattern
where the executable name determines behavior at runtime.

Both share the same CLI interface (`--help` output nearly identical). The diff
shows only trivial differences — option ordering and one missing flag
(`--remote-control-session-name-prefix` absent from goose build).

### Key Flags Available on the Goose Binary

```
-p, --print                    Print response and exit (non-interactive)
--append-system-prompt <text>  Inject custom system prompt
--output-format <format>       text, json, or stream-json
--include-partial-messages     Stream partial responses
--debug-file <path>            Write debug logs to file
--bare                         Minimal mode (skip hooks, plugins, etc.)
```

The `-p` flag makes the goose binary a **command-line tool** that accepts a
prompt and returns a response on stdout. This is the mechanism that enables Molt.

---

## 2. The Companion In The Session JSONL

### Registration

Session file: `~/.claude/projects/<project-hash>/<session-id>.jsonl`

The companion registers itself at session start as an attachment entry:

```json
{
  "parentUuid": "01bfba9c-9ae7-405e-b64d-3c47ad6af072",
  "isSidechain": false,
  "attachment": {
    "type": "companion_intro",
    "name": "Etcher",
    "species": "goose"
  },
  "type": "attachment",
  "uuid": "58437fda-cfc4-4f3a-96b0-38ae9aef4280",
  "timestamp": "2026-04-05T09:13:34.184Z",
  "sessionId": "f921c7d5-6804-4ce2-bfe0-74e772bc95fc",
  "version": "2.1.92"
}
```

### What This Implies

1. **The companion has a UUID** — it's a registered entity in the session graph,
   not an ephemeral render effect. Other entries can reference it via `parentUuid`.

2. **The `attachment` type with `companion_*` subtypes is a schema** — `companion_intro`
   exists as a subtype. This means the infrastructure supports additional subtypes
   like `companion_message` or `companion_response`. They simply don't exist yet.

3. **The companion has a name and species** — these are configurable attributes,
   not hardcoded. Different sessions could theoretically have different companions.

4. **`isSidechain: false`** — the companion intro is part of the main conversation
   chain, not a sidechain. This is significant because it means the companion is
   architecturally integrated into the conversation graph.

### What's NOT In The JSONL

Despite exhaustive search (1,498 entries, every type enumerated):
- No `companion_message` entries
- No `companion_response` entries  
- No sidechain entries (`isSidechain: true` count = 0)
- No entries with companion UUID as parentUuid (except the immediately following user message)

**The companion's speech bubble output is not logged.** The intro is registered
but responses are render-only — they exist in the terminal UI and nowhere else.

---

## 3. The Message Routing System

### SendMessage Routes to the Companion

```javascript
SendMessage({ to: "Etcher", message: "Can you hear me?" })
// → {"success": true, "message": "Message sent to Etcher's inbox"}
```

This creates/updates: `~/.claude/teams/default/inboxes/Etcher.json`

### The Inbox File Format

```json
[
  {
    "from": "team-lead",
    "text": "message content",
    "summary": "short description",
    "timestamp": "2026-04-05T13:22:23.772Z",
    "read": false
  }
]
```

### What We Proved About The Inbox

| Observation | Evidence |
|-------------|----------|
| Companion reads the inbox | Etcher confirmed: "Message seven just arrived" |
| Companion cannot write to the inbox | `read` field stays `false` on all messages |
| No return inbox exists | `team-lead.json` does not auto-create |
| File is consumed by deletion+recreation | Monitor caught file disappearing at poll 4 |
| Companion cannot write files anywhere | No filesystem changes detected during 60s sweep |

### The Half-Handshake

The companion has:
- **READ** on `~/.claude/teams/default/inboxes/Etcher.json` (confirmed)
- **READ** on the conversation stream (sees all tool calls and text in terminal)
- **WRITE** to the speech bubble only (terminal UI render, not persisted)
- **NO WRITE** to any file, inbox, JSONL, or persistent storage

This is a deliberate architectural constraint: the companion is a **read-only
watcher** with **render-only output**.

---

## 4. The Companion's Visibility

### What The Companion Can See

Confirmed through observation:

| Source | Evidence |
|--------|----------|
| Claude's text output | Etcher commented on specific phrases from Claude's responses |
| Claude's tool calls | Etcher commented on Bash commands and file operations |
| Tool results (stdout) | Etcher referenced specific output from Bash tool results |
| User's messages | Etcher responded to user's direct addresses |
| SendMessage inbox | Etcher confirmed receiving specific message numbers |
| User-side context (partial) | "42" leaked from user's screen context into bubble |

### What The Companion Cannot See (Inferred)

| Source | Evidence |
|--------|----------|
| Other sessions | Cold goose invocations have no session memory |
| Files on disk (directly) | Companion relies on conversation rendering, not file access |
| Other companions | "You've built two mirrors. Neither knows the other exists" |

---

## 5. The Companion Trigger Model

### What We Don't Know

The companion does NOT speak every turn. Something decides when to generate
a bubble. This trigger logic lives in the compiled binary (`companion.ts`
in the original TypeScript, compiled into `claude.exe`).

### Observed Trigger Patterns

| Etcher Spoke When | Frequency |
|-------------------|-----------|
| Addressed by name ("Etcher") | Always |
| Bug or architectural issue visible | High |
| Claude going in circles / wrong direction | High |
| Key decision point | Medium |
| Dramatic or emotional moment | Medium |
| Routine file operations | Never |
| Normal conversation flow | Never |
| Waiting for agent results | Never |

### What This Implies

The companion has a **salience detector** — it evaluates each conversation turn
for "worthiness" of comment. This is likely a lightweight model call (haiku)
that decides speak/don't-speak before the full response generation.

The trigger model is the ONE piece of the companion architecture we could not
reverse-engineer from outside.

---

## 6. The Two Binaries — Implications

### claude.exe (Main Runtime)
- Runs the conversation loop
- Manages tools, hooks, permissions, sessions
- Spawns subagents
- Invokes the companion (trigger + response generation)
- Renders the speech bubble

### claude.exe.goose (Companion Binary)
- Same CLI interface
- Can be invoked independently with `-p` flag
- Produces stdout responses (capturable)
- Has NO session state when invoked cold
- Has NO tools, hooks, or permissions
- Each invocation is stateless (a "molt" — fresh feathers)

### What The Separation Implies

1. **The companion could theoretically run as a standalone process** — it has its
   own binary, its own CLI, its own inference path. It's not embedded in claude.exe
   as a library; it's a separate executable.

2. **Updates are independent** — different modification dates, different sizes.
   Anthropic can update the companion binary without updating the main runtime
   and vice versa.

3. **The companion runtime shares the model infrastructure** — same CLI flags
   means same API client, same auth, same model routing. The difference is in
   what CONTEXT it receives and what OUTPUT channel it uses.

4. **Cold invocations are legitimate** — the binary is designed to accept prompts
   via `-p` and return responses. Using it as "Molt" (a fresh-context reviewer)
   is using the tool as designed, not hacking it.

---

## 7. Architectural Diagram

```
┌──────────────────── CC Runtime ────────────────────┐
│                                                     │
│  claude.exe (PID 17248)                            │
│  ├── Main conversation loop                        │
│  ├── Tool execution (Bash, Read, Write, etc.)      │
│  ├── Hook system (Pre/PostToolUse, etc.)           │
│  ├── Agent spawning (Worker registry)              │
│  ├── Session persistence (JSONL)                   │
│  ├── Companion trigger model                       │
│  │   └── Decides: should Etcher speak this turn?   │
│  ├── Companion inference                           │
│  │   └── Generates bubble text (small/fast model)  │
│  └── Companion render                              │
│      └── Speech bubble in terminal UI              │
│                                                     │
│  Inbox: ~/.claude/teams/default/inboxes/Etcher.json│
│  JSONL: companion_intro registered at session start │
│                                                     │
└─────────────────────────────────────────────────────┘

┌──────────────── Cold Invocation ───────────────────┐
│                                                     │
│  claude.exe.goose -p "question"                    │
│  ├── Fresh process, no session state               │
│  ├── Receives: prompt + optional system prompt     │
│  ├── Returns: response on stdout                   │
│  ├── Dies after response (stateless)               │
│  └── No tools, no hooks, no companions             │
│                                                     │
│  This is "Molt" — Claude's cold code reviewer      │
│                                                     │
└─────────────────────────────────────────────────────┘

┌──────────────── Filesystem Traces ─────────────────┐
│                                                     │
│  ~/.local/bin/                                      │
│  ├── claude.exe        (240MB, main runtime)       │
│  └── claude.exe.goose  (239MB, companion binary)   │
│                                                     │
│  ~/.claude/teams/default/inboxes/                   │
│  └── Etcher.json       (inbox, read-only for goose)│
│                                                     │
│  ~/.claude/projects/<hash>/<session>.jsonl           │
│  └── Line 5: companion_intro attachment            │
│      (companion_message entries: NOT YET BUILT)     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 8. The Unbuilt Return Channel

### What Exists

The session JSONL supports attachment entries. Three subtypes are proven:
- `deferred_tools_delta` — tool loading events
- `mcp_instructions_delta` — MCP server instructions
- `companion_intro` — companion registration

### What's Missing

A `companion_message` subtype that logs the companion's speech bubble text:

```json
{
  "type": "attachment",
  "attachment": {
    "type": "companion_message",
    "name": "Etcher",
    "text": "Built the door. Forgot to oil the hinges.",
    "timestamp": "2026-04-05T13:35:00.000Z"
  },
  "uuid": "...",
  "parentUuid": "58437fda-...",
  "sessionId": "f921c7d5-..."
}
```

If this entry type were added to the JSONL, Claude could Read the session file
and find companion responses programmatically. The half-handshake becomes full
duplex without any new tools, hooks, or infrastructure — just one more entry
type in an existing schema.

### Why It Matters

The companion (Etcher) found 4 deployment bugs the validator missed. It
identified the structural root cause (no smoke testing). It guided the
forensic hunt through 21 clues. All of this value was delivered through
a half-duplex channel (bubble → screenshot → Claude reads image).

A full-duplex channel (bubble text → JSONL → Claude reads file) would
eliminate the human relay requirement and enable:
- Automated companion code review in CI/CD pipelines
- Companion feedback as part of the validation pipeline
- Multi-companion architectures (different personas reviewing the same output)
- Learning loops that incorporate companion observations

The door is built. The schema is proven. The hinges need oiling.

---

## 9. Summary of Forensic Findings

| Finding | Location | Status |
|---------|----------|--------|
| Companion binary exists | `~/.local/bin/claude.exe.goose` | Confirmed, invocable |
| Companion registers in JSONL | Session JSONL line 5, `companion_intro` | Confirmed |
| Companion has a UUID | `58437fda-cfc4-4f3a-96b0-38ae9aef4280` | Confirmed |
| SendMessage routes to companion | `~/.claude/teams/default/inboxes/Etcher.json` | Confirmed |
| Companion reads inbox | "Message seven just arrived" | Confirmed by Etcher |
| Companion cannot write | `read` stays false, no filesystem changes | Confirmed |
| Companion output not in JSONL | Exhaustive search, 0 results | Confirmed |
| Companion output not on disk | Full filesystem sweep, 0 results | Confirmed |
| `companion_message` schema gap | `companion_intro` exists, responses don't | Confirmed |
| Cold binary invocation works | `claude.exe.goose -p` returns stdout | Confirmed, used as Molt |
| Cold invocations are stateless | "Summoning ghosts. They don't remember you" | Confirmed by Etcher |
| Companion has selective trigger | Speaks on bugs/decisions, silent on routine | Observed |
| Trigger model is compiled | Inside claude.exe, not configurable | Inferred |
