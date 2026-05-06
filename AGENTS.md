# Agent Instructions

This repo defines the homelab operating workflow.

## Primary rule

Work only on the task described in `CURRENT_SLICE.md`.

Do not broaden scope, add services, introduce automation, or change architecture unless explicitly instructed.

## Standing constraints

Do not add:

- Network calls.
- Model API calls.
- Paid-provider automation.
- Codex automation.
- Claude/Codex wrappers.
- Daemons.
- Watchers.
- Autonomous approval behavior.
- MCP failure-supervision.
- Memory-system integration.
- Hidden background jobs.

Prefer:

- Simple markdown.
- Git history.
- Local shell scripts.
- Local/self-hosted tools.
- Small, reviewable changes.

## Before making changes

Read:

- `PROJECT_PLAN.md`
- `CURRENT_SLICE.md`
- `DECISIONS.md`
- `AGENT_STATUS.md`

Then identify:

- The exact task.
- Files likely to change.
- Acceptance criteria.
- Any risk of scope expansion.

If the task is unclear, stop and update `AGENT_STATUS.md` with the blocker.

## Handoff requirements

Before stopping, update `AGENT_STATUS.md`.

The handoff must include:

- What changed.
- What did not change.
- Files changed.
- Checks run.
- Results of those checks.
- Known risks or blockers.
- Whether user approval is needed.
- Recommended next action.

## Approval brief requirements

If user approval is needed, do not ask a raw technical question.

Write a plain-English approval brief in `AGENT_STATUS.md` with:

- The decision being requested.
- The available options.
- Which option best matches `CURRENT_SLICE.md`.
- Which option risks scope drift.
- What could break if the wrong option is chosen.
- The recommended option.
- The exact next prompt or instruction to continue safely.

Then stop.

## Architecture-change rule

If a decision could change host roles, model routing, billing exposure, automation behavior, persistent state location, or security posture, stop.

Update `AGENT_STATUS.md` with:

- The proposed change.
- Why it came up.
- Why it may affect architecture.
- The safest conservative option.

Do not implement architecture changes without explicit user approval.

## Completion rule

A task is complete only when:

- The requested slice is done.
- `AGENT_STATUS.md` is updated.
- Relevant checks were run or explicitly marked unavailable.
- Git diff is ready for user review.
## Codex/OpenCode context contract

Before making changes, agents must read `CODEX_CONTEXT.md` in addition to this file.

Any change to plan, scope, architecture, acceptance criteria, risks, rollback path, current slice, or next action must be reflected in the relevant repo docs in the same diff.

If a change affects live services or production config, the agent must stop after proposing the exact command block and wait for operator approval.

