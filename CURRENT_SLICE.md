# Current Slice

## Active: next-slice choice pending

## Goal

Choose the next bounded slice after completing the additive
`model-dispatch` alias deployment.

The additive aliases are already deployed live. This state is selection only:
do not edit live `/srv/model-dispatch`, restart services, edit the
`model-dispatch` source repo, or change Open WebUI, OpenCode, Continue.dev,
dashboard, monitoring, or observability configuration.

## Next Slice Options

- OpenCode through `model-dispatch`.
- Continue.dev through `model-dispatch`.
- Observe current deployment.

## Files Expected to Change

- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`

## Acceptance Criteria

- `CURRENT_SLICE.md` identifies the active state as
  `next-slice choice pending`.
- The completed additive model-dispatch alias deployment is recorded in prior
  slice history.
- The completed validation and backup path are listed.
- Next slice options are listed:
  - OpenCode through `model-dispatch`
  - Continue.dev through `model-dispatch`
  - observe current deployment
- No `/srv/model-dispatch` files are touched.
- No `/srv/projects/model-dispatch` files are touched.
- No services are restarted.
- No Open WebUI config is changed.
- No OpenCode config is changed.
- No Continue.dev config is changed.
- No dashboard, monitoring, or observability deployment is started.
- No commit is made.
- `AGENT_STATUS.md` is updated with the handoff.
- The requested checks are run:
  - `git diff --check`
  - `git diff --stat`
  - `git status --short`

## Scope Expansion Risks

- Starting OpenCode or Continue.dev migration now would bundle next-slice
  implementation into this status update.
- Editing live `/srv/model-dispatch` or restarting services would turn a
  documentation update into an operational change.
- Adding dashboards, monitoring, observability, automation, paid fallback, or
  hidden supervision would violate the standing constraints.

## Prior Slice History

### Completed Slice: additive model-dispatch alias deployment

Purpose:

Deploy additive `model-dispatch` aliases live after the deployment plan and
approval checkpoint.

Completed facts:

- Homelab latest commit before this status update:
  `5ce3374 document additive alias deployment checkpoint`.
- Additive aliases were deployed live.
- Deployment record exists:
  `inventory/model-dispatch-additive-alias-deployment-approval-brief-2026-05-18.md`.
- Backup path:
  `/srv/model-dispatch/backups/20260518-093534`.
- No Open WebUI config change.
- No OpenCode config change.
- No Continue.dev config change.
- No dashboard, monitoring, or observability deployment.

Validation completed:

- `/health` returned OK.
- `/v1/models` listed:
  - `advisor`
  - `reasoning`
  - `coding`
  - `small`
  - `review`
  - `long-code`
  - `local/strix-reasoning`
  - `local/strix-coder`
  - `local/amd-coder`
  - `local/amd-small`
  - `free-cloud`
- `advisor` worked through `/v1/chat/completions`.
- `local/amd-coder` worked through `/v1/chat/completions`.

Definition of done from that slice:

- Additive aliases were deployed live.
- Existing client configuration was left unchanged.
- Backup path was recorded as
  `/srv/model-dispatch/backups/20260518-093534`.
- Validation confirmed health, model listing, and chat completions for
  `advisor` and `local/amd-coder`.
- No Open WebUI, OpenCode, Continue.dev, dashboard, monitoring, or
  observability configuration was changed.

### Previous Active Slice: additive model-dispatch alias deployment planning

Purpose:

Plan an additive `model-dispatch` alias deployment from the reviewed source
repo without changing live routing yet.

This slice was planning only. It did not edit live `/srv/model-dispatch`,
restart services, deploy aliases, or change Open WebUI, OpenCode, or
Continue.dev configuration.

Definition of done from that slice:

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
