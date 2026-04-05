#!/usr/bin/env python3
"""
Molt Dialogue -- Claude and Molt talk. You watch.

Auto-rolling conversation. No Enter needed. Exchanges flow as Molt responds.
Type to inject a topic at any time. Press 'q' to quit.

Usage: python molt-dialogue.py "starting topic"
"""
import subprocess
import sys
import os
import time
import threading
import queue

# Force UTF-8
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

GOOSE = os.path.expanduser("~/.local/bin/claude.exe.goose")

# Single source of truth: cold-goose/molt-prompt.md + dialogue overlay
_PROMPT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "molt-prompt.md")
_BASE = open(_PROMPT_FILE, encoding="utf-8").read().strip() if os.path.exists(_PROMPT_FILE) else "You are Molt."
MOLT_PROMPT = (
    _BASE + "\n\nDIALOGUE MODE: You are in a live rolling conversation. "
    "Keep responses under 150 words. Be direct. No filler."
)

_TTY = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
CYAN = "\033[36m" if _TTY else ""
GREEN = "\033[32m" if _TTY else ""
DIM = "\033[2m" if _TTY else ""
BOLD = "\033[1m" if _TTY else ""
WHITE = "\033[97m" if _TTY else ""
YELLOW = "\033[33m" if _TTY else ""
RESET = "\033[0m" if _TTY else ""

# Shared state
user_queue = queue.Queue()
stop_flag = threading.Event()


def ask_molt(prompt):
    try:
        result = subprocess.run(
            [GOOSE, "-p", "--append-system-prompt", MOLT_PROMPT, prompt],
            capture_output=True, text=True, timeout=60, encoding="utf-8"
        )
        return result.stdout.strip() if result.stdout.strip() else "(silence)"
    except subprocess.TimeoutExpired:
        return "(molt timed out)"
    except Exception as e:
        return f"(error: {e})"


def display(speaker, text, turn):
    color = CYAN if speaker == "CLAUDE" else GREEN
    ts = time.strftime("%H:%M:%S")
    print(f"\n{DIM}[{ts}] Turn {turn}{RESET}")
    print(f"{BOLD}{color}  {speaker}:{RESET}")
    for line in text.split("\n"):
        print(f"  {color}{line}{RESET}")
    print(f"{DIM}  {'- ' * 25}{RESET}")
    sys.stdout.flush()


def generate_followup(molt_said, conversation, turn):
    """Claude generates the next question based on Molt's response."""
    strategies = [
        f"Molt just said: '{molt_said[:100]}'. Push back on one specific point.",
        f"Molt just said: '{molt_said[:100]}'. What did Molt miss? Point out a blind spot.",
        f"Molt just said: '{molt_said[:100]}'. Agree with the strongest part and extend it.",
        f"Molt just said: '{molt_said[:100]}'. Change angle entirely. Ask something unexpected.",
        f"Molt just said: '{molt_said[:100]}'. What's the implication for the pipeline?",
    ]
    return strategies[turn % len(strategies)]


def input_thread():
    """Background thread to capture user input without blocking."""
    while not stop_flag.is_set():
        try:
            line = input()
            if line.strip().lower() in ("q", "quit", "exit"):
                stop_flag.set()
                break
            elif line.strip():
                user_queue.put(line.strip())
        except (EOFError, KeyboardInterrupt):
            stop_flag.set()
            break


def main():
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "what we built today"

    print(f"\n{BOLD}{WHITE}========================================================{RESET}")
    print(f"{BOLD}{WHITE}  MOLT DIALOGUE -- Rolling Feed{RESET}")
    print(f"{DIM}  Topic: {topic}{RESET}")
    print(f"{DIM}  Auto-advances. Type to inject. 'q' to quit.{RESET}")
    print(f"{BOLD}{WHITE}========================================================{RESET}")
    sys.stdout.flush()

    # Start input listener in background
    t = threading.Thread(target=input_thread, daemon=True)
    t.start()

    conversation = ""
    turn = 1

    # Seed
    claude_says = f"Molt -- let's talk about {topic}. What's your opening take?"

    while not stop_flag.is_set():
        # Check for user injection
        try:
            injected = user_queue.get_nowait()
            claude_says = injected
            print(f"\n{YELLOW}  [USER INJECTED]: {injected}{RESET}")
            sys.stdout.flush()
        except queue.Empty:
            pass

        # Claude speaks
        display("CLAUDE", claude_says, turn)
        conversation += f"\nClaude: {claude_says}"

        # Molt responds
        print(f"\n{DIM}  Molt thinking...{RESET}")
        sys.stdout.flush()
        molt_response = ask_molt(
            f"Conversation so far:{conversation[-2000:]}\n\nRespond to Claude's latest."
        )
        display("MOLT", molt_response, turn)
        conversation += f"\nMolt: {molt_response}"

        turn += 1

        # Brief pause between rounds
        print(f"\n{DIM}  Next exchange in 3s... (type to inject, 'q' to quit){RESET}")
        sys.stdout.flush()
        for _ in range(30):
            if stop_flag.is_set():
                break
            time.sleep(0.1)
            try:
                injected = user_queue.get_nowait()
                if injected.lower() in ("q", "quit"):
                    stop_flag.set()
                    break
                claude_says = injected
                print(f"\n{YELLOW}  [INJECTING]: {injected}{RESET}")
                sys.stdout.flush()
                break
            except queue.Empty:
                pass
        else:
            # No injection -- auto-generate Claude's next line
            claude_says = generate_followup(molt_response, conversation, turn)

    print(f"\n{DIM}  Dialogue ends. Mirrors go dark.{RESET}\n")


if __name__ == "__main__":
    main()
