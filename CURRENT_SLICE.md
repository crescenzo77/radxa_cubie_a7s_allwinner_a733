# Current Slice

## Active: Strix vLLM runtime mode strategy checkpoint complete

## Current State

The Strix vLLM runtime mode strategy checkpoint is complete enough to
preserve.

Validated and pushed:

- Live Strix and ThinkCentre state were checked before writing the strategy.
- Strix remained in `tool` mode with `qwen36-awq-agent-test` active.
- ThinkCentre `model-dispatch.service` remained active with
  `Restart=on-failure`.
- The current one-port mode design was documented.
- Future options were compared without implementing any of them.
- Recommendation: keep manual one-port switching for now.
- No services, ports, Compose files, model-dispatch config, Open WebUI defaults,
  Docker runtime state, or systemd units were changed.

Strategy file:

- `inventory/strix-vllm-runtime-mode-strategy-2026-05-28.md`

## Prior Current State

The first real bounded Aider trial in a non-critical repo is complete enough to
preserve.

Validated and pushed:

- `cubie-camera-node` was selected as a clean, non-critical repo.
- Strix switched to `code` mode and `local/code-test` passed the smoke test.
- `scripts/aider-code-test` edited `README.md` only.
- The generated Aider history files were removed before commit.
- The committed diff was one file and four inserted lines.
- `cubie-camera-node` commit:
  `3af1c05 document next hardware readiness step`
- The commit was pushed to `thinkcentre:/srv/git/cubie-camera-node.git`.
- Strix was restored to `tool` mode and `local/tool-test` passed the smoke
  test.
- Aider remains evaluation-only and is not promoted to the core workflow.

## Earlier Current State

The repo and mirror inventory checkpoint is complete enough to preserve.

Validated and pushed:

- Live Strix and ThinkCentre state matched the Strix local-agent checkpoint.
- Strix remained in `tool` mode with `qwen36-awq-agent-test` active.
- ThinkCentre `model-dispatch.service` was active and still used
  `Restart=on-failure`.
- Current Strix working repositories were inventoried.
- Current ThinkCentre working repositories were inventoried.
- Current ThinkCentre bare mirrors were inventoried.
- Dirty working trees were recorded without modification.
- No services, routes, Docker runtimes, systemd units, Open WebUI defaults, or
  model-dispatch config were changed.

Inventory file:

- `inventory/repo-and-mirror-inventory-2026-05-28.md`

## Earlier Current State

The current Strix vLLM local-agent validation checkpoint is complete enough to
stop this pass.

Validated and pushed:

- Strix Qwen3.6 AWQ vLLM runtime is managed by Docker Compose and restored as
  the current stable baseline.
- `local/tool-test` passes the model-dispatch OpenAI-style tool loop while
  Qwen3.6 is active.
- Strix Qwen3-Coder-Next AWQ has a preserved manual test runtime.
- `local/code-test` passes the model-dispatch OpenAI-style tool loop while
  Coder-Next is active.
- `scripts/strix-vllm-mode` switches the one-port Strix runtime between
  `tool` and `code`, waits for readiness, and runs the matching smoke test.
- Aider `0.86.2` passed a bounded one-file throwaway edit through
  `local/code-test` and model-dispatch.
- Aider `0.86.2` passed one real bounded non-critical repo edit in
  `cubie-camera-node`.
- `scripts/aider-code-test` preserves the validated Aider command shape and
  refuses to run unless the Coder-Next served model is active.
- Latest pushed checkpoint at the time of this slice update:
  `6ee8fc0 add local code-test aider helper`.

## Active Posture

No active implementation slice.

Do not promote Aider, add auto routes, make Coder-Next persistent, add hidden
automation, change Open WebUI defaults, or redesign model routing until an
explicit slice selects that work.

## Current Walking Skeleton

- Framework is the user seat.
- Strix is the normal project home for new non-GPU projects.
- ThinkCentre is the services/control-plane host and Git mirror.
- AMD is the GPU-heavy project host and model host.
- Planner asks for targeted evidence instead of guessing.
- Planner gives exact commands or controlled manual edit steps.
- User runs the commands.
- Review Coach reviews diffs in layman's terms.
- User commits and pushes to ThinkCentre.

## Evaluation-Only / Deferred

- Aider remains evaluation-only, but one bounded local `local/code-test` edit is
  now proven.
- OpenCode is not the default or primary coder, and nothing should depend on it.
- OpenHuman is abandoned for the current phase because it creates signup/service
  pressure.
- CodeGraphContext write workflows are evaluation-only.
- Hermes remains observer/reviewer/reporting only.
- Autonomous reviewer/oracle loops are out of scope.

## Recommended Next Choices

1. Stop here and treat the Strix runtime mode strategy as preserved.
2. Write a separate approval brief for a future two-port Strix concurrency
   feasibility test.
