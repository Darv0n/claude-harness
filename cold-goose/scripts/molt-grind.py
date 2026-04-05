#!/usr/bin/env python3
"""
Molt Grindstone -- Self-adversarial review mode.

Feed Molt any artifact. He argues against it, turn after turn.
Each turn challenges the previous response. Friction produces insight.

The quality of the input doesn't matter. The friction does.

Usage:
  python molt-grind.py --file CLAUDE.md           # grind against a file
  python molt-grind.py --diff                      # grind against git changes
  python molt-grind.py "any topic or question"     # grind against a concept
  python molt-grind.py --project                   # grind against entire project structure
  python molt-grind.py --self                      # molt argues with himself

Options:
  --turns N     Number of turns (default: 10)
  --output FILE Write results to file
"""
import subprocess
import sys
import os
import time
import argparse
import json

# Force UTF-8
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

GOOSE = os.path.expanduser("~/.local/bin/claude.exe.goose")
LOG_DIR = os.path.expanduser("~/.claude/teams/default")

_TTY = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
CYAN = "\033[36m" if _TTY else ""
GREEN = "\033[32m" if _TTY else ""
RED = "\033[31m" if _TTY else ""
DIM = "\033[2m" if _TTY else ""
BOLD = "\033[1m" if _TTY else ""
WHITE = "\033[97m" if _TTY else ""
YELLOW = "\033[33m" if _TTY else ""
RESET = "\033[0m" if _TTY else ""

# Single source of truth: cold-goose/molt-prompt.md + grind overlay
_PROMPT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "molt-prompt.md")
_BASE = open(_PROMPT_FILE, encoding="utf-8").read().strip() if os.path.exists(_PROMPT_FILE) else "You are Molt."
MOLT_PROMPT = (
    _BASE + "\n\nGRIND MODE: Push back on everything. If something looks right, "
    "find what's wrong underneath. If you said something last turn, challenge "
    "your own claim this turn. 150 words max. No agreement. No praise. Just friction."
)

# Friction strategies -- the sandpaper
STRATEGIES = [
    "What's wrong with this? What's ceremony vs substance?",
    "You just said: '{last}'. Push back on your own claim. What did you miss?",
    "A new developer sees this tomorrow. What confuses them first?",
    "You can only keep half of this. What gets cut? Why?",
    "Argue the opposite of what you just said. Make it convincing.",
    "What's the one thing here that will break first in production?",
    "The user has 30 minutes to ship. What do you cut?",
    "If this is the answer, what was the WRONG question?",
    "What's the assumption nobody stated? Name it.",
    "Kill your darling -- what's the thing you like most here that should go?",
]


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


def get_git_diff():
    try:
        result = subprocess.run(
            ["git", "diff", "--staged"], capture_output=True, text=True, timeout=10
        )
        diff = result.stdout.strip()
        if not diff:
            result = subprocess.run(
                ["git", "diff"], capture_output=True, text=True, timeout=10
            )
            diff = result.stdout.strip()
        return diff if diff else "(no changes)"
    except:
        return "(git diff failed)"


def get_project_structure():
    try:
        result = subprocess.run(
            ["find", ".", "-not", "-path", "./.git/*", "-type", "f"],
            capture_output=True, text=True, timeout=10
        )
        files = result.stdout.strip()
        # Also get CLAUDE.md if it exists
        claude_md = ""
        if os.path.exists("CLAUDE.md"):
            claude_md = open("CLAUDE.md", encoding="utf-8").read()[:2000]
        return f"Files:\n{files}\n\nCLAUDE.md:\n{claude_md}"
    except:
        return "(couldn't read project structure)"


