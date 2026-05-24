# Current Slice

## Active: Codex Aider vLLM architecture planning

## Goal

Document the current homelab development architecture direction away from
OpenCode as the primary coding-agent path and toward:

- Codex as the high-trust manual planner, sequencer, approval-brief author,
  reviewer, and risky live-service agent.
- Aider as the small bounded patch assistant only after local/free-model
  compatibility is proven.
- vLLM as the preferred model-serving direction to evaluate for
  coding/reasoning models on AMD and Strix.
- `model-dispatch` as the policy/routing layer that should not be replaced
  casually.
- Hermes as an observer, reviewer, recorder, and approved-skill-assisted
  preservation layer, not the primary coder and not an autonomous mutator.

This is a docs-only architecture planning slice.

## Files Expected to Change

- `CURRENT_SLICE.md`
- `inventory/codex-aider-vllm-architecture-plan.md`
- `PROJECT_PLAN.md`
- `ROADMAP.md`
- `WORKFLOW.md`
- `AGENT_STATUS.md`

`ROADMAP.md` and `WORKFLOW.md` should be updated only where needed to remove
contradictions with this active architecture direction.

## Acceptance Criteria

- `CURRENT_SLICE.md` identifies the active slice as
  `Codex Aider vLLM architecture planning`.
- `inventory/codex-aider-vllm-architecture-plan.md` exists.
- The architecture plan includes:
  - current operating decision
  - why OpenCode is no longer primary
  - Codex role
  - Aider role
  - vLLM role on AMD
  - vLLM role on Strix
  - `model-dispatch` role
  - Hermes role
  - Qwen thinking-on versus thinking-off treatment
  - Aider compatibility test approach
  - what not to change yet
  - next recommended slices
- The ideal architecture states:
  - Codex remains the high-trust manual planner/reviewer.
  - Aider becomes the small bounded patch tool after local/free-model
    compatibility is proven.
  - vLLM should be evaluated as the clean model-serving layer for Aider on AMD
    and Strix.
  - `model-dispatch` remains the policy/routing layer and should not be
    replaced casually.
  - Hermes observes, reviews, records, and uses approved skills for
    preservation checks, but does not become the coding agent.
- The plan includes this phased path:
  - Phase 1: document architecture.
  - Phase 2: inspect AMD and Strix vLLM readiness.
  - Phase 3: test vLLM endpoint with curl only.
  - Phase 4: test Aider against vLLM with a harmless one-file docs edit.
  - Phase 5: add a dedicated `model-dispatch` alias only after Aider/vLLM
    compatibility is proven.
  - Phase 6: return to Hermes and use the approved runtime preservation skill
    for a read-only preservation check.
- Prior Aider/OpenCode history remains preserved as history.
- Aider is not run.
- vLLM is not run.
- `model-dispatch` is not edited.
- No `/srv/model-dispatch` files are touched.
- No `/srv/projects/model-dispatch` files are touched.
- No `/srv/projects/hermes-homelab-runtime` files are touched.
- No services are restarted.
- No `sudo`, Docker, or systemd commands are run.
- No Open WebUI, OpenCode, Continue.dev, LiteLLM, dashboard, monitoring, or
  observability configuration is changed.
- No commit is made.
- `AGENT_STATUS.md` is updated with the handoff.
- The requested checks are run:
  - `git diff --check`
  - `git diff --stat`
  - `git status --short`

## Scope Expansion Risks

- Running Aider would turn this planning slice into a tool trial.
- Running vLLM would turn this planning slice into serving validation.
- Editing live `/srv/model-dispatch` or `/srv/projects/model-dispatch` would
  broaden the task into routing implementation.
- Editing `/srv/projects/hermes-homelab-runtime` would broaden the task into
  Hermes runtime implementation.
- Restarting services, using `sudo`, Docker, or systemd would broaden the task
  into operations.
- Changing Open WebUI, OpenCode, Continue.dev, LiteLLM, dashboards,
  monitoring, or observability would violate the docs-only boundary.
