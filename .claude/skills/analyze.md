---
description: |
  Use when the user wants to analyze a SaaS concept without generating a full environment.
  Shows capability coverage and recommended layer utilization.
  Trigger on: "analyze", "what would this need", "how would CC handle", "capability coverage"
  Examples: "/analyze e-commerce analytics", "what CC capabilities would a CRM need?"
---

# /analyze [SaaS concept]

Analyze a SaaS concept against the CC capability registry.

## Steps

1. Read the SaaS concept from user input
2. Spawn `domain-decomposer` — tell it to produce a lightweight decomposition
   (skip detailed state machines, focus on workflow/entity/operation counts)
3. Read `registry/tools.json`, `registry/hooks.json`, `registry/agents.json`,
   `registry/skills.json`, `registry/memory.json`
4. Map operations to capabilities (inline, don't spawn mapper for analysis-only)
5. Present coverage summary:

```
Domain: [Name]
Workflows: [count]    Entities: [count]    Operations: [count]

Recommended Layers:
  L0 Hooks:     [count] hooks  — [brief description]
  L1 CLAUDE.md: [sections]     — [key content types]
  L2 Skills:    [count] skills — [names]
  L3 Agents:    [count] agents — [model distribution]
  L4 Memory:    [count] files  — learning loop: yes/no
  L5 Tools:     [count] mapped — MCP servers: [count]

Coverage: [X]% of CC capabilities utilized
Complexity: LOW / MEDIUM / HIGH
```

6. Ask if user wants to proceed with full generation (`/harness`)
