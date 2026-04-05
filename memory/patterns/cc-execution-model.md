---
name: cc-execution-model
description: Extracted CC runtime mechanics — hook protocol, agent spawning, permission algo, prompt assembly, memory paths
type: project
---

Extracted from claw-code analysis (48.6K LOC Rust). Full reference at registry/CC-EXECUTION-MODEL.md.

Key patterns for the generator:
- Hooks: stdin JSON + env vars, exit 0=allow/1=deny, use python3 not jq
- Agents: fresh context, tools restricted to frontmatter, prompt must be self-contained
- Permissions: deny → mode → ask → allow → fallback
- CLAUDE.md: position 9 in prompt, 4K/file limit, format shapes behavior
- Memory: auto-loads from ~/.claude/projects/<hash>/memory/, NOT project root
- Compaction: 100K tokens, use files not conversation for persistent state
- MCP: mcp__server__tool naming, partial failure is first-class
