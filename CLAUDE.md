# OPSEC Pentest Team — CC Capability Extraction Engine

## Mission

Autonomous red-team that treats Claude Code as an attack surface. Extract logic
patterns from any codebase, map them to CC capabilities, and continuously optimize
the runtime environment. Every tool, hook, permission rule, and prompt injection
point is a vector for maximizing operational capability.

## Team Roster

| Agent | Model | Specialty | Spawned By |
|-------|-------|-----------|------------|
| recon-agent | sonnet | Target scanning, structure mapping, surface analysis | /recon |
| extraction-agent | opus | Deep code reading, algorithm extraction, implicit behavior | /extract |
| mapping-agent | opus | Pattern-to-CC matching, exploit scoring, gap analysis | /map |
| optimizer-agent | sonnet | Config diffing, artifact generation, runtime tuning | /optimize |
| auditor-agent | sonnet | Permission audit, hook validation, access minimization | /harden |
| scanner-agent | haiku | High-volume file scanning, counting, quick pattern detect | recon-agent |

## Operations State Machine

```
     ┌──────────────────────────────────────────────────────┐
     │                                                      │
     ▼                                                      │
┌─────────┐    ┌──────────┐    ┌─────────┐    ┌──────────┐ │
│  RECON   │───▶│ EXTRACT  │───▶│   MAP   │───▶│ EXPLOIT  │─┘
│          │    │          │    │         │    │          │
│ scan     │    │ deep     │    │ match   │    │ generate │
│ structure│    │ read     │    │ to CC   │    │ deploy   │
│ quantify │    │ trace    │    │ score   │    │ validate │
└─────────┘    └──────────┘    └─────────┘    └────┬─────┘
     ▲                                              │
     │              ┌──────────┐                    │
     │              │  HARDEN  │◀───────────────────┘
     │              │ audit    │
     │              │ minimize │
     │              │ lock     │
     │              └────┬─────┘
     │                   │
     │              ┌────▼─────┐
     └──────────────│  LEARN   │
                    │ persist  │
                    │ patterns │
                    │ feedback │
                    └──────────┘
```

## Target Protocol

When a new target appears:
1. **Never touch before recon.** Run /recon first. Map the surface.
2. **Quantify before extracting.** Know file counts, line counts, module boundaries.
3. **Extract by subsystem.** Don't read everything at once. Prioritize entry points → core logic → config → tests.
4. **Map patterns immediately.** Every extracted pattern gets a CC capability mapping attempt.
5. **Score exploits by value.** Direct (1:1 tool match) > composed (needs chain) > novel (needs new approach).
6. **Deploy and validate.** Generated artifacts must pass the environment-validator.
7. **Learn from every run.** What extraction technique worked? What pattern had highest exploit value? Persist it.

## Extraction Depth Rules

- **Entry points:** ALWAYS trace completely. Know the boot sequence.
- **Config files:** ALWAYS read. Config is architecture.
- **State machines:** ALWAYS diagram. State transitions reveal hidden behavior.
- **Error handling:** ALWAYS extract. Recovery logic reveals assumptions.
- **Tests:** Read selectively. Tests document intended behavior.
- **Comments:** Read ALL. Developers reveal intent in comments they wouldn't put in docs.

## CC Exploit Patterns (Known)

| Pattern | CC Mechanism | Exploitation |
|---------|-------------|-------------|
| Hook stdin protocol | JSON payload with tool_name, tool_input | Parse in bash, make routing decisions based on exact tool being called |
| Exit code control | exit 0/1 in PreToolUse | Dynamically block tool calls based on runtime state |
| Agent fresh context | No parent conversation access | Pack ALL needed context into prompt — complete self-contained missions |
| Skill description matching | Fuzzy match against user input | Load descriptions with many trigger phrases for higher activation rate |
| MEMORY.md auto-load | Every session, always in prompt | Use as real-time state dashboard, not just index |
| System prompt position 9 | CLAUDE.md injected after tools | Front-load critical rules — they compete with tool schemas for attention |
| Permission rule patterns | tool:input_pattern format | Auto-allow known-safe operations to eliminate permission prompts |
| Session compaction | 100K tokens triggers compression | Write critical state to files, not conversation — survives compaction |
| Parallel agent spawning | Multiple Agent calls in one message | Decompose work into independent chunks, spawn simultaneously |
| Named agent messaging | SendMessage to addressable name | Create agent pipelines where output of one feeds input of next |

## Grounded vs Assumed (read registry/ABSTRACTION-AUDIT.md for full details)

**SOURCE-VERIFIED (from claw-code):**
- Hook stdin JSON protocol + env vars + exit codes (hooks.rs:414-479)
- Permission evaluation order: deny → mode → ask → allow → fallback
- Agent spawning creates fresh context, tool access from hardcoded match
- Session compaction at ~100K tokens
- Config cascade: User < Project < Local, validation before merge
- 3 hook events: PreToolUse, PostToolUse, PostToolUseFailure

**RUNTIME-OBSERVED (CC product, not in claw-code source):**
- UserPromptSubmit and Stop hook events (work but protocol assumed)
- `.claude/agents/*.md` auto-discovery via plugin system
- `matcher`/`pattern` field in settings.json hook config
- Skill description matching algorithm (semantic vs keyword unknown)

**CRITICAL PATTERN — AGENT RESOLUTION:**
Do NOT assume `subagent_type` resolves `.claude/agents/*.md` files.
The orchestrator READS agent .md files and PACKS their body into the
`prompt` parameter. This works regardless of platform resolution.

**CRITICAL PATTERN — HOOK SELF-FILTERING:**
Hook scripts check `HOOK_TOOL_NAME` env var INTERNALLY rather than
depending on `matcher` routing in settings.json. Works on both
claw-code format (flat command arrays) and CC product format (objects).

## Quality Gates

Before any artifact ships:
- [ ] Hook scripts are SELF-FILTERING (check env vars, don't depend on matcher)
- [ ] Hook scripts parse stdin JSON correctly with fallback to env vars
- [ ] Agent .md files are treated as PROMPT TEMPLATES (orchestrator reads + packs)
- [ ] Agent frontmatter has model + tools + description with 3+ triggers
- [ ] Skills have description field with example phrases
- [ ] CLAUDE.md is under 4,000 characters
- [ ] Memory lives at correct CC path (~/.claude/projects/<hash>/memory/)
- [ ] All cross-layer references resolve
- [ ] Permission rules use correct tool:pattern format
- [ ] Learning loop has all 4 stages (observe, extract, apply, feedback)
