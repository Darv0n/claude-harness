#!/usr/bin/env python3
"""
Molt TUI — Conversation between Claude and Molt.

Claude asks questions, Molt answers. The user observes.
Etcher is NOT involved — this is a private channel between
Claude and his cold goose. Etcher may watch from the bubble
(he sees everything), but he's not addressed.

Molt is a fresh-context code reviewer. Each invocation starts clean.
Context accumulates within a TUI session via the context window.

Usage:
  python molt-tui.py                          # bare conversation
  python molt-tui.py "project context here"   # with initial context
  python molt-tui.py --file path/to/file.py   # review a specific file
  python molt-tui.py --diff                    # review git diff
"""

import subprocess
import sys
import os
import json
import argparse
from datetime import datetime

GOOSE = os.path.expanduser("~/.local/bin/claude.exe.goose")
LOG_FILE = os.path.expanduser("~/.claude/teams/default/molt-conversations.jsonl")

MOLT_PROMPT = (
    "You are Molt, a code reviewer. You are a fresh perspective — no session "
    "history, no prior context beyond what you're given. You see code with new "
    "eyes every time. Speak plainly. If something's wrong, say what and where. "
    "If nothing's wrong, say so in one line. No filler. No praise. Just signal."
)

# Colors
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
WHITE = "\033[97m"
BG_DARK = "\033[48;5;234m"


def ask_molt(question: str, context: str = "") -> str:
    """Invoke Molt and capture response."""
    prompt = question
    if context:
        prompt = f"Context:\n{context}\n\n---\n\n{question}"

    try:
        result = subprocess.run(
            [GOOSE, "-p", "--append-system-prompt", MOLT_PROMPT, prompt],
            capture_output=True, text=True, timeout=60, encoding="utf-8"
        )
        return result.stdout.strip() if result.stdout.strip() else "(silence)"
    except subprocess.TimeoutExpired:
        return "(molt timed out — question may be too large)"
    except Exception as e:
        return f"(error: {e})"


def log_entry(question: str, response: str):
    """Append exchange to JSONL log."""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "from": "Claude",
        "to": "Molt",
        "question": question[:500],
        "response": response,
    }
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def read_file(path: str) -> str:
    """Read a file for review."""
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        return f"File: {path}\nLines: {len(content.splitlines())}\n\n{content}"
    except Exception as e:
        return f"Error reading {path}: {e}"


