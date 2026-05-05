# Current Slice

## Slice 3: Strengthen `AGENTS.md` coder status and approval brief rules

Update `AGENTS.md` so any self-hosted coding agent working in this repo knows how to produce useful handoff/status briefs.

## Purpose

The agent should not leave the user with raw technical approval questions or unexplained changes. It should update `AGENT_STATUS.md` with a concise plain-English brief before handoff.

## Requirements

`AGENTS.md` should require the coding agent to:

- Work only on `CURRENT_SLICE.md`.
- Keep changes narrow and reviewable.
- Update `AGENT_STATUS.md` before handoff.
- Explain what changed.
- List files changed.
- List checks run.
- Identify risks or blockers.
- State whether approval is needed.
- If approval is needed, explain:
  - the decision being requested
  - the available options
  - which option best matches `CURRENT_SLICE.md`
  - the recommended next action
- Stop instead of improvising if the decision could broaden scope or change architecture.

## Constraints

- No automation.
- No daemon.
- No watcher.
- No MCP supervision.
- No model API calls.
- No Codex infrastructure.

## Acceptance Criteria

- `AGENTS.md` contains clear handoff and approval-brief rules.
- `AGENT_STATUS.md` is updated to show Slice 3 was completed or is ready for review.
- Changes are committed to Git.
