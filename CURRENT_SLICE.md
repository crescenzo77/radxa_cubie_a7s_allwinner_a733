# Current Slice

## Active: next-slice choice pending

## Completed Slice: model-dispatch first-class repo transition

The `model-dispatch` transition slice is complete.

This slice moved `model-dispatch` from incidental live-service files toward a
first-class reviewed repo, mirror, and deployment workflow, then validated the
live service without adding dashboard, monitoring, or observability deployment.

## Completion Summary

- Source repo created:
  `strix:/srv/projects/model-dispatch`.
- ThinkCentre mirror created:
  `thinkcentre:/srv/git/model-dispatch.git`.
- Live deployment completed to:
  `thinkcentre:/srv/model-dispatch`.
- Rollback backup location:
  `/srv/model-dispatch/backups/<timestamp>`.
- Service validation completed:
  `model-dispatch.service` is healthy after deployment.
- Systemd restart policy fixed:
  `Restart=unless-stopped` was replaced with `Restart=on-failure`.
- Benchmark tool committed:
  `tools/bench/openai_endpoint_bench.py`.
- Homelab latest commit:
  `b0f5356 add OpenAI endpoint benchmark tool`.
- Homelab pushed to:
  `thinkcentre/main`.

## Explicit Non-Changes

- No dashboard deployment occurred.
- No monitoring deployment occurred.
- No observability deployment occurred.
- No new implementation is active until the next slice is chosen.

## Recommended Next Slice Choices

### Option 1: OpenCode Through model-dispatch

Move OpenCode from direct AMD endpoint definitions toward stable
`model-dispatch` aliases.

Why this fits:
- It advances the central routing decision.
- It reduces duplicated model endpoint configuration.
- It directly affects the main coding surface.

Risks:
- OpenCode is the active coding tool, so config mistakes could interrupt the
  normal coder workflow.
- Direct AMD routing must remain documented as rollback until validated.

### Option 2: Strix Dual-Coder Layout

Document and validate Strix as a source/development/code-graph/reasoning host
with a clear dual-coder layout.

Why this fits:
- It supports the target host-role split.
- It keeps AMD available for mode-switched GPU workloads.

Risks:
- This can drift into architecture changes if it starts moving live services or
  enabling new background tooling.

### Option 3: Continue.dev Through model-dispatch

Move Continue.dev away from LiteLLM-routed model IDs and toward stable
`model-dispatch` aliases.

Why this fits:
- It reduces LiteLLM dependency in another client.
- It aligns editor-side review with the central routing layer.

Risks:
- Continue.dev is optional but user-facing; config changes should be reversible.
- Existing LiteLLM-routed IDs should remain rollback until validation.

### Option 4: model-dispatch Alias Registry Cleanup

Clean up and document the stable alias registry before moving more clients.

Why this fits:
- It improves the foundation before touching OpenCode or Continue.dev.
- It can define advisor, coding, reasoning, small, training, and creative
  aliases clearly.

Risks:
- Alias changes can break clients if existing names are removed too early.
- This should stay registry-focused and avoid live deployment unless separately
  approved.

### Option 5: Pause and Observe Current Deployment

Make no further routing or client changes yet. Observe the current
`model-dispatch` deployment and only document findings.

Why this fits:
- It is the most conservative next slice.
- It gives the live deployment time to prove stable.

Risks:
- It delays reducing duplicated client routing.
- It may leave OpenCode and Continue.dev on older paths longer than necessary.

## Recommended Next Action

Choose the next slice before implementation. The conservative recommendation is
Option 5, `pause and observe current deployment`, if live stability is the top
priority. If continuing the routing migration is preferred, choose Option 4,
`model-dispatch alias registry cleanup`, before changing OpenCode or
Continue.dev clients.

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
