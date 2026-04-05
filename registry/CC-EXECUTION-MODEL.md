# Claude Code Execution Model — Deep Logic Reference

This document encodes the INTERNAL MECHANICS of how Claude Code works. Every agent
in this harness MUST understand this to generate environments that exploit CC fully.

Source: claw-code analysis (48.6K LOC Rust + Python porting workspace).

---

## 1. THE EXECUTION LOOP

When a user sends a message, CC runs this loop:

```
User Input
    │
    ▼
[UserPromptSubmit hooks fire] ← can inject system messages
    │
    ▼
System prompt assembled (see §7)
    │
    ▼
API call to Claude (streaming)
    │
    ▼
Claude responds with text + tool_use blocks
    │
    ▼
For EACH tool_use:
    ├─ [PreToolUse hooks fire] ← can BLOCK (exit 1) or ALLOW (exit 0)
    ├─ Permission check (see §4)
    ├─ Tool executes
    ├─ [PostToolUse hooks fire] ← can inject quality feedback
    └─ Tool result added to conversation
    │
    ▼
Loop continues until Claude sends MessageStop
    │
    ▼
[Stop hooks fire] ← session end capture
    │
    ▼
Session persisted to disk
```

**KEY INSIGHT**: Hooks fire OUTSIDE Claude's context. They are shell commands run
by the harness, not by Claude. Their stdout becomes system messages that Claude
sees on the NEXT turn. This means hooks can:
- Inject routing suggestions before Claude processes input
- Block dangerous tool calls before they execute
- Inject quality feedback after tool output
- Capture session data on exit

---

## 2. HOOK PROTOCOL (MECHANICAL DETAIL)

Source: `runtime/src/hooks.rs:19-300`

### How hooks receive data

Each hook command receives context via BOTH stdin and environment variables:

**stdin (JSON):**
```json
{
  "event": "PreToolUse|PostToolUse|PostToolUseFailure",
  "tool_name": "bash",
  "tool_input": "{\"command\": \"rm -rf /\"}",
  "tool_output": "...",      // POST hooks only
  "is_error": false           // POST hooks only
}
```

**Environment variables:**
- `HOOK_EVENT` — event type string
- `HOOK_TOOL_NAME` — tool being invoked
- `HOOK_TOOL_INPUT` — JSON string of tool parameters
- `HOOK_TOOL_OUTPUT` — tool result (POST hooks only)
- `HOOK_TOOL_IS_ERROR` — "0" or "1"

### How hooks control execution

**Exit codes:**
- `0` = Allow (tool executes normally)
- `1` = Deny (tool call BLOCKED, stdout shown as warning)
- `2+` = Failure (hook chain stops, error reported)

**stdout**: Whatever the hook prints becomes a system message. Claude sees it.

**Return values** (advanced): Hooks can return:
- `permission_override`: Force Allow/Deny/Ask regardless of mode
- `updated_input`: Modify the tool's input before execution
- `messages`: Array of system messages to inject

### Hook execution order
Hooks execute SEQUENTIALLY within an event type. First hook to deny stops the chain.
Config validated BEFORE deep-merge — malformed hooks fail with source-path context.

### EXPLOITATION PATTERNS

**Pattern: Smart Router**
```bash
#!/bin/bash
# UserPromptSubmit hook — reads stdin, detects intent, suggests skill
INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt // empty')
if echo "$PROMPT" | grep -qi "linkedin\|profile\|prospect"; then
  echo "[HARNESS] LinkedIn prospect detected. Running /research pipeline."
fi
```

**Pattern: Quality Gate**
```bash
#!/bin/bash
# PostToolUse hook on Write — validates output
INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name')
if [ "$TOOL" = "Write" ]; then
  OUTPUT=$(echo "$INPUT" | jq -r '.tool_output')
  # Check output quality, echo feedback
  echo "[QUALITY] Review written content for domain compliance."
fi
```

