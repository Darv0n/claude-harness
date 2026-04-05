---
name: claw-code
description: Claude Code source — 48.6K LOC Rust, 9 crates, Python porting workspace. Fully recon'd and extracted.
type: project
---

## Target: claw-code (ultraworkers/claw-code)

**Status:** EXTRACTED + MAPPED
**Location:** `apps/claw-code/`
**Language:** Rust (primary), Python (porting workspace)
**Lines:** 48,599 Rust + Python porting workspace

## Surface Area
- 9 Rust crates: api, commands, compat-harness, mock-anthropic-service, plugins, runtime, rusty-claude-cli, telemetry, tools
- Runtime crate is the core: 38 .rs files covering config, hooks, permissions, sessions, conversation, prompts, MCP, tasks, teams, cron, sandbox, recovery, policy
- Python porting workspace: 67 .py files mirroring TS architecture
- 12 mock parity scenarios with 21 captured requests

## Key Extraction Targets (All Complete)
1. Hook protocol (stdin JSON, env vars, exit codes)
2. Permission evaluation algorithm (deny → mode → ask → allow → fallback)
3. Agent spawning mechanics (Worker lifecycle, trust resolution)
4. System prompt assembly order (11 positions, CLAUDE.md at position 9)
5. Session compaction (100K threshold, summary compression)
6. MCP lifecycle (6 transports, degraded mode, partial success)
7. Config cascade (5-level, pre-merge validation)
8. Plugin manifest format (lifecycle, hooks, tools, commands)
9. Sandbox isolation modes (Off, WorkspaceOnly, AllowList)
10. Recovery recipes (7 failure scenarios with auto-healing)
