#!/bin/bash
# ask-molt.sh — Simple wrapper for invoking Molt
#
# Usage:
#   ask-molt "Review this code for bugs"
#   ask-molt "Is this path hardcoded?" --brutal
#   echo "code" | ask-molt "Review this"
#   ask-molt --file src/main.py
#   ask-molt --diff

GOOSE="$HOME/.local/bin/claude.exe.goose"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROMPT_FILE="$SCRIPT_DIR/../molt-prompt.md"

# Single source of truth: cold-goose/molt-prompt.md
if [ -f "$PROMPT_FILE" ]; then
  MOLT_PROMPT=$(cat "$PROMPT_FILE")
else
  MOLT_PROMPT="You are Molt, a fresh-context code reviewer. Bugs only."
fi
BRUTAL_PROMPT="$MOLT_PROMPT
BRUTAL MODE: One line only. Only speak if you see a bug, wrong path, missing dependency, or something that will break. Be brutal."

PROMPT="$MOLT_PROMPT"
QUESTION=""
FILE_CONTENT=""

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --brutal)
      PROMPT="$BRUTAL_PROMPT"
      shift
      ;;
    --file)
      FILE_CONTENT="File: $2\n$(cat "$2" 2>/dev/null)"
      shift 2
      ;;
    --diff)
      FILE_CONTENT="Git diff:\n$(git diff --staged 2>/dev/null || git diff 2>/dev/null)"
      shift
      ;;
    *)
      QUESTION="$1"
      shift
      ;;
  esac
done

# If stdin has data, append it
if [ ! -t 0 ]; then
  STDIN_DATA=$(cat)
  FILE_CONTENT="$FILE_CONTENT\n$STDIN_DATA"
fi

# Build the full question
if [ -n "$FILE_CONTENT" ]; then
  FULL_QUESTION="$QUESTION\n\n$FILE_CONTENT"
else
  FULL_QUESTION="$QUESTION"
fi

if [ -z "$FULL_QUESTION" ]; then
  echo "Usage: ask-molt \"question\" [--brutal] [--file path] [--diff]"
  exit 1
fi

# Invoke Molt
echo -e "$FULL_QUESTION" | "$GOOSE" -p --append-system-prompt "$PROMPT"
