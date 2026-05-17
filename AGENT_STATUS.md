# Agent Status

## Current status

Documentation-only architecture transition slice has been started and is ready
for review. This status file has been repaired so prior useful history remains
available below the current handoff.

## Current task

Start a new active slice: "Architecture transition planning and model-dispatch
repo preparation."

## What changed

- `CURRENT_SLICE.md` now defines the active transition-planning slice, including
  scope, non-scope, validation steps, and definition of done.
- `DECISIONS.md` now records the 2026-05-17 decision to centralize model routing
  through `model-dispatch`, make Strix the canonical source/code-graph host, and
  make AMD a mode-switched GPU compute worker.
- `ROADMAP.md` now includes the ordered architecture transition plan from slice
  0 through slice 15.
- `HOMELAB_LAYOUT.md` now includes the target platform architecture and final
  desired host roles.
- `WORKFLOW.md` now includes the Codex-assisted deployment rule.
- `AGENT_STATUS.md` now preserves useful prior status history under
  `Archived Status History` instead of replacing it.

## What did not change

No live services, production configs, OpenCode config, MCP config, or
`model-dispatch` runtime files were changed.

No scripts, daemons, watchers, hidden automation, paid-provider fallback, model
API calls, or network calls were added.

## Files changed

- `CURRENT_SLICE.md`
- `DECISIONS.md`
- `ROADMAP.md`
- `HOMELAB_LAYOUT.md`
- `WORKFLOW.md`
- `AGENT_STATUS.md`

## Checks run

- Read required context docs:
  - `AGENTS.md`
  - `CODEX_CONTEXT.md`
  - `PROJECT_PLAN.md`
  - `CURRENT_SLICE.md`
  - `DECISIONS.md`
  - `AGENT_STATUS.md`
- Read related architecture/workflow docs:
  - `ROADMAP.md`
  - `HOMELAB_LAYOUT.md`
  - `WORKFLOW.md`
- Checked working tree before editing:
  - `git status --short`
- Ran requested post-edit checks:
  - `git diff --check`
  - `git diff --stat`
  - `git diff -- AGENT_STATUS.md | sed -n '1,260p'`

## Results of checks

- Required docs were present and readable.
- Pre-existing untracked `tools/` path was observed and left unchanged.
- `git diff --check` passed with no output.
- `git diff --stat` reported 6 files changed, 403 insertions, and 69
  deletions across the full uncommitted docs diff.
- `git diff -- AGENT_STATUS.md | sed -n '1,260p'` showed the current
  architecture transition handoff followed by restored archived history.
- `git status --short` shows only the requested markdown files modified plus the
  pre-existing untracked `tools/` path.

## Known risks or blockers

No known blocker for this documentation-only slice.

The next implementation slice should stay conservative: prepare
`model-dispatch` as a first-class repo boundary without changing the live
service until an operator-approved command block exists.

## User approval needed

No approval is needed for this docs-only update.

Approval will be needed before any live service change, OpenCode config change,
MCP enablement, repo migration, or `model-dispatch` deployment.

## Recommended next action

Review this diff, then start transition slice 0: baseline inventory and freeze
point. After slice 0 is complete, proceed to slice 1: `model-dispatch`
first-class repo preparation.

## Archived Status History

Older status entries remain below for continuity. They are not the active slice.

## Previous status — LLM runtime topology documentation

LLM runtime topology documentation update is complete and ready for review.

Previous task:
Edit `inventory/models/llm-runtime-topology.md` into a stable,
CodeGraphContext-friendly LLM model topology document.

What changed:
`inventory/models/llm-runtime-topology.md` now describes stable LLM topology
across:

- `strix`
- `thinkcentre`
- `AMD`

The document now includes:

- Purpose and scope.
- A clear statement that it is structural inventory, not runtime monitoring.
- Host sections for `strix`, `thinkcentre`, and `AMD`.
- Stable service/container names where known.
- Runtime/image families where known.
- Endpoint/port details where known.
- Role/purpose notes where known.
- Source/config path hints where known.
- A CGC exclusions section for logs, request logs, Docker stats, cache details,
  daily container churn, secrets, and unrelated containers.

