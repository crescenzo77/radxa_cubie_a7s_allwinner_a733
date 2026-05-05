# Current Slice

## Slice 6: Recenter workflow on OpenCode through LiteLLM

Recenter the homelab two-surface workflow around OpenCode as the coding agent.

## Purpose

Aider was evaluated and eliminated from the homelab workflow after it failed a simple bounded documentation task in an unacceptable way.

The two-surface workflow remains valid, but the coder surface should now be OpenCode through Homelab LiteLLM.

## Requirements

Update the homelab docs so they clearly state:

- OpenCode through LiteLLM is the preferred coding agent path.
- Aider was evaluated and eliminated from the homelab workflow.
- Aider should not be used as default or fallback for this workflow.
- `advisor-packet` remains the bridge between coder state and the web UI advisor.
- The user remains the final approver.
- No autonomous supervisor, daemon, watcher, MCP failure-supervision, or paid API automation should be added.

## Constraints

- Documentation only.
- No scripts.
- No service changes.
- No model routing changes.
- No uninstall yet.
- No new tools.

## Acceptance Criteria

- `PROJECT_PLAN.md` says the current stage is recentering on OpenCode.
- `WORKFLOW.md` no longer presents Aider as a candidate path.
- `ROADMAP.md` reflects that Aider was eliminated and OpenCode is the path forward.
- `AGENT_STATUS.md` is updated with a concise handoff.
- Changes are committed to Git.
