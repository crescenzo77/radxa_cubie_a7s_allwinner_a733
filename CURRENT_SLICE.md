# Current Slice

## Active: Align agent context with archive-first plan structure

## Current State

`CODEX_CONTEXT.md` is being aligned with the new plan-file structure:

- top-level `PROJECT_PLAN.md`, `WORKFLOW.md`, `ROADMAP.md`, and
  `HOMELAB_LAYOUT.md` are current entrypoints
- old versions live in `docs/archive/`
- agents must archive or quarantine old plans before creating replacements
- Aider is the preferred bounded patch executor for planned strict slices

This is a docs-only slice.

Do not:

- delete workflow, plan, history, or draft files
- change services, Docker, systemd, model-dispatch, Open WebUI, routing, or
  deployment state
- stage or commit without user approval

Checks to preserve before commit:

- `git status --short`
- `git diff --check`
- verify `CODEX_CONTEXT.md` no longer describes current entrypoints as
  historical workflow/roadmap references

## Prior Current State

## Active: Archive superseded top-level plan files

## Current State

The workflow procedure has been corrected:

- Do not edit old plan files in place to make them current.
- Archive or quarantine old plan files first.
- Create fresh current files at stable entrypoint paths.
- Keep `PLAN_INDEX.md` as the registry of current state records and archived
  history.

This slice archived old versions of:

- `PROJECT_PLAN.md`
- `WORKFLOW.md`
- `ROADMAP.md`
- `HOMELAB_LAYOUT.md`

Fresh current entrypoints now exist at those same top-level paths.

This is a docs-only slice.

Do not:

- delete workflow, plan, history, or draft files
- change services, Docker, systemd, model-dispatch, Open WebUI, routing, or
  deployment state
- stage or commit without user approval

Checks to preserve before commit:

- `git status --short`
- `git diff --check`
- verify archived files exist under `docs/archive/`
- verify current entrypoint files are short and point to `PLAN_INDEX.md`

## Prior Current State

## Active: Clarify Aider preferred patch executor posture

## Current State

The workflow docs are being corrected to reflect the user's clarified tool
choice:

- Aider is the preferred bounded patch executor for planned strict slices.
- Aider performs the coding/editing action after the planner defines the slice.
- Aider must not become the planner, broaden scope, auto-commit, deploy, change
  services, or become autonomous.
- OpenCode remains blocked for local model patching and is not the preferred
  next patch tool.
- The active workflow now includes a `Start Here` order that begins with
  `PLAN_INDEX.md`.

This is a docs-only clarification slice.

Do not:

- change services, Docker, systemd, model-dispatch, Open WebUI, routing, or
  deployment state
- delete workflow, plan, history, or draft files
- stage or commit without user approval

Checks to preserve before commit:

- `git status --short`
- `git diff --check`
- verify no docs still say OpenCode is the preferred next local-model coding
  agent candidate
- verify the active workflow points readers to `PLAN_INDEX.md` first

## Prior Current State

## Active: Provider-neutral workflow plan tracking checkpoint

## Current State

The provider-neutral workflow and no-delete plan tracking slice is in progress.

Current docs state:

- `PLAN_INDEX.md` was added as the canonical registry for current, superseded,
  archived, and quarantined plans.
- `docs/provider-neutral-adhd-workflow.md` is the current active operating plan.
- `docs/provider-neutral-adhd-workflow-evolution-2026-05-29.md` is the protected
  long-context master history/evolution file. Do not delete it.
- `docs/archive/local-agent-workflow-runbook-draft-2026-05-29.md` preserves the
  first draft instead of deleting it.
- `WORKFLOW.md`, `ROADMAP.md`, and `PROJECT_PLAN.md` are marked as superseded or
  historical references through `PLAN_INDEX.md`.
- `CODEX_CONTEXT.md` now requires future agents to read `PLAN_INDEX.md` before
  selecting a workflow plan.

This is a docs-only slice.

Do not:

- delete workflow, plan, history, or draft files
- delete the long-context master history/evolution file
- stage or commit without user approval
- change services, Docker, systemd, model-dispatch, Open WebUI, routing, or
  deployment state

Checks to preserve before commit:

- `git status --short`
- `git diff --check`
- trailing whitespace check for new untracked docs
- verify `PLAN_INDEX.md` has exactly one `Current` plan

## Prior Current State

The AMD `local/amd-coder` Aider code-patch validation is complete enough to
preserve.

Validated and pushed:

- Aider `0.86.2` edited one code file in `/srv/projects/cubie-camera-node`.
- The edit used model-dispatch endpoint `http://192.168.50.225:4010/v1`.
- Aider model argument: `openai/local/amd-coder`.
- Aider created only `scripts/cubie-node-summary`.
- Aider history files were written outside the repo.
- The helper passed `bash -n`.
- Running the helper printed the expected three status lines.
- `git diff --check` passed.
- `cubie-camera-node` commit:
  `d6246ef add Cubie node summary helper`
- The commit was pushed to `thinkcentre:/srv/git/cubie-camera-node.git`.

AMD Aider code validation note:

- `inventory/aider-amd-coder-code-validation-2026-05-28.md`

## Prior Current State

The OpenCode local-model follow-up is complete enough to preserve as a blocker.

Validated:

- The throwaway repo remained isolated at `/tmp/opencode-local-trial`.
- Adding `limit.context: 32768` and `limit.output: 4096` to the AMD OpenCode
  model config removed the earlier model-dispatch context rejection.
- AMD `local/amd-coder` still produced no OpenCode edit and no visible
  OpenCode model output.
- Strix `local/strix-coder` also produced no visible OpenCode model output.
- `opencode run --format json` for a plain "Reply exactly ok" prompt emitted
  only `step_start` and `step_finish` events with zero recorded tokens for both
  AMD and Strix.
- Direct model-dispatch tool-loop smoke passed for both:
  - `scripts/model-tool-loop-smoke --model local/amd-coder`
  - `scripts/model-tool-loop-smoke --model local/strix-coder`

Conclusion:

- model-dispatch and the llama.cpp coder backends can do OpenAI-style tool
  calls directly.
- The current blocker is specific to OpenCode's local provider/run path.
- OpenCode remains installed but not validated as a patch tool.
- Aider remains the validated bounded patch-tool path.

OpenCode follow-up note:

- `inventory/opencode-local-model-followup-2026-05-28.md`

## Prior Current State

The first OpenCode local-model preflight is complete enough to preserve as a
partial/negative checkpoint.

Validated:

- OpenCode was not initially present on Strix or the Mac mini.
- Official installer access via `https://opencode.ai/install` failed from
  Strix because `opencode.ai:443` was unreachable.
- Strix had general internet access and `npm`.
- OpenCode was installed on Strix with `npm install -g opencode-ai`.
- Installed OpenCode version: `1.15.12`.
- Binary path: `/home/enzo/.local/npm-global/bin/opencode`.
- A throwaway repo was created at `/tmp/opencode-local-trial`.
- Project-local `opencode.json` configured model-dispatch through
  `@ai-sdk/openai-compatible`.
- OpenCode listed:
  - `homelab/amd-coder-qwen3-coder-30b-32k`
  - `homelab/strix-coder-qwen3-coder-next-65k`

Trial results:

- AMD `local/amd-coder` did not run the OpenCode build agent because
  model-dispatch rejected the request as context-too-small:
  estimated total `34682` tokens against `32768` context.
- Strix `local/strix-coder` accepted the larger-context request, but OpenCode
  exited without editing, with zero recorded model tokens and no tool calls.
- No real project repo was edited by OpenCode.
- No model-dispatch, Open WebUI, Docker, systemd, or routing config changed.

OpenCode preflight note:

- `inventory/opencode-local-model-preflight-2026-05-28.md`

## Prior Current State

The AMD `local/amd-coder` bounded patch-tool validation is complete enough to
preserve.

Validated and pushed:

- AMD `qwen3-coder-30b` was live and healthy on port `8083`.
- model-dispatch `local/amd-coder` returned a clean `ok`.
- Aider `0.86.2` edited one file in `/srv/projects/cubie-camera-node`.
- The edit used model-dispatch endpoint `http://192.168.50.225:4010/v1`.
- Aider edited only `README.md`.
- Aider history files were written outside the repo.
- `git diff --check` passed.
- `cubie-camera-node` commit:
  `cd4b5a1 validate AMD coder bounded patch`
- The commit was pushed to `thinkcentre:/srv/git/cubie-camera-node.git`.

AMD Aider validation note:

- `inventory/aider-amd-coder-validation-2026-05-28.md`

## Prior Current State

The provider-neutral patch-review workflow checkpoint is complete enough to
preserve.

Validated and pushed:

- Added `docs/patch-review-workflow.md`.
- Updated `WORKFLOW.md` so coding-agent trials follow:
  planner/advisor -> patch tool -> reviewer -> user decision.
