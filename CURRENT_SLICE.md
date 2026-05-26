# Current Slice

## Active: AMD vLLM model-dispatch alias planning

## Goal

Plan whether and how to add a dedicated `model-dispatch` alias for the proven
temporary AMD vLLM endpoint, without implementing the alias, changing live
routing, changing Open WebUI, starting vLLM, stopping services, or running
Aider.

This is a docs-only planning slice. It must preserve the direct AMD vLLM and
Aider trial history while deciding the conservative next routing posture.

## Files Expected To Change

- `CURRENT_SLICE.md`
- `PROJECT_PLAN.md`
- `AGENT_STATUS.md`
- `ROADMAP.md`, only if needed to correct current workflow facts
- `inventory/amd-vllm-model-dispatch-alias-plan.md`

Do not edit `/srv/model-dispatch` or `/srv/projects/model-dispatch`.

## Acceptance Criteria

- `CURRENT_SLICE.md` identifies the active slice as
  `AMD vLLM model-dispatch alias planning`.
- `inventory/amd-vllm-model-dispatch-alias-plan.md` exists.
- The plan includes:
  - purpose
  - current proven facts
  - why no live alias should be added yet
  - temporary/manual-only alias recommendation
  - alias naming options
  - whether Aider should stay direct-to-vLLM for now
  - how to handle RTX 3090 ownership conflict
  - why `qwen3-coder-30b` and vLLM should not both be assumed available
  - `model-dispatch` risks
  - Open WebUI risks
  - Aider risks
  - exact go/no-go criteria before implementation
  - future implementation phases
  - rollback expectations
- The recommended direction is:
  - Do not add a `model-dispatch` alias yet.
  - Keep Aider direct-to-vLLM for one more practical one-file patch or until
    vLLM runtime mode is made repeatable.
  - If an alias is later added, make it explicit/manual-only, not auto-routed.
  - Do not route Open WebUI `auto-local` or `auto-coding-local` to this vLLM
    endpoint yet.
  - Do not expose it as always available unless a persistent vLLM runtime
    exists.
  - Treat AMD RTX 3090 as mode-switched: either `qwen3-coder-30b` llama.cpp on
    `8083` or vLLM on `18000`, not both.
- Future phases are documented:
  - Phase 1: document alias plan.
  - Phase 2: create repeatable temporary vLLM start/stop procedure.
  - Phase 3: run one more direct Aider trial with a practical single-file patch,
    if needed.
  - Phase 4: inspect `model-dispatch` source and config read-only.
  - Phase 5: propose explicit manual alias only.
  - Phase 6: implement alias only after approval.
  - Phase 7: curl-test alias through `model-dispatch`.
  - Phase 8: optionally test Aider through `model-dispatch` alias.
- Prior history remains preserved.
- `/srv/model-dispatch` is not edited or touched.
- `/srv/projects/model-dispatch` is not edited or touched.
- `model-dispatch` live config and service are not changed.
- Open WebUI is not changed.
- vLLM is not started.
- `qwen3-coder-30b` is not stopped or restarted.
- `gemma4-7900xt` is not stopped or restarted.
- Aider is not run.
- No `sudo`, Docker write commands, or systemd write commands are run.
- No commit is made.
- `AGENT_STATUS.md` is updated with the handoff.
- The requested checks are run:
  - `git diff --check`
  - `git diff --stat`
  - `git status --short`

## Proven Facts To Preserve

- Latest homelab commit before this slice:
  `8d79196 document second direct aider vllm trial`.
- AMD vLLM with `Qwen2.5-Coder-7B-Instruct` works directly on port `18000`.
- Direct endpoint used:
  `http://192.168.50.252:18000/v1`
- Served model:
  `amd-vllm-temp-qwen2.5-coder-7b`
- Aider succeeded twice against the direct vLLM endpoint.
- Both Aider trials were bounded one-file docs edits.
- Aider still asks to add context/control files, but respects declined
  additions.
- `qwen3-coder-30b` was restored healthy on `8083` after each test.
- `gemma4-7900xt` stayed healthy on `8084`.
- `model-dispatch` and Open WebUI were not changed.
- vLLM is not currently persistent.
- vLLM owns the RTX 3090 while running.
- `qwen3-coder-30b` must be stopped while vLLM owns the RTX 3090.

## Scope Expansion Risks

- Adding a live alias would turn this planning slice into routing
  implementation.
- Editing `/srv/model-dispatch` or `/srv/projects/model-dispatch` would violate
  the requested boundary.
- Routing Open WebUI auto aliases to vLLM would imply the endpoint is generally
  available, which is false while vLLM is temporary and RTX 3090 mode-switched.
- Starting vLLM would turn this into runtime execution.
- Stopping or restarting `qwen3-coder-30b` or `gemma4-7900xt` would affect
  healthy AMD serving.
- Running Aider would turn this into another agent trial.
- Adding daemons, wrappers, restart policies, Compose files, systemd units, or
  automation would broaden the slice beyond planning.
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
