# Agent Status

## Current status

Slice 6 documentation recentering is complete. The workflow docs now center on OpenCode through Homelab LiteLLM.

## Current slice

Slice 6: recenter workflow on OpenCode through LiteLLM.

## Completed work

- `WORKFLOW.md` no longer presents Aider as an active candidate or fallback.
- `ROADMAP.md` records that Aider was evaluated and eliminated.
- OpenCode through LiteLLM is now the active coder path.
- The two-surface workflow remains: web UI advisor, OpenCode coder, `advisor-packet`, markdown state files, and Git review.

## Files changed

- `WORKFLOW.md`
- `ROADMAP.md`
- `AGENT_STATUS.md`

## Checks run

- `grep -n "Aider\|aider" WORKFLOW.md ROADMAP.md`
- `git diff --stat`
- `git diff`
- `git status`

## Risks or blockers

OpenCode still needs to be tested directly against the two-surface workflow after the Aider elimination.

## Recommended next action

Commit this status update, then set the next slice to test OpenCode with one small documentation-only task.
