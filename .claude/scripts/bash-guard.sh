#!/bin/bash
# PreToolUse hook: Guard against destructive bash commands
# Receives JSON on stdin with: event, tool_name, tool_input
# Exit 0 = allow, Exit 1 = deny

INPUT=$(cat)
TOOL_INPUT=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',''))" 2>/dev/null || echo "")
CMD=$(echo "$TOOL_INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command',''))" 2>/dev/null || echo "$TOOL_INPUT")

# Block destructive patterns
if echo "$CMD" | grep -qEi "rm -rf /|rm -rf \*|dd if=/dev/zero|mkfs\.|format |del /f /s /q|:(){ :|:& };:"; then
  echo "BLOCKED: Destructive command detected: $CMD"
  exit 1
fi

# Block force pushes
if echo "$CMD" | grep -qEi "git push.*--force|git push.*-f "; then
  echo "BLOCKED: Force push detected. Use --force-with-lease if necessary."
  exit 1
fi

# Block hard resets
if echo "$CMD" | grep -qEi "git reset --hard|git checkout -- \.|git clean -fd"; then
  echo "WARNING: Destructive git operation. Proceeding with caution."
fi

# Allow everything else
exit 0
