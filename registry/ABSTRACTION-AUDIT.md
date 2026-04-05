# Abstraction Audit — Critical Gaps Between Assumptions and Ground Truth

This document confronts every place where the harness rides on implicit assumptions
rather than verified mechanics. Each gap is classified and resolved.

---

## GAP 1: HOOK FORMAT — CRITICAL

### What We Assumed
Our `settings.json` uses objects with `"matcher"` and `"command"` keys:
```json
{"matcher": "(?i)github\\.com", "command": "echo '...'"}
```

### What The Source Actually Says
`claw-code/rust/crates/runtime/src/config.rs:68-72`:
```rust
pub struct RuntimeHookConfig {
    pre_tool_use: Vec<String>,      // Just command strings
    post_tool_use: Vec<String>,     // Just command strings
    post_tool_use_failure: Vec<String>,
}
```

The claw-code source shows hooks as **flat arrays of command strings**, not objects
with matcher/pattern fields. There is NO pattern matching in the hook config — the
hook command itself must do any filtering.

### What The CC Product Actually Does
The CC product (which we're running in) supports a richer format with `pattern` or
`matcher` fields for filtering by tool name. This is NOT in the claw-code source —
it's a product-level feature built on top.

### Resolution
**The `matcher` key might need to be `pattern`.** The CC system prompt mentions
hooks "configured in settings.json" but doesn't specify the exact JSON format.
We need to test empirically. For safety, the bash-guard script should do its OWN
filtering rather than relying on matcher-based routing.

**ACTION:** Update hook scripts to be self-filtering (check HOOK_TOOL_NAME env var
internally) rather than depending on matcher config for routing.

---

## GAP 2: AGENT RESOLUTION — CRITICAL

### What We Assumed
That `subagent_type: "domain-decomposer"` would resolve to `.claude/agents/domain-decomposer.md`
and use its body as the system prompt and its frontmatter `tools:` field for tool restriction.

### What The Source Actually Says
`claw-code/rust/crates/tools/src/lib.rs:3164-3177`:
```rust
fn build_agent_system_prompt(subagent_type: &str) -> Result<Vec<String>, String> {
    let mut prompt = load_system_prompt(cwd, ...);
    prompt.push(format!(
        "You are a background sub-agent of type `{subagent_type}`..."
    ));
    Ok(prompt)
}
```

And `lib.rs:3187-3265`:
```rust
fn allowed_tools_for_subagent(subagent_type: &str) -> BTreeSet<String> {
    let tools = match subagent_type {
        "Explore" => vec![...],
        "Plan" => vec![...],
        _ => vec!["bash", "read_file", "write_file", ...],  // DEFAULT: all standard tools
    };
}
```

**In claw-code, agent resolution is a HARDCODED match statement.** Unknown types get
the default tool set. The `.md` body is NOT loaded as the system prompt — instead,
a generic prompt is built and the subagent_type is appended as a label.

### What The CC Product Actually Does
The CC product has a DIFFERENT agent system. Custom agents come from **plugins**
(`.claude-plugin/plugin.json` or similar) with agent definitions that include
frontmatter. The system prompt lists them as `plugin:agent-name` format.

The `.claude/agents/*.md` files ARE a real CC feature — they're how plugins define
agents. But the `subagent_type` parameter on the Agent tool maps to these via the
plugin system, not via direct file lookup.

### Resolution
**Our `.claude/agents/*.md` files are structurally correct** — they follow the CC
agent definition format. But the `subagent_type` parameter alone may not resolve
to them. The CC product likely discovers them through the plugin/agent registry.

**What DOES work:** The Agent tool with `prompt` parameter. The prompt IS the agent's
instructions. The `.md` file's body is documentation of WHAT the prompt should contain.

**CORRECT PATTERN:** The orchestrator should NOT rely on `subagent_type` to magically
load `.claude/agents/domain-decomposer.md`. Instead, it should:
1. READ the `.md` file itself
2. PACK the content into the `prompt` parameter
3. Set `model` explicitly
4. The `.md` files serve as TEMPLATES that the orchestrator reads and uses

This is actually MORE powerful — the orchestrator controls exactly what each agent sees.

---

## GAP 3: UserPromptSubmit AND Stop HOOKS — MEDIUM

### What We Assumed
That UserPromptSubmit and Stop are hook events like PreToolUse and PostToolUse.

### What The Source Says
`claw-code/rust/crates/runtime/src/hooks.rs:19-34` defines exactly 3 events:
```rust
pub enum HookEvent {
    PreToolUse,
    PostToolUse,
    PostToolUseFailure,
}
```

No UserPromptSubmit. No Stop. These are NOT in the claw-code source.

### What The CC Product Does
The CC product's system prompt explicitly mentions UserPromptSubmit and Stop as
hook types. They exist in the product but not in the open-source claw-code.

### Resolution
**These hooks work in the CC product** but we can't verify their exact protocol
from source. We're using them correctly based on runtime observation, but the
stdin payload format is assumed, not verified.

**ACTION:** Document as "runtime-observed, protocol assumed" in the registry.
The hooks we depend on most (PreToolUse bash-guard, PostToolUse quality gates)
ARE source-verified and reliable.

---

## GAP 4: MEMORY.md AUTO-LOADING PATH — MEDIUM

### What We Assumed
That `memory/MEMORY.md` at the project root auto-loads into the system prompt.

### What Actually Happens
CC auto-loads memory from `~/.claude/projects/<project-hash>/memory/MEMORY.md` —
a SPECIFIC path in the user's home directory, keyed by project hash. NOT from
a `memory/` directory in the project root.

Our `memory/MEMORY.md` is at `apps/claude-harness/memory/MEMORY.md` — this is
a project file, not the auto-loaded memory path.

### Resolution
**Our memory/ directory is for GENERATED ENVIRONMENTS**, not for the harness's
own operational memory. The harness's own memory lives at:
`~/.claude/projects/C--Users-doubl-projects-apps-claude-harness/memory/`

For generated environments, the deployment step should create memory files at
the correct CC memory path for the target project, OR document that the user
needs to move them.

**ACTION:** The harness's own learning loop should use the actual CC memory path.
Generated environments should document the correct memory location.

---

## GAP 5: CLAUDE.md CHARACTER LIMIT — LOW

### What We Assumed
4,000 chars per file, 12,000 chars total. Source: claw-code `runtime/src/prompt.rs`.

### Reality
These limits come from the open-source claw-code, which is a port/reimplementation.
The CC product may have different limits. Our OPSEC CLAUDE.md is currently ~3,700
chars so it fits regardless, but we should verify on the actual product.

### Resolution
**Keep CLAUDE.md under 4K as a safe target.** If the product has higher limits,
we're just being conservative. If lower, we'd need to trim.

---

## GAP 6: TOOL NAME MISMATCHES — MEDIUM

### What We Assumed
Tool names like `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `Agent`.

### What The Source Shows
claw-code uses: `read_file`, `write_file`, `edit_file`, `bash`, `glob_search`,
`grep_search`, `WebFetch`, `WebSearch` (mixed casing).

### What The CC Product Uses
The CC product uses: `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `Agent`,
`WebSearch`, `WebFetch` (PascalCase for most).

### Resolution
**Use the CC product names** (PascalCase) since that's the platform we're generating
for. The claw-code names are its internal representations.

Our agent frontmatter uses `tools: [Read, Write, Bash, ...]` which matches the
CC product. Correct.

---

## GAP 7: TEMPLATE PLACEHOLDER RESOLUTION — LOW

### What We Assumed
Templates use `{{placeholder}}` syntax and generators fill them in.

### Reality
There is NO template engine. Generators read templates as REFERENCE PATTERNS and
produce similar output manually. The `{{placeholders}}` are documentation hints,
not machine-resolved tokens.

### Resolution
**This is fine.** The templates serve their purpose as patterns. Generators (which
are LLM agents) can read the pattern and produce domain-specific output. No code
change needed, but we should document this clearly.

---

## GAP 8: AGENT NESTING DEPTH — LOW

### What We Assumed
The orchestrator spawns agents that can spawn agents (recon-agent → scanner-agent).

### What The Source Shows
The default tool set for unknown subagent types does NOT include the `Agent` tool.
Agents can only spawn sub-agents if they have the `Agent` tool in their allowed set.

### Resolution
**Our recon-agent frontmatter includes `Agent` in its tools list**, so it CAN spawn
scanner-agent. This is correct. But we should verify that nesting works in practice
(agent → sub-agent → sub-sub-agent might hit depth limits).

---

## SUMMARY: What Must Change

| Gap | Severity | Action |
|-----|----------|--------|
| Hook format (`matcher` vs flat commands) | CRITICAL | Make hooks self-filtering via env vars |
| Agent resolution (`subagent_type` vs prompt packing) | CRITICAL | Orchestrator must READ .md files and pack into prompt |
| UserPromptSubmit/Stop hooks | MEDIUM | Document as runtime-observed, don't depend critically |
| Memory path (project root vs ~/.claude/) | MEDIUM | Fix learning loop to use correct path |
| Tool name casing | MEDIUM | Already correct (PascalCase) |
| CLAUDE.md char limit | LOW | Already under limit |
| Template resolution | LOW | Document that templates are reference patterns |
| Agent nesting | LOW | Already handled in frontmatter |
