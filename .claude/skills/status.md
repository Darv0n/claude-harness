---
description: |
  Use when the user wants to see the current state of the pentest team — targets,
  extractions, exploit maps, environment health.
  Examples: "/status", "dashboard", "what's our current state",
  "show me the team status", "where are we"
---

# /status

Show the OPSEC team dashboard.

## Steps

1. Read `memory/targets/` — list all recon'd targets with status
2. Read `memory/patterns/` — count extracted patterns
3. Read `memory/exploits/` — count mapped exploits
4. Read `memory/techniques/` — count learned techniques
5. Read `memory/analytics/` — latest performance metrics
6. Present dashboard:

```
OPSEC PENTEST TEAM — Status Dashboard

TARGETS
  [name] — status: recon'd / extracted / mapped / exploited
  ...

PATTERNS EXTRACTED: [count] across [subsystem count] subsystems
EXPLOITS MAPPED:    [count] (HIGH: X, MEDIUM: Y, LOW: Z)
TECHNIQUES LEARNED: [count]

ENVIRONMENT HEALTH
  Agents: [count] ([model distribution])
  Skills: [count]
  Hooks:  [count] ([event distribution])
  Memory: [entry count] entries, [file count] files

LAST AUDIT: [date] — Risk: [level]
```

## Memory
- Reads: all memory directories (read-only)