3. Plan a second bounded Aider trial only if a specific low-risk target is
   selected.
4. Plan a separate repo/mirror cleanup slice using the inventory.

## Constraints

- Do not use Aider on `DECISIONS.md`, `WORKFLOW.md`, `CURRENT_SLICE.md`,
  `AGENT_STATUS.md`, or `PROJECT_PLAN.md`.
- Do not use Aider in the homelab repo as a normal workflow yet.
- Do not make service, Docker, systemd, routing, storage, or model-runtime
  changes without fresh live-state validation.
- Do not trust project docs as current truth without checking live state.
- Keep old decisions as history; newer decisions define current policy.

## Prior Slice History

### Previous Active Slice: AMD vLLM manual mode-switch runbook

### Goal

Create a reviewed manual runbook for temporarily switching AMD RTX 3090 from
`qwen3-coder-30b` llama.cpp on port `8083` to vLLM on port `18000`, then
restoring `qwen3-coder-30b`.

This is a docs-only slice. Do not execute the procedure.

### Files Expected To Change

- `CURRENT_SLICE.md`
- `PROJECT_PLAN.md`
- `AGENT_STATUS.md`
- `runbooks/amd-vllm-manual-mode-switch.md`
- `ROADMAP.md`, only if needed to correct current workflow facts

Do not edit `/srv/model-dispatch` or `/srv/projects/model-dispatch`.

### Acceptance Criteria

- `CURRENT_SLICE.md` identifies the active slice as
  `AMD vLLM manual mode-switch runbook`.
- `runbooks/amd-vllm-manual-mode-switch.md` exists.
- The runbook includes:
  - purpose
  - when to use it
  - when not to use it
  - prerequisites
  - exact paths
  - exact model
  - exact temporary vLLM container name
  - exact temporary port
  - preflight checks
  - stop `qwen3-coder-30b` step
  - start temporary vLLM step
  - wait-for-vLLM checks
  - `curl /v1/models` check
  - `curl /v1/chat/completions` check
  - optional Aider direct endpoint command shape
  - rollback steps
  - wait-for-`qwen3-coder-30b` health checks
  - `8083` and `8084` validation checks
  - GPU validation checks
  - failure handling
  - what not to change
- The runbook preserves these runtime facts:
  - Normal RTX 3090 mode:
    - container: `qwen3-coder-30b`
    - port: `8083`
    - model: `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
  - Gemma backup:
    - container: `gemma4-7900xt`
    - port: `8084`
    - model: `google_gemma-4-26B-A4B-it-Q4_K_M.gguf`
  - Temporary vLLM mode:
    - container: `amd-vllm-temp-test`
    - port: `18000` mapped to container `8000`
    - model path: `/srv/llm/hf/Qwen2.5-Coder-7B-Instruct`
    - served model: `amd-vllm-temp-qwen2.5-coder-7b`
    - image: `vllm/vllm-openai:latest`
    - dtype: `float16`
    - max model length: `16384`
    - GPU memory utilization: `0.90`
    - generation config: `vllm`
- The runbook clearly warns:
  - This procedure intentionally takes `amd:8083` offline while vLLM owns RTX
    3090.
  - Do not run this during work that depends on `qwen3-coder-30b`.
  - Do not add restart policies, Compose files, systemd units, wrappers, or
    automation.
  - Do not edit `model-dispatch` or Open WebUI as part of the mode switch.
- Prior history remains preserved.
- `PROJECT_PLAN.md` is updated if needed.
- `ROADMAP.md` is updated only if needed.
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

### Runtime Facts To Preserve

- Latest homelab commit before this slice:
  `689e6e7 plan amd vllm model dispatch alias`.
- AMD direct vLLM with `Qwen2.5-Coder-7B-Instruct` is proven on port `18000`.
- Direct Aider-to-vLLM is proven twice for bounded one-file docs edits.
- `qwen3-coder-30b` on `8083` and temporary vLLM on `18000` are mutually
  exclusive RTX 3090 modes.
- `gemma4-7900xt` on `8084` should remain running.
- `model-dispatch` alias is planned but not implemented.
- Recommendation remains: do not add a `model-dispatch` alias yet.

### Scope Expansion Risks

- Executing the mode switch would turn this from a runbook slice into live
  operations.
- Starting vLLM would take RTX 3090 ownership and require stopping
  `qwen3-coder-30b`.
- Stopping or restarting `qwen3-coder-30b` would affect normal AMD serving.
- Stopping or restarting `gemma4-7900xt` would affect the backup AMD model.
- Adding daemons, wrappers, restart policies, Compose files, systemd units, or
  automation would broaden the slice beyond a manual runbook.
- Editing `model-dispatch` or Open WebUI would turn this into routing/client
  implementation.
- Running Aider would turn this into another agent trial.
- Running `sudo`, Docker write commands, or systemd write commands would
  broaden this into operations.

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
