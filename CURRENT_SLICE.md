# Current Slice

## Active: AMD temporary vLLM runtime test planning

## Goal

Plan the first temporary AMD vLLM runtime test without starting vLLM, stopping
existing containers, changing model routing, changing Open WebUI, or running
Aider.

This is a docs-only planning slice. It must turn the completed AMD Phase 1
live-state recheck and AMD Phase 2 local image/runtime inspection into a
reviewable future runtime-test plan.

## Files Expected To Change

- `CURRENT_SLICE.md`
- `PROJECT_PLAN.md`
- `AGENT_STATUS.md`
- `inventory/amd-temporary-vllm-runtime-test-plan.md`

`ROADMAP.md` should be updated only if this slice exposes a roadmap
contradiction or missing planning boundary.

## Acceptance Criteria

- `CURRENT_SLICE.md` identifies the active slice as
  `AMD temporary vLLM runtime test planning`.
- `inventory/amd-temporary-vllm-runtime-test-plan.md` exists.
- The plan includes:
  - purpose
  - current proven facts
  - why the test must be temporary
  - exact candidate image
  - exact candidate model
  - model format concern
  - whether the existing GGUF model is suitable or likely unsuitable for vLLM
  - candidate port selection
  - resource and VRAM issue
  - decision point for stopping `qwen3-coder-30b`
  - proposed future Docker run shape, clearly marked not to run yet
  - curl-only validation checks
  - stop/rollback command
  - what not to change
  - go/no-go criteria before runtime execution
- The plan includes this warning:
  - Do not stop `qwen3-coder-30b` until the model candidate and vLLM model
    format are proven.
  - If no HF/safetensors model is present locally, stop and plan model
    acquisition separately instead of trying to force vLLM to serve GGUF.
- Prior history remains preserved.
- vLLM is not started.
- `qwen3-coder-30b` is not stopped or restarted.
- `gemma4-7900xt` is not stopped or restarted.
- Aider is not run.
- `model-dispatch` is not edited.
- `/srv/model-dispatch` is not touched.
- No Open WebUI, OpenCode, Continue.dev, LiteLLM, dashboard, monitoring, or
  observability configuration is changed.
- No `sudo`, Docker write commands, or systemd write commands are run.
- No commit is made.
- `AGENT_STATUS.md` is updated with the handoff.
- The requested checks are run:
  - `git diff --check`
  - `git diff --stat`
  - `git status --short`

## Proven Facts To Preserve

- Latest homelab commit before this slice:
  `fc15397 document amd vllm phase 2 image inspection`.
- AMD Phase 1 live-state recheck is documented.
- AMD Phase 2 local vLLM image/runtime inspection is documented.
- Local image exists on AMD: `vllm/vllm-openai:latest`.
- Image has:
  - `python3`
  - Python `3.12.13`
  - torch `2.10.0+cu129`
  - CUDA `12.9`
  - vLLM `0.19.0`
- Image can see RTX 3090 with `--gpus all`.
- Existing containers remained healthy after dry checks:
  - `qwen3-coder-30b` on `8083`
  - `gemma4-7900xt` on `8084`
- RTX 3090 VRAM is mostly occupied by `qwen3-coder-30b`.
- vLLM has not been started.
- `qwen3-coder-30b` has not been stopped.
- `model-dispatch` and Open WebUI remain unchanged.

## Scope Expansion Risks

- Starting vLLM would turn this planning slice into live runtime execution.
- Stopping or restarting `qwen3-coder-30b` or `gemma4-7900xt` would affect
  healthy AMD serving.
- Pulling or downloading a model would turn this into model acquisition.
- Forcing the existing GGUF llama.cpp artifact into vLLM would create a
  confused validation target and risk wasting the RTX 3090 stop window.
- Running Aider would turn this into an agent compatibility trial.
- Editing `model-dispatch` or `/srv/model-dispatch` would broaden this into
  routing implementation.
- Changing Open WebUI, OpenCode, Continue.dev, LiteLLM, dashboards,
  monitoring, or observability would violate the docs-only boundary.
- Running `sudo`, Docker write commands, or systemd write commands would
  broaden this into operations.

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
