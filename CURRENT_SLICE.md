# Current Slice

## Active: AMD vLLM validation planning

## Goal

Plan the first AMD-first vLLM validation slice without running vLLM, installing
vLLM, stopping existing containers, changing model routing, or changing Open
WebUI.

This is a docs-only planning slice. It should preserve the committed
architecture direction:

- Codex is primary for planning, sequencing, approval briefs, and risky
  live-service work.
- Aider is the bounded patch assistant only after compatibility is proven.
- vLLM is the preferred model-serving direction to evaluate on AMD and Strix.
- `model-dispatch` remains the policy/routing layer.
- Hermes remains observer/reviewer/recorder/preservation-check layer.
- OpenCode is no longer primary.

## Files Expected to Change

- `CURRENT_SLICE.md`
- `PROJECT_PLAN.md`
- `AGENT_STATUS.md`
- `inventory/amd-vllm-validation-plan.md`

`ROADMAP.md` should be updated only if this slice exposes a roadmap
contradiction or missing planning boundary.

## Acceptance Criteria

- `CURRENT_SLICE.md` identifies the active slice as
  `AMD vLLM validation planning`.
- `inventory/amd-vllm-validation-plan.md` exists.
- The plan includes:
  - purpose
  - current AMD facts
  - why AMD goes first
  - what must be inspected before any vLLM run
  - VRAM issue from `qwen3-coder-30b` occupying RTX 3090
  - candidate validation options
  - port choice constraints
  - model choice constraints
  - Qwen thinking-off baseline for Aider-oriented patch output
  - rollback/stop conditions
  - what not to change yet
  - exact future validation phases
- Future validation phases are:
  - Phase 1: read-only AMD live-state recheck
  - Phase 2: identify candidate vLLM install/runtime method
  - Phase 3: identify candidate model and model format
  - Phase 4: choose temporary port and resource plan
  - Phase 5: stop or free RTX 3090 only after explicit approval
  - Phase 6: start vLLM only after explicit approval
  - Phase 7: curl-only OpenAI-compatible checks
  - Phase 8: Aider one-file docs trial only after curl checks pass
  - Phase 9: model-dispatch alias only after Aider/vLLM proof
- Prior history remains preserved.
- vLLM is not run.
- vLLM is not installed.
- `qwen3-coder-30b` and `gemma4-7900xt` containers are not stopped or
  restarted.
- Aider is not run.
- `model-dispatch` is not edited.
- No `/srv/model-dispatch` files are touched.
- No Open WebUI, OpenCode, Continue.dev, LiteLLM, dashboard, monitoring, or
  observability configuration is changed.
- No `sudo`, Docker write commands, or systemd write commands are run.
- No commit is made.
- `AGENT_STATUS.md` is updated with the handoff.
- The requested checks are run:
  - `git diff --check`
  - `git diff --stat`
  - `git status --short`

## Readiness Findings To Preserve

- AMD is the better first vLLM candidate.
- AMD has RTX 3090 visible through `nvidia-smi`.
- NVIDIA driver reports CUDA 13.2 support.
- RTX 3090 VRAM is mostly occupied by the current `qwen3-coder-30b`
  llama.cpp container.
- AMD currently has healthy containers:
  - `qwen3-coder-30b` on 8083
  - `gemma4-7900xt` on 8084
- AMD current endpoints return OpenAI-compatible `/v1/models`.
- `vllm` was not found in the current user path.
- Python is 3.14.4.
- Strix is later because ROCm tools are absent and port 8000 is occupied.
- ThinkCentre `model-dispatch` and Open WebUI routing are healthy and
  unchanged.

## Scope Expansion Risks

- Running vLLM would turn this planning slice into live serving validation.
- Installing vLLM would turn this planning slice into runtime preparation.
- Stopping or restarting `qwen3-coder-30b` or `gemma4-7900xt` would affect
  healthy AMD serving.
- Running Aider would turn this slice into a compatibility trial.
- Editing `model-dispatch` or `/srv/model-dispatch` would broaden this into
  routing implementation.
- Changing Open WebUI, OpenCode, Continue.dev, LiteLLM, dashboards,
  monitoring, or observability would violate the docs-only boundary.
- Running `sudo`, Docker write commands, or systemd write commands would
  broaden this into operations.
- Adding wrappers, daemons, hidden background jobs, automation, paid fallback,
  or approval behavior would violate standing constraints.

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