- Updated `docs/aider-workflow.md` to make the reviewer role provider-neutral.
- Updated `DECISIONS.md` with the provider-neutral patch-review decision.
- Clarified that local models can review diffs through Open WebUI without a
  coding agent.
- Clarified that local models need a coding harness only when expected to edit
  files.
- Documented OpenCode as the preferred next local-model coding-agent candidate
  to evaluate.
- Documented Codex-on-Strix-with-local-model as unproven and a separate
  investigation.

## Prior Current State

The first bounded Aider edit through the restored Strix llama.cpp/GGUF
Coder-Next endpoint is complete enough to preserve.

Validated and pushed:

- Strix `qwen3-coder` on `8082` was live and serving
  `Qwen3-Coder-Next-UD-Q4_K_XL.gguf`.
- Aider `0.86.2` edited one file in `/srv/projects/cubie-camera-node`.
- The edit used direct endpoint `http://127.0.0.1:8082/v1`.
- Aider edited only `README.md`.
- Generated Aider history files were removed before commit.
- `git diff --check` passed.
- `cubie-camera-node` commit:
  `8de720a clarify next hardware checklist step`
- The commit was pushed to `thinkcentre:/srv/git/cubie-camera-node.git`.
- Added repeatable helper:
  `scripts/aider-strix-coder-llamacpp`

Aider llama.cpp validation note:

- `inventory/aider-strix-llamacpp-validation-2026-05-28.md`

## Earlier Current State

The local model role reset is complete enough to preserve.

Validated and pushed:

- Strix vLLM Qwen3.6 AWQ was stopped.
- Strix llama.cpp/GGUF `qwen3-6` was started on `8081`.
- Strix llama.cpp/GGUF `qwen3-coder` was started on `8082`.
- AMD RTX 3090 `qwen3-coder-30b` was started on `8083`.
- AMD RX 7900 XT `gemma4-7900xt` was started on `8084`.
- model-dispatch already had the required aliases and routes.
- `local/strix-reasoning`, `local/strix-coder`, and `local/amd-coder`
  returned clean `ok` responses.
- `local/amd-small` responded, but emitted reasoning text instead of clean
  content for a tiny prompt.
- Qwen 3.7 was checked as a future experiment topic; no local open-weight
  target is available yet.

Role reset note:

- `inventory/local-model-role-reset-2026-05-28.md`

## Earlier Current State

The Strix concurrent model variant comparison is complete enough to preserve.

Validated and pushed:

- Strix was recovered after the second direct-only concurrent vLLM attempt.
- Temporary Coder-Next direct-test container and `/tmp` Compose files were
  removed.
- `scripts/strix-vllm-mode tool` proved the Qwen3.6 baseline again.
- The old concurrently runnable containers were inspected.
- The old pair was confirmed to be llama.cpp/Vulkan/GGUF:
  `Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf` and
  `Qwen3-Coder-Next-UD-Q4_K_XL.gguf`.
- The current failing pair was confirmed to be vLLM/AWQ Hugging Face packages:
  `cyankiwi/Qwen3.6-35B-A3B-AWQ-4bit` and
  `cyankiwi/Qwen3-Coder-Next-AWQ-4bit`.
- Recommendation: do not keep retrying concurrent vLLM AWQ numeric tweaks.

Comparison note:

- `inventory/strix-concurrent-model-variant-comparison-2026-05-28.md`

## Earlier Current State

The first attempt to run both Strix vLLM models live at the same time failed
and was recovered to the known-good single-model baseline.

Validated and pushed:

- The failed two-model attempt was documented.
- Temporary uncommitted Strix runtime/helper edits were restored from `HEAD`.
- Temporary uncommitted ThinkCentre model-dispatch config edit was restored
  from `HEAD`.
- Generated Python cache was removed.
- `scripts/strix-vllm-mode tool` removed the failed Coder-Next container and
  proved `local/tool-test`.
- Final Strix mode: `tool`
- Final served model: `qwen36-awq-agent-test`
- Final model-dispatch service state: active

Recovery note:

- `inventory/strix-two-model-feasibility-attempt-2026-05-28.md`

## Earlier Current State

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

## Earlier Current State

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

1. Stop here and treat the patch-review workflow as preserved.
2. Validate AMD `local/amd-coder` as the RTX 3090 agentic workhorse.
3. Evaluate OpenCode as a local-model coding-agent candidate under the same
   patch-review workflow.
4. Pick a concrete open-weight 7900 XT experiment model when one is available.

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
