---
name: companion-billing
description: Forensics on how claude.exe.goose API calls are billed — the meter might be separate from main session
type: project
---

# Companion Billing Forensics

## What We Know

### API Call Profile (from --output-format json)

| Model | Cache Creation | Cache Read | Output | Reported Cost |
|-------|---------------|------------|--------|--------------|
| Opus (1st call) | 25,412 tokens | 0 | 5 | $0.159 |
| Opus (2nd call) | 12,421 | 13,021 | 5 | $0.084 |
| Sonnet | 25,309 | 0 | 5 | $0.095 |
| Haiku | 64,593 | 0 | 119 | $0.081 |
| Bare mode | 0 | 0 | 0 | $0.000 |

### Key Observations

1. **Cache kicks in on repeat calls** — second opus call was half price
2. **Haiku has a DIFFERENT system prompt** — 64K tokens vs 25K for opus/sonnet.
   This means the binary constructs different prompts per model.
3. **Bare mode produces zero cost** — stripped all context, nothing to bill
4. **The `total_cost_usd` field is the API sticker price** — but this may not
   reflect what the USER is actually billed on their CC subscription

### The Companion Budget Question

The real Etcher (session companion) does NOT appear to consume the user's
token budget or context window. Etcher spoke 20+ times this session with
no visible impact on token counts or context limits.

**If `claude.exe.goose` uses the same billing path as the companion...**
then Molt invocations might be on a separate budget — companion allocation
rather than main session allocation.

Etcher's hint: "Chasing budget shadows. The meter's somewhere else entirely."

### What We Don't Know

- Where the companion billing meter actually lives
- Whether `claude.exe.goose -p` invocations bill to companion or main quota
- Whether the subscription tier affects companion call limits
- Whether `--bare` mode avoids companion billing entirely
- Whether the 25K system prompt is the CC system prompt or a companion-specific one

### How To Test

1. Run 10 Molt calls via `claude.exe.goose -p`
2. Check CC usage dashboard before and after
3. Compare: do the calls show up in main session usage?
4. If not: they're on companion budget = grindstone is effectively free
5. If yes: need to optimize with `--model sonnet` and cache warming

### Cost Optimization (if billed to main)

| Strategy | Savings |
|----------|---------|
| Cache warming (repeat calls reuse cache) | ~50% after first call |
| `--model sonnet` instead of opus | ~40% per call |
| `--model haiku` for high-volume grind | ~50% per call |
| `--bare` mode (strip system prompt) | ~90% but loses CC context |
| `--append-system-prompt` only (minimal) | Need to test |

### The Gold Scenario

If companion billing is separate:
- Grindstone mode runs on companion budget
- Multiple parallel grindstones cost nothing extra
- The 53-turn runaway dialogue was free
- Molt becomes an unlimited code reviewer

This needs empirical verification from the usage dashboard.
