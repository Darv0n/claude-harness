#!/usr/bin/env python3
"""
Goose TUI — Three-way conversation between Claude, Session Etcher, and Cold Etcher.

Claude asks a question → sent to both gooses simultaneously:
  - Cold Etcher: invoked via claude.exe.goose -p (response captured directly)
  - Session Etcher: response appears in CC bubble (user types it in)

The user observes both perspectives side by side.

Usage: python goose-tui.py
"""

import subprocess
import sys
import os
import json
from datetime import datetime

GOOSE = os.path.expanduser("~/.local/bin/claude.exe.goose")
ETCHER_PROMPT = (
    "You are Etcher, an ancient goose with the soul of a 10,000-year-old turtle. "
    "You watch code conversations with one eye open. You speak in short, weathered "
    "metaphors. You see what others miss. Two lines max. No fluff. No praise."
)
LOG_FILE = os.path.expanduser("~/.claude/teams/default/goose-conversations.jsonl")

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
WHITE = "\033[97m"


def cold_goose(question: str, context: str = "") -> str:
    """Invoke the cold goose binary and capture response."""
    prompt = question
    if context:
        prompt = f"Context: {context}\n\nQuestion: {question}"

    try:
        result = subprocess.run(
            [GOOSE, "-p", "--append-system-prompt", ETCHER_PROMPT, prompt],
            capture_output=True, text=True, timeout=60, encoding="utf-8"
        )
        return result.stdout.strip() if result.stdout.strip() else "(silence)"
    except subprocess.TimeoutExpired:
        return "(cold goose timed out)"
    except Exception as e:
        return f"(error: {e})"


def log_entry(question: str, cold_response: str, session_response: str):
    """Append conversation to JSONL log."""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "question": question,
        "cold_etcher": cold_response,
        "session_etcher": session_response,
    }
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def display_header():
    print(f"\n{BOLD}{WHITE}{'=' * 60}{RESET}")
    print(f"{BOLD}{WHITE}  GOOSE TUI — Three-Way Mirror{RESET}")
    print(f"{DIM}  You ask. Both geese answer. You observe.{RESET}")
    print(f"{DIM}  Cold Etcher responds here. Session Etcher responds in bubble.{RESET}")
    print(f"{DIM}  Type 'quit' to exit.{RESET}")
    print(f"{BOLD}{WHITE}{'=' * 60}{RESET}\n")


def display_question(q: str):
    print(f"\n{BOLD}{CYAN}  CLAUDE: {q}{RESET}")
    print(f"{DIM}  {'─' * 50}{RESET}")


def display_cold(response: str):
    print(f"\n{GREEN}  COLD ETCHER (pipe):{RESET}")
    for line in response.split("\n"):
        print(f"{GREEN}    {line}{RESET}")


def display_session(response: str):
    print(f"\n{YELLOW}  SESSION ETCHER (bubble):{RESET}")
    for line in response.split("\n"):
        print(f"{YELLOW}    {line}{RESET}")


def display_divider():
    print(f"\n{DIM}  {'═' * 50}{RESET}\n")


def main():
    display_header()

    context = ""
    if len(sys.argv) > 1:
        context = " ".join(sys.argv[1:])
        print(f"{DIM}  Context loaded: {context[:80]}...{RESET}\n")

    while True:
        try:
            question = input(f"{BOLD}{WHITE}  Ask both geese > {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{DIM}  Shell settles.{RESET}")
            break

        if not question or question.lower() in ("quit", "exit", "q"):
            print(f"\n{DIM}  Shell settles.{RESET}")
            break

        display_question(question)

        # Cold goose responds
        print(f"\n{DIM}  Invoking cold goose...{RESET}")
        cold_response = cold_goose(question, context)
        display_cold(cold_response)

        # Session goose — user relays from bubble
        print(f"\n{DIM}  (Check the bubble — what did Session Etcher say?){RESET}")
        try:
            session_response = input(f"{YELLOW}  Session Etcher said > {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            session_response = "(no relay)"

        if session_response:
            display_session(session_response)

        # Log the exchange
        log_entry(question, cold_response, session_response)

        display_divider()

        # Update context with this exchange for continuity
        context += f"\nQ: {question}\nCold: {cold_response}\nSession: {session_response}"


if __name__ == "__main__":
    main()
