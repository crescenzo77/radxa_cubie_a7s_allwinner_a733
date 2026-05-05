# Project Plan

Build a practical two-surface homelab workflow.

## Goal

Create a stable workflow where:

1. A web UI advisor/planner helps interpret state and generate next prompts.
2. A self-hosted coding agent performs bounded work on the project host.
3. A local `advisor-packet` script creates compact context packets.
4. Markdown files and Git provide durable project state.

## Non-goals

- No Codex automation.
- No paid API automation.
- No approval daemon.
- No hidden watcher agent.
- No autonomous supervision loop.
- No MCP failure-supervision system for this workflow.

## Completed stages

- Slice 1: Canonical homelab repo initialized on Strix.
- Slice 2: Initial `scripts/advisor-packet` created and committed.

## Current build stage

Slice 4: test the full two-surface loop on one small documentation task.

## How to use this repo

Use this repo as the canonical source for homelab workflow state.

- `PROJECT_PLAN.md` stores the broad goal, completed stages, and current build stage.
- `CURRENT_SLICE.md` stores the active task and its acceptance criteria.
- `AGENT_STATUS.md` stores the current handoff/status summary.
- `DECISIONS.md` stores durable decisions and rationale.
- `AGENTS.md` stores rules for coding agents working in this repo.
- `scripts/advisor-packet` creates a compact advisor packet for the web UI.
