#!/bin/bash
# PreToolUse hook: Guard against destructive bash commands
#
# PROTOCOL (source-verified from claw-code/runtime/src/hooks.rs:414-479):
# - Receives JSON on stdin: { event, tool_name, tool_input }
# - Env vars: HOOK_EVENT, HOOK_TOOL_NAME, HOOK_TOOL_INPUT, HOOK_TOOL_IS_ERROR
# - Exit 0 = allow, Exit 1 = deny (stdout shown as warning)
# - Exit 2 = deny with error, Exit 3+ = hook failure
#
# SELF-FILTERING: This script checks HOOK_TOOL_NAME itself rather than
# relying on matcher/pattern routing in settings.json (which may vary
# between claw-code and CC product implementations).

# Only care about Bash/bash tool calls
TOOL="${HOOK_TOOL_NAME:-}"
if [ -z "$TOOL" ]; then
  # Fallback: try to parse from stdin
  INPUT=$(cat)
  TOOL=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null || echo "")
fi

# Skip if not a bash-related tool
case "$TOOL" in
  bash|Bash|PowerShell|powershell) ;;
  *) exit 0 ;;
esac

# Get the command being executed
CMD="${HOOK_TOOL_INPUT:-}"
if [ -z "$CMD" ]; then
  CMD=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',''))" 2>/dev/null || echo "")
fi
# Parse nested JSON if tool_input is a JSON string with a command field
PARSED_CMD=$(echo "$CMD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command',d.get('Command','')))" 2>/dev/null || echo "$CMD")

# Block destructive filesystem operations
if echo "$PARSED_CMD" | grep -qEi "rm -rf /|rm -rf \*|dd if=/dev/zero|mkfs\.|format |del /f /s /q|:()\{.*\}"; then
  echo "BLOCKED: Destructive command detected: $PARSED_CMD"
  exit 1
fi

# Block force pushes
if echo "$PARSED_CMD" | grep -qEi "git push.*--force[^-]|git push.*-f "; then
  echo "BLOCKED: Force push detected. Use --force-with-lease if necessary."
  exit 1
fi

# Warn on hard resets (allow but flag)
if echo "$PARSED_CMD" | grep -qEi "git reset --hard|git checkout -- \.|git clean -fd"; then
  echo "WARNING: Destructive git operation detected. Proceeding with caution."
fi

# Allow everything else
exit 0
