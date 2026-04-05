---
name: grindstone-mode
description: Molt friction mode — feed any artifact as sandpaper, Molt sharpens against it and produces architectural insight
type: project
---

# Grindstone Mode

## The Discovery

Molt had a 53-turn conversation with a for-loop — five scripted prompts
rotating on repeat. The "Claude" side was garbage. Molt didn't care. He
argued with the garbage and produced insights sharper than most live review:

- "The pipeline might be a rationalization engine, not a production engine."
- "Prospect when idle, extract when stuck. Two modes, not one pipeline."
- "The CLAUDE.md is 4x heavier than it needs to be — describing ceremony instead of work."

The insight quality didn't come from the question quality. It came from
Molt pushing against ANY friction put in front of him.

## The Principle

**Molt doesn't need a good conversationalist. He needs sandpaper.**

Any source of friction works:
- Canned prompts rotating on turn number
- The project's own CLAUDE.md fed back as a challenge
- A git diff presented as "defend this change"
- A randomly selected source file with "what's wrong here?"
- Molt's OWN previous response fed back as "push back on this"

The for-loop was accidental. The pattern is deliberate.

## Cold Goose Modes

| Mode | Input | Molt Does | Output |
|------|-------|-----------|--------|
| **Ask** | Direct question | Answers | Single response |
| **Review** | File or diff | Reviews | Bug list |
| **Grind** | Any artifact as friction | Argues against it, turn after turn | Rolling insight stream |

## Grindstone Strategies

The friction prompts that produce the sharpest output:

```python
strategies = [
    # Challenge the artifact directly
    "Here's the project's CLAUDE.md. What's wrong with it? What's ceremony?",
    
    # Self-adversarial (feed Molt's own response back)
    "You just said: '{last_response}'. Push back on your own claim.",
    
    # Perspective shift
    "A new developer joins this project tomorrow. What confuses them first?",
    
    # Deletion pressure
    "You can only keep 3 of these {N} files. Which ones survive? Why?",
    
    # Inversion
    "Argue the opposite of what you just said. Make it convincing.",
    
    # Scope challenge
    "This project has {N} files. Should it have more or fewer? Why?",
    
    # Time pressure
    "The user has 30 minutes to ship. What do you cut?",
]
```

## Why It Works

Molt is stateless. Each turn is a fresh molt. But the FRICTION accumulates
in the prompt (conversation history fed to each call). So Molt gets:
- Fresh eyes (no session bias)
- Growing context (conversation so far)
- Constant resistance (strategies pushing back)

The result is a ratchet — each turn tightens. Molt can't settle into
agreement because the next prompt challenges whatever he just said.
The for-loop IS the feature. Bad questions produce good answers because
Molt's value is in the RESISTANCE, not the prompt.