- Adding wrappers, daemons, hidden background jobs, automation, paid fallback,
  or approval behavior would violate standing constraints.
- Recommending paid frontier models for Aider, OpenCode, Cline, or other
  non-Codex agents would violate the current model-use constraint.

## Prior Slice History

### Previous Active Slice: Codex Aider vLLM Hermes strategy consolidation

Purpose:

Consolidate the development-agent and model-serving strategy around Codex for
planning/risk, Aider for bounded patches after compatibility is validated,
vLLM as the preferred serving candidate for AMD and Strix tests, and Hermes as
observer/reviewer/skill proposer only.

Definition of done from that slice:

- `CURRENT_SLICE.md` identified the active slice as
  `Codex Aider vLLM Hermes strategy consolidation`.
- `inventory/codex-aider-vllm-hermes-strategy.md` was created.
- The strategy document covered purpose, current state, development roles,
  target architecture, AMD and Strix vLLM roles, Aider compatibility path,
  Qwen mode decision tree, Hermes boundary, explicit non-goals, validation
  order, and stop conditions.
- `WORKFLOW.md` no longer implied OpenCode was the next primary agent.
- `ROADMAP.md` reflected the vLLM, Aider, and Hermes strategy.
- Prior Aider/OpenCode history remained preserved.
- Aider was not run.
- vLLM was not run.
- No `/srv/model-dispatch`, `/srv/projects/model-dispatch`, or
  `/srv/projects/hermes-homelab-runtime` files were touched.
- No services were restarted.
- No `sudo`, Docker, or systemd commands were run.
- No Open WebUI, OpenCode, Continue.dev, LiteLLM, dashboard, monitoring, or
  observability configuration was changed.
- No commit was made.

### Previous Active Slice: Aider compatibility read-only inspection

Purpose:

Inspect why Aider gets empty responses from local `model-dispatch` aliases by
comparing OpenAI-compatible response shapes from `model-dispatch` and the
direct AMD Qwen3 Coder endpoint.

Definition of done from that slice:

- `CURRENT_SLICE.md` identified the active slice as
  `Aider compatibility read-only inspection`.
- `inventory/aider-compatibility-inspection-2026-05-18.md` was created.
- The inspection document included purpose, endpoints, exact read-only manual
  commands, expected response fields, comparison criteria, and issue
  indicators for dispatcher, backend, and Aider configuration or edit-format
  causes.
- The manual commands did not run Aider.
- The manual commands did not edit services.
- No `/srv/model-dispatch` files were touched.
- No `/srv/projects/model-dispatch` files were touched.
- No services were restarted.
- No `sudo`, Docker, or systemd commands were run.
- No OpenCode, Continue.dev, Open WebUI, LiteLLM, dashboard, monitoring, or
  observability configuration was changed.
- No commit was made.

### Previous Active Slice: Aider compatibility planning

Purpose:

Plan how to diagnose why Aider gets empty responses from local
`model-dispatch` aliases without running more Aider trials.

Definition of done from that slice:

- `CURRENT_SLICE.md` identified the active slice as
  `Aider compatibility planning`.
- `inventory/aider-compatibility-plan.md` was created.
- The plan covered observed failures, hypotheses, what to inspect first, local
  `model-dispatch` compatibility checks, direct AMD endpoint compatibility
  checks, verified OpenRouter-free fallback test option, what not to do, and
  validation commands for a later slice.
- The plan preserved hypotheses around Aider response-format expectations,
  `model-dispatch` alias compatibility, generic aliases versus direct model
  IDs, and possible Aider metadata, edit-format, or provider configuration
  needs.
- Aider was not run.
- No `/srv/model-dispatch` files were touched.
- No `/srv/projects/model-dispatch` files were touched.
- No services were restarted.
- No Open WebUI, OpenCode, Continue.dev, LiteLLM, dashboard, monitoring, or
  observability configuration was changed.
- No commit was made.