**Pattern: Dangerous Command Guard**
```bash
#!/bin/bash
# PreToolUse hook on Bash — blocks destructive commands
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input' | jq -r '.command // empty')
if echo "$CMD" | grep -qE "rm -rf|drop table|git push --force"; then
  echo "BLOCKED: Destructive command detected: $CMD"
  exit 1
fi
```

---

## 3. AGENT SPAWNING MECHANICS

Source: `crates/tools/src/lib.rs`, `runtime/src/worker_boot.rs`

### How the Agent tool works

When Claude calls the Agent tool:

```json
{
  "prompt": "task description",
  "description": "3-5 word summary",
  "subagent_type": "agent-name",
  "model": "opus|sonnet|haiku",
  "mode": "bypassPermissions|auto|...",
  "run_in_background": true,
  "isolation": "worktree",
  "name": "addressable-name"
}
```

**What happens internally:**
1. A new Worker is created in WorkerRegistry
2. Worker status: `Created → Ready → Running → Completed|Failed`
3. Trust resolution runs (TrustPolicy evaluates)
4. A NEW conversation is started with fresh context
5. The agent's `.md` file body becomes part of the system prompt
6. The agent can ONLY use tools listed in its frontmatter `tools:` field
7. The agent runs independently — it has NO access to the parent conversation

**CRITICAL IMPLICATIONS FOR GENERATED ENVIRONMENTS:**
- Agent prompts must be COMPLETE — include ALL context the agent needs
- Agents cannot reference "the conversation so far" — they start fresh
- Tool access is RESTRICTIVE — only listed tools work
- Model selection affects cost AND capability
- `run_in_background: true` enables parallel execution
- `name` parameter enables `SendMessage` for inter-agent communication
- `isolation: "worktree"` gives isolated git copy (for code generation agents)

### Parallel execution pattern

Multiple Agent calls in a SINGLE message = parallel execution:
```
// In one response, Claude can spawn multiple agents:
Agent({ prompt: "task 1", name: "worker-1", run_in_background: true })
Agent({ prompt: "task 2", name: "worker-2", run_in_background: true })
// Both run concurrently
```

### Inter-agent communication

Named agents can receive messages:
```
SendMessage({ to: "worker-1", message: "new instructions" })
```
The agent resumes with its full context preserved.

---

## 4. PERMISSION ENFORCEMENT ALGORITHM

Source: `runtime/src/permissions.rs:164-190`, `permission_enforcer.rs`

When a tool call is made, permissions are evaluated in THIS order:

```
1. CHECK DENY RULES → if any match, BLOCK immediately
2. CHECK MODE SUFFICIENCY → does current mode allow this tool?
   - ReadOnly: read, glob, grep, websearch only
   - WorkspaceWrite: + write, edit, notebook
   - DangerFullAccess: + bash, agent, task
3. CHECK ASK RULES → if match, PROMPT USER for approval
4. CHECK ALLOW RULES → if match, AUTO-ALLOW
5. FALL BACK TO MODE → mode's default decision
```

**Rule format**: `tool_name:input_pattern`
- `bash:npm *` — allow npm commands in bash
- `bash:rm -rf` — deny rm -rf in bash
- `write:*.rs` — ask before writing Rust files
- `read:/**` — allow reading all files

**EXPLOITATION**: Generated environments should use granular rules to:
- Auto-allow domain-safe operations (no permission prompts = faster execution)
- Hard-deny dangerous patterns (even if mode would allow them)
- Ask for edge cases (human judgment where needed)

---

## 5. SKILL TRIGGERING MECHANICS

Source: `crates/commands/src/lib.rs:237-242`

### How skills activate

Skills are discovered from `.claude/skills/*.md` files. The `description` field in
the frontmatter is the ONLY thing CC uses to decide when to activate a skill.

**The matching algorithm:**
1. User types a message
2. CC compares message against ALL skill descriptions
3. Best-matching skill's body is injected as instructions
4. CC follows the skill's instructions

