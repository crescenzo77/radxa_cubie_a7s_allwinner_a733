# Current Slice

## Active: Architecture transition planning and model-dispatch repo preparation

## Purpose

Start a reversible, documentation-first architecture transition toward:

- ThinkCentre as the control plane.
- Strix as the canonical source, development, code-graph, and reasoning host.
- AMD as a mode-switched GPU compute worker.
- `model-dispatch` as the single model-facing API registry for Open WebUI, OpenCode, Continue.dev, and scripts.

This slice prepares the planning and repo boundaries for the transition. It does
not change live services.

## Scope

- Document the target platform architecture and migration sequence.
- Record the routing/source/compute role decision in `DECISIONS.md`.
- Define the next transition roadmap slices.
- Prepare for making `model-dispatch` a first-class, reviewable repository.
- Preserve current rollback paths while documenting the intended end state.
- Keep the migration sliced, reversible, and validated at each step.

## Non-Scope

- Do not edit live service files outside this repo.
- Do not change OpenCode config.
- Do not change the live `model-dispatch` service.
- Do not enable MCP.
- Do not move canonical repos yet.
- Do not change reverse proxy, Open WebUI, SearXNG, monitoring, or backup config.
- Do not add scripts unless explicitly required by a later slice.
- Do not create hidden automation, daemons, watchers, approval systems, or Codex infrastructure.
- Do not add paid-provider fallback or broad autonomous orchestration.

## Validation Steps

For this documentation-only slice:

- Read the required control docs before editing.
- Confirm edits are limited to repo documentation.
- Run `git diff --check`.
- Run `git diff --stat`.
- Leave `AGENT_STATUS.md` with the handoff, checks, risks, and next recommended slice.

Later implementation slices must add their own concrete validation before any
live service changes are made.

## Definition of Done

- `CURRENT_SLICE.md` defines this active transition-planning slice.
- `DECISIONS.md` records the 2026-05-17 architecture transition decision.
- `ROADMAP.md` includes the ordered full transition plan.
- `HOMELAB_LAYOUT.md` describes the target platform host roles.
- `WORKFLOW.md` documents the Codex-assisted deployment rule.
- `AGENT_STATUS.md` is updated for handoff.
- No live services, production configs, OpenCode config, MCP config, or
  `model-dispatch` runtime files were changed.
- `git diff --check` and `git diff --stat` were run.
