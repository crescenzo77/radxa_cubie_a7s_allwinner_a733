# Current Slice

## Active: additive model-dispatch alias deployment planning

## Goal

Plan an additive `model-dispatch` alias deployment from the reviewed source
repo without changing live routing yet.

This slice is planning only. It must not edit live `/srv/model-dispatch`,
restart services, deploy aliases, or change Open WebUI, OpenCode, or
Continue.dev configuration.

## Scope

Create an additive alias deployment plan that documents:

- Current aliases and model IDs to preserve.
- New aliases to add.
- Proposed Open WebUI display names.
- Exact future `config.json` changes.
- Files eligible for deployment.
- Backup path.
- Validation commands.
- Rollback plan.
- Non-goals.

## Files Expected to Change

- `CURRENT_SLICE.md`
- `inventory/model-dispatch-additive-alias-deployment-plan.md`
- `AGENT_STATUS.md`

## Acceptance Criteria

- `CURRENT_SLICE.md` identifies the active slice as
  `additive model-dispatch alias deployment planning`.
- `inventory/model-dispatch-additive-alias-deployment-plan.md` exists and
  covers the required deployment planning sections.
- The first alias deployment is planned as additive only.
- Existing IDs remain available.
- Open WebUI display names are descriptive enough to infer model family,
  parameter size, quantization, context window, and host or role where known.
- Exact future `config.json` model and route additions are documented.
- Files eligible for deployment are documented.
- The backup path is documented as
  `/srv/model-dispatch/backups/<timestamp>/`.
- Validation commands and rollback steps are documented as future
  operator-approved commands, not run in this slice.
- OpenCode direct AMD routing remains unchanged.
- Continue.dev's current documented route remains unchanged.
- Open WebUI live config remains unchanged.
- `/srv/model-dispatch` is not edited.
- `/srv/projects/model-dispatch` may be inspected only; it is not edited.
- No services are restarted.
- No Docker, systemd, sudo, deployment, or live endpoint-changing command is
  run.
- No dashboards, monitoring, or observability are deployed.
- No commit is made.
- `AGENT_STATUS.md` is updated with the handoff.
- The requested checks are run:
  - `git diff --check`
  - `git diff --stat`
  - `git status --short`

## Scope Expansion Risks

- Deploying aliases during this slice would change model routing and is out of
  scope.
- Editing OpenCode, Continue.dev, or Open WebUI would bundle client migration
  with alias deployment planning and is out of scope.
- Removing existing model IDs during the first alias deployment could break
  Open WebUI selections or rollback paths.
- Treating `free-cloud` as an automatic fallback could introduce cloud routing
  behavior that is not part of this slice.
- Adding dashboards, monitoring, observability, automation, paid fallback, or
  hidden supervision would violate the standing constraints.

## Prior Slice History

### Previous Active Slice: model-dispatch alias registry cleanup planning

Purpose:

Plan and document stable `model-dispatch` model aliases before changing
OpenCode or Continue.dev.

This slice was planning only. No live routing behavior changed in that slice.

Definition of done from that slice:

- `CURRENT_SLICE.md` identified the active slice as
  `model-dispatch alias registry cleanup planning`.
- `inventory/model-dispatch-alias-registry-plan.md` existed and covered the
  required alias planning sections.
- The plan preserved current behavior and explicitly said no live
  `model-dispatch` config changes happened in that slice.
- OpenCode direct AMD routing remained unchanged.
- Continue.dev's current documented route remained unchanged.
- `/srv/model-dispatch` was not edited.
- No services were restarted.
- No dashboards, monitoring, or observability were deployed.
- `AGENT_STATUS.md` was updated with the handoff.
- Requested checks were run:
  - `git diff --check`
  - `git diff --stat`
  - `git status --short`

### Previous Active Slice: model-dispatch deployment planning only

Purpose:

Write the deployment, rollback, and validation plan for eventually deploying
the Strix `model-dispatch` source repo to the live ThinkCentre
`/srv/model-dispatch` service path.

This slice was planning only. No deployment happened in that slice.

Definition of done from that slice:

- `CURRENT_SLICE.md` identified the active slice as
  `model-dispatch deployment planning only`.
- `inventory/model-dispatch-deployment-plan-2026-05-17.md` covered the
  required deployment, rollback, validation, and approval plan.
- The deployment plan explicitly said:
  - no deployment happens in this slice
  - live `/srv/model-dispatch` remains untouched
  - `model-dispatch.service` remains untouched
  - dashboards, monitoring, and observability remain deferred
- `AGENT_STATUS.md` described what changed, what did not change, checks run,
  risks, and next recommended action.
- No live services, configs, OpenCode settings, Open WebUI settings, LiteLLM
  settings, MCP settings, Docker state, systemd state, reverse proxy settings,
  dashboard, monitoring, observability, source mirror, live runtime files,
  `tools/` files, or commits were changed.
