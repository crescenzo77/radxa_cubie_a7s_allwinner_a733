# Current Slice

## Active: model-dispatch alias registry cleanup planning

## Goal

Plan and document stable `model-dispatch` model aliases before changing
OpenCode or Continue.dev.

This slice is planning only. It must not change live routing behavior.

## Scope

Create a registry cleanup plan that documents:

- Current exposed model IDs.
- Proposed stable aliases.
- Compatibility aliases to preserve.
- Role aliases for advisor, reasoning, coding, small, review, and long-code.
- What must not change yet.
- Validation required before any alias deployment.
- Rollback expectations.

## Files Expected to Change

- `CURRENT_SLICE.md`
- `inventory/model-dispatch-alias-registry-plan.md`
- `AGENT_STATUS.md`

## Acceptance Criteria

- `CURRENT_SLICE.md` identifies the active slice as
  `model-dispatch alias registry cleanup planning`.
- `inventory/model-dispatch-alias-registry-plan.md` exists and covers the
  required alias planning sections.
- The plan preserves current behavior and explicitly says no live
  `model-dispatch` config changes happen in this slice.
- OpenCode direct AMD routing remains unchanged.
- Continue.dev's current documented route remains unchanged.
- `/srv/model-dispatch` is not edited.
- No services are restarted.
- No dashboards, monitoring, or observability are deployed.
- `AGENT_STATUS.md` is updated with the handoff.
- The requested checks are run:
  - `git diff --check`
  - `git diff --stat`
  - `git status --short`

## Scope Expansion Risks

- Deploying aliases during this slice would change model routing and is out of
  scope.
- Editing OpenCode or Continue.dev would bundle client migration with registry
  planning and is out of scope.
- Removing existing model IDs too early could break Open WebUI or future
  rollback paths.
- Adding dashboards, monitoring, observability, automation, paid fallback, or
  hidden supervision would violate the standing constraints.

## Prior Slice History

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