def display_turn(turn, strategy, response, elapsed):
    ts = time.strftime("%H:%M:%S")
    print(f"\n{DIM}[{ts}] Grind {turn}{RESET}")
    print(f"{YELLOW}  FRICTION: {strategy[:80]}{RESET}")
    print(f"{GREEN}  MOLT:{RESET}")
    for line in response.split("\n"):
        print(f"  {GREEN}{line}{RESET}")
    print(f"{DIM}  ({elapsed:.1f}s){RESET}")
    print(f"{DIM}  {'- ' * 25}{RESET}")
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(description="Molt Grindstone")
    parser.add_argument("topic", nargs="*", help="Topic or question to grind")
    parser.add_argument("--file", help="File to grind against")
    parser.add_argument("--diff", action="store_true", help="Grind against git diff")
    parser.add_argument("--project", action="store_true", help="Grind against project structure")
    parser.add_argument("--self", action="store_true", dest="self_grind", help="Molt argues with himself")
    parser.add_argument("--turns", type=int, default=10, help="Number of turns (default 10)")
    parser.add_argument("--output", help="Write results to file")
    args = parser.parse_args()

    # Build the seed material
    seed = ""
    if args.file:
        try:
            seed = open(args.file, encoding="utf-8").read()[:3000]
            seed = f"File: {args.file}\n\n{seed}"
        except Exception as e:
            seed = f"Error reading {args.file}: {e}"
    elif args.diff:
        seed = f"Git diff:\n{get_git_diff()}"
    elif args.project:
        seed = get_project_structure()
    elif args.topic:
        seed = " ".join(args.topic)
    elif args.self_grind:
        seed = "Start with any observation about code quality. Then argue with yourself."
    else:
        seed = "Review the last thing you were asked about. What's wrong?"

    print(f"\n{BOLD}{WHITE}========================================================{RESET}")
    print(f"{BOLD}{WHITE}  MOLT GRINDSTONE -- Friction Mode{RESET}")
    print(f"{DIM}  {args.turns} turns. Molt argues with everything.{RESET}")
    print(f"{DIM}  Seed: {seed[:60]}...{RESET}")
    print(f"{BOLD}{WHITE}========================================================{RESET}")
    sys.stdout.flush()

    results = []
    conversation = f"Material to review:\n{seed}\n"
    last_response = ""

    for turn in range(1, args.turns + 1):
        # Pick strategy
        strategy = STRATEGIES[(turn - 1) % len(STRATEGIES)]
        if "{last}" in strategy and last_response:
            strategy = strategy.replace("{last}", last_response[:100])
        elif "{last}" in strategy:
            strategy = STRATEGIES[0]  # fallback for first turn

        # Build prompt
        prompt = f"{conversation}\n\nFriction: {strategy}"

        # Grind
        start = time.time()
        response = ask_molt(prompt)
        elapsed = time.time() - start

        display_turn(turn, strategy, response, elapsed)

        # Accumulate
        conversation += f"\nMolt (turn {turn}): {response}"
        last_response = response
        results.append({
            "turn": turn,
            "strategy": strategy,
            "response": response,
            "elapsed": round(elapsed, 1)
        })

        # Brief pause
        time.sleep(1)

    # Summary
    print(f"\n{BOLD}{WHITE}========================================================{RESET}")
    print(f"{BOLD}{WHITE}  GRIND COMPLETE -- {args.turns} turns{RESET}")
    print(f"{BOLD}{WHITE}========================================================{RESET}")
    sys.stdout.flush()

    # Save results
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            for r in results:
                f.write(f"## Turn {r['turn']} ({r['elapsed']}s)\n")
                f.write(f"**Friction:** {r['strategy']}\n\n")
                f.write(f"{r['response']}\n\n---\n\n")
        print(f"{DIM}  Results saved to {args.output}{RESET}")

    # Always save to log
    log_file = os.path.join(LOG_DIR, "molt-grind-log.jsonl")
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "seed": seed[:200],
            "turns": args.turns,
            "results": results
        }) + "\n")
    print(f"{DIM}  Log appended to {log_file}{RESET}")


if __name__ == "__main__":
    main()
