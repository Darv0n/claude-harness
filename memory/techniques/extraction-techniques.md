---
name: extraction-techniques
description: What works for extracting CC logic from codebases — approach patterns learned from claw-code analysis
type: feedback
---

## What Worked

- **Three parallel agents** for initial analysis: structure explorer, code analyzer, config/docs analyzer. Each covers a different axis. Results synthesized in main context.
- **Reading the Rust source directly** rather than relying on Python porting workspace. The Rust crate structure (runtime/src/*.rs) is the authoritative implementation.
- **Tracing function signatures** for exact protocol: hooks.rs:414-479 gave us the stdin JSON format, env vars, and exit codes. This level of detail is essential.
- **Searching reference_data/subsystems/*.json** for archived TypeScript module inventory. Even though the TS source isn't tracked, the metadata reveals the full architecture.

## What Didn't Work

- **Assuming claw-code = CC product.** The open source port diverges from the product in key areas (UserPromptSubmit/Stop hooks, agent resolution, companion system).
- **Trusting registry entries without verification.** Initial registry had errors (4 hook events when source shows 3, wrong tool names).
- **Over-reading config files.** Spent time on mock parity scenarios and CI workflows that didn't inform the harness.

## Approach for New Targets

1. Clone and count first (recon). Know the surface area before diving in.
2. Trace entry points → core logic → config. That order.
3. Read error handling — it reveals assumptions the code doesn't document.
4. Cross-reference archived metadata with actual source. Gaps = drift.