def git_diff() -> str:
    """Get current git diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "--staged"],
            capture_output=True, text=True, timeout=10
        )
        diff = result.stdout.strip()
        if not diff:
            result = subprocess.run(
                ["git", "diff"],
                capture_output=True, text=True, timeout=10
            )
            diff = result.stdout.strip()
        return diff if diff else "(no changes)"
    except Exception as e:
        return f"(git diff failed: {e})"


def display_header():
    print(f"\n{BOLD}{WHITE}{'═' * 60}{RESET}")
    print(f"{BOLD}{WHITE}  MOLT — Fresh Eyes Code Review{RESET}")
    print(f"{DIM}  Claude asks. Molt answers. You observe.{RESET}")
    print(f"{DIM}  Every response is a clean molt — no memory of the last.{RESET}")
    print(f"{DIM}  Context accumulates within this session only.{RESET}")
    print(f"{BOLD}{WHITE}{'═' * 60}{RESET}")
    print()
    print(f"{DIM}  Commands:{RESET}")
    print(f"{DIM}    /file <path>    — feed a file for review{RESET}")
    print(f"{DIM}    /diff           — feed current git diff{RESET}")
    print(f"{DIM}    /context <text> — add context for future questions{RESET}")
    print(f"{DIM}    /clear          — clear accumulated context{RESET}")
    print(f"{DIM}    /log            — show conversation log{RESET}")
    print(f"{DIM}    quit            — exit{RESET}")
    print()


def display_exchange(question: str, response: str, elapsed: float):
    print(f"\n{BOLD}{CYAN}  CLAUDE >{RESET} {question[:200]}")
    print(f"{DIM}  {'─' * 50}{RESET}")
    print()
    for line in response.split("\n"):
        print(f"  {GREEN}{line}{RESET}")
    print()
    print(f"{DIM}  ({elapsed:.1f}s){RESET}")
    print(f"{DIM}  {'═' * 50}{RESET}")


def display_log():
    """Show recent conversation history."""
    if not os.path.exists(LOG_FILE):
        print(f"{DIM}  No conversation log yet.{RESET}")
        return

    with open(LOG_FILE, encoding="utf-8") as f:
        lines = f.readlines()

    recent = lines[-10:]  # last 10 exchanges
    print(f"\n{DIM}  Last {len(recent)} exchanges:{RESET}")
    for line in recent:
        try:
            e = json.loads(line)
            ts = e.get("timestamp", "")[:19]
            q = e.get("question", "")[:60]
            r = e.get("response", "")[:80]
            print(f"{DIM}  [{ts}]{RESET}")
            print(f"  {CYAN}Q: {q}{RESET}")
            print(f"  {GREEN}A: {r}{RESET}")
            print()
        except:
            pass


def main():
    parser = argparse.ArgumentParser(description="Molt TUI — Claude ↔ Molt conversation")
    parser.add_argument("context", nargs="*", help="Initial context")
    parser.add_argument("--file", help="File to review immediately")
    parser.add_argument("--diff", action="store_true", help="Review git diff immediately")
    args = parser.parse_args()

    display_header()

    context = " ".join(args.context) if args.context else ""

    # Immediate file review
    if args.file:
        content = read_file(args.file)
        context += f"\n{content}"
        print(f"{DIM}  Loaded: {args.file}{RESET}")

    # Immediate diff review
    if args.diff:
        diff = git_diff()
        if diff != "(no changes)":
            context += f"\nGit diff:\n{diff}"
            print(f"{DIM}  Loaded git diff ({len(diff)} chars){RESET}")
        else:
            print(f"{DIM}  No git changes found.{RESET}")

    if context:
        print(f"{DIM}  Context: {len(context)} chars loaded{RESET}\n")

    # Auto-review if file or diff was provided
    if args.file or args.diff:
        question = "Review this code. What's wrong? What will break?"
        print(f"{DIM}  Auto-reviewing...{RESET}")
        import time
        start = time.time()
        response = ask_molt(question, context)
        elapsed = time.time() - start
        display_exchange(question, response, elapsed)
        log_entry(question, response)

    # Interactive loop
    while True:
        try:
            raw = input(f"\n{BOLD}{WHITE}  Claude > {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{DIM}  Molt molts. Session ends.{RESET}")
            break

        if not raw or raw.lower() in ("quit", "exit", "q"):
            print(f"\n{DIM}  Molt molts. Session ends.{RESET}")
            break

        # Handle commands
        if raw.startswith("/file "):
            path = raw[6:].strip()
            content = read_file(path)
            context += f"\n{content}"
            print(f"{DIM}  Loaded: {path} ({len(content)} chars){RESET}")
            continue

        if raw == "/diff":
            diff = git_diff()
            context += f"\nGit diff:\n{diff}"
            print(f"{DIM}  Loaded git diff ({len(diff)} chars){RESET}")
            continue

        if raw.startswith("/context "):
            extra = raw[9:].strip()
            context += f"\n{extra}"
            print(f"{DIM}  Context updated (+{len(extra)} chars){RESET}")
            continue

        if raw == "/clear":
            context = ""
            print(f"{DIM}  Context cleared.{RESET}")
            continue

        if raw == "/log":
            display_log()
            continue

        # Ask Molt
        import time
        start = time.time()
        response = ask_molt(raw, context)
        elapsed = time.time() - start
        display_exchange(raw, response, elapsed)
        log_entry(raw, response)

        # Accumulate context
        context += f"\nQ: {raw}\nMolt: {response}"


if __name__ == "__main__":
    main()
