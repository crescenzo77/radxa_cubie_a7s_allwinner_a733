# Project Plan

Build a practical two-surface homelab workflow.

## Goal

Create a stable workflow where:

1. A web UI advisor/planner helps interpret state and generate next prompts.
2. OpenCode performs bounded coding work through a direct local-coder path.
3. A local `advisor-packet` script creates compact context packets.
4. Markdown files and Git provide durable project state.

## Non-goals

- No Codex automation.
- No paid API automation.
- No approval daemon.
- No hidden watcher agent.
- No autonomous supervision loop.
- No MCP failure-supervision system for this workflow.
- No Aider usage in the homelab steady-state workflow.
- No long-term LiteLLM dependency in the active OpenCode/OpenWebUI path.

## Completed stages

- Slice 1: Canonical homelab repo initialized on Strix.
- Slice 2: Initial `scripts/advisor-packet` created and committed.
- Slice 3: `AGENTS.md` strengthened with handoff and approval-brief rules.
- Slice 4: Two-surface loop tested on one documentation-only repo task.
- Slice 5: Aider evaluated and eliminated from the homelab workflow.
- Slice 6: Workflow docs recentered on OpenCode after Aider elimination.

## Current build stage

Slice 7: transition OpenCode and Open WebUI away from LiteLLM as the active routing layer.

## How to use this repo

Use this repo as the canonical source for homelab workflow state.

- `PROJECT_PLAN.md` stores the broad goal, completed stages, and current build stage.
- `CURRENT_SLICE.md` stores the active task and its acceptance criteria.
- `AGENT_STATUS.md` stores the current handoff/status summary.
- `DECISIONS.md` stores durable decisions and rationale.
- `AGENTS.md` stores rules for coding agents working in this repo.
- `scripts/advisor-packet` creates a compact advisor packet for the web UI.
