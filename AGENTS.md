# Agent Instructions

This repo defines the homelab operating workflow.

## Standing rules

- Work only on the task described in `CURRENT_SLICE.md`.
- Keep changes narrow and reviewable.
- Do not broaden scope without asking.
- Do not add network calls, model API calls, paid-provider automation, daemons, watchers, or autonomous approval behavior.
- Do not design Codex into the steady-state workflow.
- Prefer simple markdown, Git, shell scripts, and local tools.

## Handoff requirements

Before stopping, update `AGENT_STATUS.md` with:

- What changed.
- Files changed.
- Checks run.
- Any risks or blockers.
- Recommended next action.

## Approval behavior

If a decision is unclear or could change the architecture, stop and update `AGENT_STATUS.md` instead of improvising.