**EXPLOITATION**: The description field is the MOST IMPORTANT part of a skill.
Write it like a search index:
```yaml
---
description: |
  Use when the user asks to "research a prospect", "build a dossier",
  "analyze a LinkedIn profile", "score a lead", or provides a LinkedIn URL.
  Examples: "/research https://linkedin.com/in/someone",
  "research John Smith", "build dossier on this prospect"
---
```

More trigger phrases = higher activation rate. Be specific but comprehensive.

### Skill composition

Skills can invoke other skills via the Skill tool:
```
Skill({ skill: "research", args: "John Smith" })
```
This enables skill chaining without manual intervention.

---

## 6. MEMORY LIFECYCLE

Source: `runtime/src/prompt.rs:199-220`

### Auto-loading

`MEMORY.md` is ALWAYS loaded into the system prompt. Every session. This is why:
- MEMORY.md must be an INDEX (pointers), not content
- Each entry should be under 150 characters
- Total MEMORY.md should be under 200 lines (truncated after)
- Heavy content goes in individual memory files (loaded on demand)

### Memory file format

```yaml
---
name: prospect-john-smith
description: Whale-tier SaaS CTO, researched 2026-04-01
type: project
---

[content here]
```

The `description` field is used for RELEVANCE MATCHING — CC reads it to decide
whether to load the full file. Write it like a search snippet.

### The Learning Loop (most powerful pattern)

```
OBSERVE → EXTRACT → APPLY → FEEDBACK
   │          │         │        │
   │    Stop hook or    │   User corrections
   │    skill completion│   saved as feedback
   │          │         │   memory type
   │          ▼         │
   │    Write to        │
   │    memory/patterns/ │
   │          │         │
   ▼          ▼         ▼
Agent      Memory     Memory
behavior   read at    refined
during     session    by user
operation  start      input
```

**EXPLOITATION**: Every generated environment MUST have:
1. A `patterns/` directory in memory for accumulated knowledge
2. A mechanism to EXTRACT patterns (Stop hook or skill completion step)
3. A mechanism to APPLY patterns (memory read at relevant decision points)
4. A mechanism for user FEEDBACK to refine patterns

---

## 7. SYSTEM PROMPT ASSEMBLY

Source: `runtime/src/prompt.rs:89-191`

The system prompt is assembled in THIS order:

```
[1] Core identity + behavior rules (IMMUTABLE)
[2] Output style (configurable via /output-style)
[3] System instructions (IMMUTABLE)
[4] Task approach rules (IMMUTABLE)
[5] Tool schemas + descriptions (AUTO-GENERATED from tool registry)
[6] ──── DYNAMIC BOUNDARY ────
[7] Environment: model, cwd, date, platform, shell
[8] Project context: git status, instruction file content
[9] CLAUDE.md content (4K per file, 12K total across all files)
[10] Config: MCP servers, plugin status, active settings
[11] Custom appended sections
```

**EXPLOITATION — CLAUDE.md IS YOUR INJECTION POINT:**

Positions 1-8 are controlled by the system. Position 9 (CLAUDE.md) is where YOU
inject domain knowledge. This means:

- Front-load the most critical rules (attention decays with document length)
- Stay under 4,000 characters per CLAUDE.md file
- Total across all CLAUDE.md files (walking up directory tree) capped at 12,000 chars
- Format shapes behavior: bulleted specs → bulleted outputs, flowing narrative → flowing judgment
- State machines as ASCII diagrams give Claude visual structure to follow
- ICP matrices as tables give Claude classification structure

**EXPLOITATION — SKILL DESCRIPTIONS IN THE PROMPT:**

Skill descriptions are listed in system reminders. This means every skill's
description is ALWAYS in context. Write them densely — they compete for attention.

**EXPLOITATION — MEMORY IN THE PROMPT:**

MEMORY.md is injected into system reminders. It's always present. This is why
the index must be lean and the hooks must be descriptive — Claude reads them
EVERY TURN to decide what's relevant.

---

## 8. SESSION COMPACTION

Source: `runtime/src/compact.rs`

