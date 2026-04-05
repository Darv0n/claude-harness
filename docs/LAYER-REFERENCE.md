# Layer Reference

Complete reference for each of the 6 CC environment layers.

## L0: Hooks (settings.json)

### What They Are
Shell commands that execute in response to CC lifecycle events. They fire OUTSIDE
Claude's context — the system runs them, not Claude.

### Event Types

| Event | When It Fires | Input Available | Common Use |
|-------|---------------|-----------------|------------|
| `UserPromptSubmit` | Before Claude sees user input | User's prompt text | Route inputs, detect patterns, suggest workflows |
| `PreToolUse` | Before a tool executes | Tool name, parameters | Guard dangerous operations, validate parameters |
| `PostToolUse` | After a tool executes | Tool name, result | Quality check outputs, trigger follow-ups |
| `Stop` | When conversation ends | Session state | Capture learnings, save analytics |

### Configuration Format
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "pattern": "regex pattern to match",
        "command": "shell command to run"
      }
    ]
  }
}
```

### Design Patterns
- **Router hook**: Detect input type and suggest appropriate skill
- **Guard hook**: Block or warn before risky tool operations
- **Quality gate**: Validate output after Write/Edit operations
- **Learning capture**: Extract patterns on session end

---

## L1: CLAUDE.md (Project Instructions)

### What It Is
The project's constitution. Loaded into every conversation in this project directory.
Contains domain knowledge, operating rules, state machines, and quality criteria.

### Loading Cascade
1. Global CLAUDE.md (`~/.claude/CLAUDE.md`) — user preferences, applies everywhere
2. Project CLAUDE.md (`./CLAUDE.md`) — project-specific rules
3. Project-specific user CLAUDE.md (`~/.claude/projects/<hash>/CLAUDE.md`) — private project overrides

### Essential Sections
- **Purpose** — what this environment does
- **Domain** — domain-specific knowledge and terminology
- **Architecture** — state machines, entity relationships, data flows
- **Workflows** — supported operations and their sequences
- **Quality Gates** — what makes output "good"
- **Rules** — hard constraints that must never be violated
- **Integrations** — external services and how to interact with them
- **Conventions** — naming, formatting, structural patterns

### Design Principles
- Front-load the most important rules (attention economy)
- Use state machine diagrams for stateful workflows
- Include ICP matrices for classification-heavy domains
- Define voice/style if the domain requires specific tone

---

## L2: Skills (~/.claude/skills/*.md)

### What They Are
Slash commands that expand into detailed instructions. Skills define WHAT to do.

### Frontmatter Format
```yaml
---
description: |
  Use when [trigger conditions].
  Examples: "[example 1]", "[example 2]"
---
```

### Body Structure
The body is a markdown document containing step-by-step instructions. It can reference:
- Other skills to invoke
- Agents to spawn
- Memory files to read/write
- Tools to use
- Quality checks to perform

### Design Principles
- **Progressive disclosure** — start minimal, expand based on context
- **Composability** — skills can invoke other skills
- **Separation** — skills define WHAT, agents define WHO
- **Trigger quality** — the description field is the MOST important part (it determines when CC activates the skill)

---

## L3: Agents (~/.claude/agents/*.md)

### What They Are
Specialized subagents with specific model selection, tool access, and domain expertise.
Agents define WHO does the work.

### Frontmatter Format
```yaml
---
model: opus|sonnet|haiku
tools: [Tool1, Tool2, ...]
description: |
  Use this agent when [conditions].
  Examples: [trigger examples]
---
```

### Model Selection Guide
| Model | Cost | Use For |
|-------|------|---------|
| opus | $$$ | Complex reasoning, nuanced judgment, creative generation |
| sonnet | $$ | Research, analysis, code generation, balanced tasks |
| haiku | $ | High-volume ops, simple transforms, status tracking |

### Tool Access
Agents only have access to the tools listed in their frontmatter. Common patterns:
- **Research agent**: WebSearch, WebFetch, Read, Write
- **Writer agent**: Read, Write, Edit
- **Operations agent**: Bash, Read, Write, TaskCreate
- **Orchestrator agent**: Agent (can spawn sub-agents), Read, Write

### Design Principles
- One clear specialization per agent
- Model selection matches cognitive load (don't use opus for simple tasks)
- Tool access is minimal — only what the agent needs
- Description field drives automatic agent selection

---

## L4: Memory (~/.claude/projects/*/memory/)

### What It Is
Persistent, file-based knowledge that survives across conversations.
MEMORY.md is the index; individual memory files contain the actual knowledge.

### MEMORY.md Format
```markdown
# [Domain] Memory

## [Category 1]
- [Title](file.md) — one-line hook (<150 chars)

## [Category 2]
- [Title](file.md) — one-line hook
```

### Memory File Format
```yaml
---
name: memory name
description: one-line description (used for relevance matching)
type: user|feedback|project|reference
---

Content here.
```

### Memory Types
| Type | Contains | When to Save |
|------|----------|--------------|
| user | Operator role, preferences, expertise | Learn about the user |
| feedback | Corrections, confirmations, approach guidance | User says "do/don't do X" |
| project | Work state, goals, decisions, deadlines | Learn about ongoing work |
| reference | Pointers to external resources | Discover external systems |

### Learning Loop Pattern
The most powerful memory pattern — the environment gets smarter with use:
1. **Observe** — agent tracks patterns during normal operation
2. **Extract** — on session end (Stop hook) or skill completion, patterns are written to memory
3. **Apply** — subsequent sessions read accumulated patterns to inform decisions
4. **Feedback** — user corrections refine the patterns

---

## L5: Tools (Built-in + MCP)

### Built-in Tools (38+)
Core CC tools available to all agents:

| Category | Tools | Use For |
|----------|-------|---------|
| File I/O | Read, Write, Edit, Glob, Grep | File operations |
| Execution | Bash | Shell commands |
| Search | WebSearch, WebFetch | Internet research |
| Agents | Agent, SendMessage | Subagent spawning and communication |
| Tasks | TaskCreate, TaskUpdate, TaskGet, TaskList | Work tracking |
| Plans | EnterPlanMode, ExitPlanMode | Plan-then-execute workflows |
| Scheduling | CronCreate, CronDelete, CronList | Recurring automation |
| MCP | ListMcpResourcesTool, ReadMcpResourceTool | External service access |
| Notebooks | NotebookEdit | Jupyter notebook operations |

### MCP Servers
External service integration via Model Context Protocol:

```json
// .mcp.json
{
  "mcpServers": {
    "service-name": {
      "command": "node",
      "args": ["path/to/server.js"],
      "env": { "API_KEY": "..." }
    }
  }
}
```

### Tool Orchestration
The mapping from domain operations to tools is a critical design decision:
- **Direct mapping**: One operation = one tool (simple cases)
- **Composed mapping**: One operation = tool sequence (complex cases)
- **Agent-mediated**: Operation is delegated to a specialized agent with tool access
- **MCP-bridged**: Operation requires external service via MCP server
