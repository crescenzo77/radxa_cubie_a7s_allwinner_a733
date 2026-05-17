# Current Slice

## Active: model-dispatch first-class repo preparation

## Purpose

Prepare the documentation, repo layout plan, validation plan, and operator
approval brief for making `model-dispatch` a first-class source-controlled repo.

This slice does not change the live `model-dispatch` service.

## Scope

- Document the current known live `model-dispatch` state from existing docs.
- Define the target source repo and tier-1 mirror locations.
- Propose a future repo layout and file inventory.
- Record exact non-goals, risks, rollback thinking, and validation needed before
  touching the live service.
- Draft an operator approval brief template.
- Include future command blocks only as proposals clearly marked `NOT RUN`.
- Leave a clear handoff in `AGENT_STATUS.md`.

## Non-Scope

- Do not run `sudo`.
- Do not restart services.
- Do not edit files outside this repo.
- Do not touch `tools/`.
- Do not create `strix:/srv/projects/model-dispatch` yet.
- Do not create `/srv/projects/model-dispatch` yet.
- Do not copy `/srv/model-dispatch` yet.
- Do not change `model-dispatch` runtime files.
- Do not change Open WebUI, OpenCode, LiteLLM, Docker, systemd, reverse proxy,
  SearXNG, monitoring, backup, or MCP settings.
- Do not add scripts.
- Do not commit.

## Validation Steps

- Read the required control docs:
  - `CURRENT_SLICE.md`
  - `ROADMAP.md`
  - `HOMELAB_LAYOUT.md`
  - `WORKFLOW.md`
  - `DECISIONS.md`
  - `ROUTING_INVENTORY.md`
  - `inventory/baseline-2026-05-17.md`
  - `AGENT_STATUS.md`
- Confirm the Slice 1 plan is documentation-only.
- Run `git diff --check`.
- Run `git diff --stat`.
- Run `git status --short`.

## Definition of Done

- `CURRENT_SLICE.md` identifies Slice 1 as the active slice.
- `inventory/model-dispatch-first-class-repo-plan.md` records the preparation
  plan and approval brief template.
- `AGENT_STATUS.md` describes what changed, what did not change, checks run,
  risks, and next recommended action.
- No live services, configs, OpenCode settings, `model-dispatch` runtime files,
  MCP settings, Docker state, systemd state, repo locations, scripts, or
  `tools/` files were changed.