What did not change:
No live services or live configs were changed.

No:

- Docker commands
- sudo commands
- network calls
- model API calls
- service restarts
- files outside this repo
- secrets, tokens, raw logs, request logs, daily activity logs, or cache details

Files changed:

- `inventory/models/llm-runtime-topology.md`
- `AGENT_STATUS.md`

Checks run:

- Read required context docs:
  - `AGENTS.md`
  - `CODEX_CONTEXT.md`
  - `PROJECT_PLAN.md`
  - `CURRENT_SLICE.md`
  - `DECISIONS.md`
  - `AGENT_STATUS.md`
- Read related routing/workflow docs because the task touches service topology:
  - `HOMELAB_LAYOUT.md`
  - `WORKFLOW.md`
  - `ROADMAP.md`
- Read the target file:
  - `inventory/models/llm-runtime-topology.md`
- Reviewed the edited target file with:
  - `sed -n '1,260p' inventory/models/llm-runtime-topology.md`
- Checked Git state with:
  - `git status --short`
- Attempted a tracked diff for the target file with:
  - `git diff -- inventory/models/llm-runtime-topology.md`

Results of checks:

- Required context files were present and readable.
- The target document is readable Markdown.
- The document separates stable topology from validation notes.
- The document explicitly says it is not runtime monitoring.
- The document excludes observer logs, request logs, Docker stats, cache
  directories, daily container churn, unrelated non-LLM containers, and secrets.
- `git status --short` showed `inventory/models/` as untracked, so the target
  file was not yet visible in normal tracked `git diff` output.

Known risks or blockers:

- No known technical blocker.
- Because `inventory/models/` was untracked, the user should review and add that
  path intentionally if this inventory document should become part of Git
  history.

User approval needed:
No approval was needed for the completed documentation-only edit.

Recommended next action:
Review `inventory/models/llm-runtime-topology.md`, then add and commit
`inventory/models/llm-runtime-topology.md` and `AGENT_STATUS.md` if the topology
wording matches the intended stable inventory.

## 2026-05-15 — Strix Halo vLLM Ubuntu Docker PR

Created upstream PR for the Ubuntu 26.04 Docker Engine adaptation of
`kyuz0/amd-strix-halo-vllm-toolboxes`.

PR:

- https://github.com/kyuz0/amd-strix-halo-vllm-toolboxes/pull/54

Validated before PR:

- Docker-only Ubuntu path.
- No Podman, Distrobox, Toolbx, Ubuntu toolbox, or LXC.
- ROCm/PyTorch/vLLM smoke test on Strix Halo.
- Conservative Qwen/Qwen2.5-7B-Instruct API validation.
- Hugging Face auth through `hf auth login`.
- Conservative google/gemma-4-26B-A4B-it API validation.
- Memory exposure notes with 48 GiB clean allocation while other model-serving
  containers were stopped.

## 2026-05-15 — Strix qwen3.6 visible-output fix

Restored Strix llama.cpp mode as the default after vLLM benchmarking.

Runtime state:
- `qwen3-6` runs on port 8081.
- `qwen3-coder` runs on port 8082.
- vLLM on port 8010 is stopped/manual testbed mode.

Fix:
- Recreated `qwen3-6` with llama-server `--reasoning off`.
- This fixed the issue where Qwen3.6 returned output only in
  `message.reasoning_content` while `message.content` was empty.

Validation:
- `/health` on 8081 returned OK.
- `/v1/models` on 8081 listed `Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf`.
- `/v1/chat/completions` on 8081 returned visible content:
  `strix reasoning endpoint restored`.

Operational note:
- Keep `--reasoning off` for the normal visible-output Strix reasoning endpoint.
- vLLM remains validated as an optional Docker testbed, but current Strix
  default should remain llama.cpp Vulkan.