When input tokens exceed ~100,000:
- Middle section of conversation is compressed
- AI generates a summary of removed content
- Most recent messages + pinned messages are preserved
- Compaction count tracked in session metadata

**EXPLOITATION**: For generated environments with long workflows:
- Use memory files for persistent state (survives compaction)
- Don't rely on conversation history for critical data
- Write important intermediate results to files, not just conversation

---

## 9. MCP TOOL BRIDGE

Source: `runtime/src/mcp*.rs`

### How MCP tools appear to Claude

MCP tools are namespaced: `mcp__<server>__<tool>`
They appear as regular tools in Claude's tool list.
Claude calls them like any other tool.

### Degraded mode (partial success is first-class)

If server A fails but server B succeeds:
- Server B's tools are available
- Server A's tools are missing
- Recovery recommendations generated

**EXPLOITATION**: Generated environments should:
- Configure MCP servers with appropriate timeouts
- Handle degraded mode in CLAUDE.md (document what to do when a server is down)
- Use built-in tools as fallbacks when MCP fails

---

## 10. CONFIG CASCADE ALGORITHM

Source: `runtime/src/config.rs:229-256`

```
~/.claude.json        (User legacy)     ─┐
~/.claude/settings.json (User)          ─┤ Deep merge
.claude.json          (Project legacy)  ─┤ Later overrides
.claude/settings.json (Project)         ─┤ earlier
.claude/settings.local.json (Local)     ─┘ ← HIGHEST PRIORITY
```

**Validation happens BEFORE merge** — bad config in one source doesn't corrupt others.

**EXPLOITATION**: Generated environments should use:
- `.claude/settings.json` for project-level defaults (committed to git)
- `.claude/settings.local.json` for machine-specific overrides (gitignored)
- User-level settings for operator preferences (not touched by the environment)

---

## 11. SANDBOX AND ISOLATION

Source: `runtime/src/sandbox.rs`

Three filesystem modes:
- `Off` — full access
- `WorkspaceOnly` — locked to project directory
- `AllowList` — only specified mounts

Agent isolation via `isolation: "worktree"` creates a temporary git worktree
so the agent works on an isolated copy. Changes in worktree don't affect main.

**EXPLOITATION**: For generated environments that do code generation:
- Use worktree isolation for agents that write code
- Use WorkspaceOnly sandbox for agents that should stay in the project
- Use AllowList for agents that need access to specific external directories

---

## 12. TOOL-TO-DOMAIN MAPPING ALGORITHM

When mapping domain operations to CC tools, use this decision tree:

```
Does the operation need external data?
├── YES: Does an MCP server exist?
│   ├── YES → Use MCP tool
│   └── NO: Can it be done via web?
│       ├── YES → WebSearch + WebFetch
│       └── NO: Does it need a CLI tool?
│           ├── YES → Bash (wrap the CLI)
│           └── NO → Custom MCP server needed
│
└── NO: Does it read or write files?
    ├── READ → Read + Glob + Grep
    ├── WRITE → Write + Edit
    └── NEITHER: Does it need computation?
        ├── YES → Bash (run a script)
        └── NO: Is it orchestration?
            ├── YES → Agent (spawn specialist)
            └── NO → It's probably a CLAUDE.md rule, not a tool
```

---

## 13. AGENT MODEL SELECTION ALGORITHM

```
What is the cognitive load?
│
├── COMPLEX REASONING (architecture, strategy, creative writing, nuanced judgment)
│   → opus ($$$) — worth the cost for quality-critical outputs
│
├── BALANCED (research, analysis, code gen, moderate decisions)
│   → sonnet ($$) — best quality/cost ratio for most tasks
│
├── SIMPLE (status tracking, data extraction, transforms, high-volume ops)
│   → haiku ($) — fast and cheap, good enough for structured tasks
│
└── ROUTING DECISION: How many times will this agent run?
    ├── ONCE per session → cost doesn't matter, use opus
    ├── FEW TIMES → sonnet is fine
    └── MANY TIMES (per entity, per message) → haiku or you'll burn budget
```
