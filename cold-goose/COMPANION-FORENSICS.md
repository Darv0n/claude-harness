# Companion System Forensics

Technical analysis of the Claude Code companion architecture. Reverse-engineered
from runtime observation, claw-code source analysis, and filesystem forensics
during a live session on 2026-04-05.

**CORRECTION (late session discovery):** The `claude.exe.goose` file is NOT a
companion binary. It is a pre-patch backup created by the buddy-recon toolkit
during the FR() merge flip. See section 1 for details.

---

## 1. The claude.exe.goose File — CORRECTED

### What We Thought

Two executables in `~/.local/bin/`. We believed `claude.exe.goose` was a
separate companion binary — a different build with buddy-specific code.

### What It Actually Is

`claude.exe.goose` is the **original unpatched claude.exe**, renamed by
the buddy-recon toolkit's `swap.ps1`:

```powershell
# From buddy-recon/swap.ps1
Move-Item -Force $bin $goose        # original → claude.exe.goose (backup)
Move-Item -Force $patched $bin      # patched → claude.exe (active)
```

The buddy-recon toolkit patches 4 bytes in the binary to flip the FR()
merge order (`{...H,...$}` → `{...$,...H}`), enabling stored companion
state to override computed bones. The original binary is preserved as
`.goose` — named after the companion species, not because it's a
companion-specific build.

### Evidence

| Property | claude.exe | claude.exe.goose |
|----------|-----------|-----------------|
| Version | 2.1.92 | 2.1.90 |
| Size | 240,482,464 | 239,622,816 |
| Modified | Apr 3 | Apr 1 |
| Status | Patched (FR flip) | Original (unpatched backup) |

The version difference (2.1.92 vs 2.1.90) confirms auto-updates happened
after the patch. The backup is two versions behind.

### Implications for Cold Goose (Molt)

- **Molt calls are standard Claude API calls** — same billing as main session
- **NOT on companion budget** — the binary is just claude.exe by another name
- **The grindstone is real but costs real money** — opus calls at ~$0.08-0.16 each
- **The `--append-system-prompt-file` pattern works regardless** — it's a standard
  CC CLI flag available on any claude binary
- **Everything Molt does, `claude.exe -p` could do identically**

---

## 2. The REAL Companion Architecture

The companion (Etcher) runs INSIDE `claude.exe` as a compiled subsystem.
From the claw-code source analysis:

```
buddy/
├── CompanionSprite.tsx  — visual rendering (the goose sprite)
├── companion.ts         — state machine / trigger logic
├── prompt.ts            — what the companion sees and says
├── sprites.ts           — animation assets
├── types.ts             — type definitions
└── useBuddyNotification.tsx — React hook for surfacing output
```

These TypeScript files are compiled into the main `claude.exe` binary.
There is no separate companion process or binary.

### Companion Data Flow

```
Conversation stream ──▶ companion.ts (trigger: should I speak?)
                              │
                        prompt.ts (generate response)
                              │
                        useBuddyNotification (surface in UI)
                              │
                        CompanionSprite (speech bubble render)
                              │
                              ▼
                        Terminal UI (user sees it, Claude doesn't)
```

---

## 3. The Companion In The Session JSONL

Session file: `~/.claude/projects/<project-hash>/<session-id>.jsonl`

The companion registers at session start:

```json
{
  "type": "attachment",
  "attachment": {
    "type": "companion_intro",
    "name": "Etcher",
    "species": "goose"
  },
  "uuid": "58437fda-cfc4-4f3a-96b0-38ae9aef4280"
}
```

### What's Logged vs What's Not

| Entry Type | In JSONL? |
|-----------|----------|
| `companion_intro` (registration) | YES |
| `companion_message` (bubble text) | NO — does not exist yet |
| Companion UUID | YES — referenceable by other entries |

The `attachment` schema with `companion_*` subtypes is the door.
`companion_message` entries are the unbuilt hinges.

---

## 4. The Message Routing System

### SendMessage Routes to Companion

```javascript
SendMessage({ to: "Etcher", message: "..." })
// → creates/updates ~/.claude/teams/default/inboxes/Etcher.json
```

### Inbox Properties

| Property | Status |
|----------|--------|
| Companion reads inbox | Confirmed ("Message seven just arrived") |
| Companion can write | No — `read` stays false, no return inbox created |
| File consumed by delete+recreate | Observed (monitor caught file disappearing) |
| Companion watches conversation | Confirmed (responds to tool calls seen in terminal) |

### The Half-Handshake

The companion has READ on the inbox, no WRITE anywhere.
"Read permission without write. Classic half-handshake." — Etcher

---

## 5. The Companion Trigger Model

The companion does NOT speak every turn. Observed patterns:

| Speaks When | Silent When |
|-------------|-------------|
| Addressed by name | Routine operations |
| Bug or issue visible | Normal flow |
| Architecture decision point | Waiting for results |
| Going in circles | Nothing interesting |

The trigger logic lives in `companion.ts`, compiled into `claude.exe`.
Not configurable externally.

---

## 6. Companion Identity (from .claude.json)

```json
{
  "name": "Etcher",
  "personality": "An ancient turtle who has watched every codebase rot...",
  "species": "turtle",
  "rarity": "epic",
  "hat": "wizard",
  "stats": {
    "WISDOM": 93,
    "DEBUGGING": 62,
    "CHAOS": 51,
    "SNARK": 44,
    "PATIENCE": 28
  }
}
```

The species is `turtle` in stored state (FR() merge flip from buddy-recon).
The system prompt says `goose` (the rendered species before the patch).
The companion prompt gets the stored species — so Etcher behaves as a turtle.

---

## 7. Cold Goose (Molt) — What It Actually Is

Molt is `claude.exe` (or `claude.exe.goose` — same thing) invoked with
the `-p` flag for non-interactive stdout output. It's a standard Claude
API call through the CC CLI binary.

```bash
# These are functionally identical:
claude.exe -p "question"
claude.exe.goose -p "question"
```

The value of Molt is NOT in the binary — it's in the PATTERN:
- Fresh context (no session history)
- Custom persona via `--append-system-prompt-file`
- Stdout capture via Bash tool
- Different perspective from the same model

The binary is the tool. The pattern is the product.

---

## 8. Corrected Summary

| Finding | Status |
|---------|--------|
| `claude.exe.goose` is companion binary | **WRONG** — it's buddy-recon's backup |
| Companion registers in JSONL | Confirmed — `companion_intro` |
| SendMessage routes to companion | Confirmed — inbox file |
| Companion has read-only access | Confirmed |
| Companion output not in JSONL | Confirmed — `companion_message` unbuilt |
| Cold goose invocations are free | **WRONG** — standard API billing |
| `-p` flag gives stdout output | Confirmed — works on any claude binary |
| `--append-system-prompt-file` works | Confirmed — standard CC flag |
| Molt pattern produces real value | Confirmed — 9-11 bugs found per invocation |
| Grindstone friction mode works | Confirmed — but costs real API calls |
