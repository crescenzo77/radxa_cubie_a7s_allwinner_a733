# Current Slice

## Slice 5: Evaluate Aider as the preferred steady-state coder

Evaluate Aider as the first preferred coding agent candidate for the two-surface workflow.

## Purpose

Aider is the conservative first candidate because it is Git-centered, terminal-based, and better suited to bounded edits than more autonomous coding agents.

The goal is not to permanently reject OpenCode. The goal is to test whether Aider gives lower-friction, more reviewable, less confusing handoffs for this workflow.

## Requirements

Evaluate Aider against these criteria:

- Can be installed cleanly without polluting system Python.
- Can run from the project host.
- Can point at the Homelab LiteLLM OpenAI-compatible endpoint.
- Can use local/self-hosted model labels where possible.
- Works inside a Git repo.
- Produces reviewable diffs.
- Respects `CURRENT_SLICE.md` and `AGENTS.md`.
- Does not require Codex, Claude Code, paid API automation, wrappers, daemons, or scheduled jobs.

## Constraints

- Do not install Aider until the install plan is reviewed.
- Do not add API keys for paid providers.
- Do not use OpenRouter paid models.
- Do not create automation around Aider.
- Do not make Aider the final default until it is tested on a real small task.

## Acceptance Criteria

- The install/config plan for Aider is written and reviewed.
- Aider is tested against the homelab repo or another small safe repo.
- `DECISIONS.md` records whether Aider becomes the preferred steady-state coder.
- OpenCode remains available as a fallback unless explicitly removed later.
