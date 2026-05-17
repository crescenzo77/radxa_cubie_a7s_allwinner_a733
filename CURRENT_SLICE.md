# Current Slice

## Active: model-dispatch deployment planning only

## Purpose

Write the deployment, rollback, and validation plan for eventually deploying
the Strix `model-dispatch` source repo to the live ThinkCentre
`/srv/model-dispatch` service path.

This slice is planning only. No deployment happens in this slice.

## Current Known State

- Homelab latest pushed commit:
  `b7bd223 document model-dispatch mirror state`.
- `model-dispatch` source repo: `strix:/srv/projects/model-dispatch`.
- `model-dispatch` ThinkCentre mirror:
  `thinkcentre:/srv/git/model-dispatch.git`.
- `model-dispatch` latest mirrored commit:
  `7cbb1d9 document thinkcentre mirror creation`.
- `model-dispatch` remains review-only.
- Live service path remains `thinkcentre:/srv/model-dispatch`.
- No deployment has occurred.
- Dashboards, monitoring, and observability deployment remain deferred.

## Scope

- Update this active slice description.
- Create `inventory/model-dispatch-deployment-plan-2026-05-17.md`.
- Document deployment purpose, current source/mirror/live state, exact
  non-goals, pre-deployment validation, eligible and excluded files, backup
  plan, proposed deployment commands, rollback commands, post-deployment
  validation commands, Open WebUI validation, OpenRouter-free fail-closed
  validation, known risks, and approval requirements.
- Mark all future command blocks clearly as `NOT RUN`.
- Update `AGENT_STATUS.md` with the handoff.

## Non-Scope

- Do not deploy.
- Do not edit `/srv/model-dispatch`.
- Do not copy files to `/srv/model-dispatch`.
- Do not run `rsync`, `scp`, `cp`, `mv`, or `rm` against
  `/srv/model-dispatch`.
- Do not restart or reload `model-dispatch.service`.
- Do not run `sudo`.
- Do not run Docker or systemd commands.
- Do not change Open WebUI, OpenCode, LiteLLM, MCP, reverse proxy, dashboard,
  monitoring, or observability configuration.
- Do not touch `tools/`.
- Do not commit.
- Do not make network calls or model API calls as part of this planning slice.

## Validation Steps

- Read the required homelab control docs:
  - `CURRENT_SLICE.md`
  - `ROADMAP.md`
  - `HOMELAB_LAYOUT.md`
  - `WORKFLOW.md`
  - `DECISIONS.md`
  - `ROUTING_INVENTORY.md`
  - `inventory/model-dispatch-first-class-repo-plan.md`
  - `inventory/model-dispatch-live-inventory-2026-05-17.md`
  - `AGENT_STATUS.md`
- Read the allowed `model-dispatch` source repo docs:
  - `README.md`
  - `SERVICE.md`
  - `DEPLOYMENT.md`
  - `ROUTING.md`
  - `DECISIONS.md`
  - `TESTING.md`
  - `AGENT_STATUS.md`
- Run `git diff --check`.
- Run `git diff --stat`.
- Run `git status --short`.

## Definition of Done

- `CURRENT_SLICE.md` identifies the active slice as
  `model-dispatch deployment planning only`.
- `inventory/model-dispatch-deployment-plan-2026-05-17.md` exists and covers
  the required deployment, rollback, validation, and approval plan.
- The deployment plan explicitly says:
  - no deployment happens in this slice
  - live `/srv/model-dispatch` remains untouched
  - `model-dispatch.service` remains untouched
  - dashboards, monitoring, and observability remain deferred
- `AGENT_STATUS.md` describes what changed, what did not change, checks run,
  risks, and next recommended action.
- No live services, configs, OpenCode settings, Open WebUI settings, LiteLLM
  settings, MCP settings, Docker state, systemd state, reverse proxy settings,
  dashboard, monitoring, observability, source mirror, live runtime files,
  `tools/` files, or commits were changed.
