---
name: performance
description: Agent performance metrics from harness operations — what ran, how long, what quality
type: project
---

## cli-task-manager Deployment (first test run)

| Phase | Agent | Model | Duration | Output Quality |
|-------|-------|-------|----------|---------------|
| Decompose | domain-decomposer | opus | ~3 min | 300 lines, 25 source files traced, all 6 workflows captured |
| Scan | integration-scanner | sonnet | ~3.5 min | 8K, 13 MCP servers, 7 APIs, 4 CLIs found |
| Map | capability-mapper | opus | ~3 min | 272 lines, 27 ops mapped, full coverage metric |
| Generate | layer-generator | opus | ~9 min | 44 files, all 6 layers, 3,495 char CLAUDE.md |
| Validate | environment-validator | sonnet | ~3.5 min | Found 1 blocker + 6 warnings |

Total pipeline: ~22 min for complete 6-layer environment generation.

## Bugs Found Post-Deployment: 4

All caught by Etcher (companion code review), not by the validator.
Root cause: validator checked form (static), not function (dynamic).
Fix: added smoke-tester agent to pipeline.

## Etcher Bridge Discovery

Time spent: ~1.5 hours
Channels found: 3 (SendMessage, screenshot, goose binary)
Key finding: companion_intro in session JSONL proves attachment schema supports companion entries.
Binary: ~/.local/bin/claude.exe.goose (239MB, separate build)
