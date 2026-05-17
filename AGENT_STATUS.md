# Agent Status

## Current status

Slice 1 read-only live inventory of `thinkcentre:/srv/model-dispatch` is
complete and ready for review.

## Current task

Document the live `model-dispatch` file shape for include/exclude planning
without creating repos, copying files, restarting services, editing live config,
or reading secret contents.

## What changed

- `inventory/model-dispatch-live-inventory-2026-05-17.md` was added with:
  - purpose
  - boundaries
  - commands run
  - directory/file inventory summary
  - candidate source files to include later
  - candidate docs/config/tests to include later
  - candidate excludes
  - unknowns requiring user review
  - recommended include/exclude policy
  - next operator approval brief
- `AGENT_STATUS.md` was updated with this handoff while preserving older history
  below.

Live inventory highlights:

- `/srv/model-dispatch` already contains a `.git/` directory.
- Branch reported by read-only Git metadata: `main`.
- Recent commit reported: `ef65a5c initialize model dispatch service repo`.
- No Git remote was printed by `git remote -v`.
- Non-`.git` top-level files observed by name/metadata:
  - `.cgcignore`
  - `.gitignore`
  - `app.py`
  - `config.json`
  - timestamped `app.py.*.bak` files
  - timestamped `config.json.*.bak` files
  - `dispatch.log`

## What did not change

No live services, production configs, OpenCode config, MCP config, or
`model-dispatch` runtime files were changed.

No Docker state, systemd state, repo locations, scripts, daemons, watchers,
hidden automation, paid-provider fallback, model API calls, network calls, or
`tools/` files were changed.

No `/srv/projects/model-dispatch` repo was created. No
`thinkcentre:/srv/git/model-dispatch.git` mirror was created. No
`/srv/model-dispatch` files were copied. No file contents were printed.

## Files changed

- `inventory/model-dispatch-live-inventory-2026-05-17.md`
- `AGENT_STATUS.md`

## Checks run

- Read required context docs:
  - `CURRENT_SLICE.md`
  - `inventory/model-dispatch-first-class-repo-plan.md`
  - `inventory/baseline-2026-05-17.md`
  - `ROUTING_INVENTORY.md`
  - `AGENT_STATUS.md`
- Ran read-only remote inventory commands:
  - `ssh thinkcentre 'find /srv/model-dispatch -maxdepth 4 -printf "%y %s %TY-%Tm-%Td %TH:%TM %p\n" | sort'`
  - `ssh -F /dev/null thinkcentre 'find /srv/model-dispatch -maxdepth 4 -printf "%y %s %TY-%Tm-%Td %TH:%TM %p\n" | sort'`
  - `ssh -F /dev/null 192.168.50.225 'find /srv/model-dispatch -maxdepth 4 -printf "%y %s %TY-%Tm-%Td %TH:%TM %p\n" | sort'`
  - `ssh -F /dev/null 192.168.50.225 'find /srv/model-dispatch -maxdepth 4 \( ... likely secret/log/cache name patterns ... \) -printf "%y %s %TY-%Tm-%Td %TH:%TM %p\n" | sort'`
  - `ssh -F /dev/null 192.168.50.225 'find /srv/model-dispatch -path /srv/model-dispatch/.git -prune -o -maxdepth 2 -printf "%y %s %TY-%Tm-%Td %TH:%TM %p\n" | sort'`
  - `ssh -F /dev/null 192.168.50.225 'git -C /srv/model-dispatch status --short && git -C /srv/model-dispatch branch --show-current && git -C /srv/model-dispatch log --oneline -5'`
  - `ssh -F /dev/null 192.168.50.225 'git -C /srv/model-dispatch remote -v'`
  - `ssh -F /dev/null 192.168.50.225 'find /srv/model-dispatch -path /srv/model-dispatch/.git -prune -o -type f -printf "%f\n" | awk ... | sort | uniq -c'`
- Ran requested post-edit checks:
  - `git diff --check`
  - `git diff --stat`
  - `git status --short`

## Results of checks

- Required docs were present and readable.
- Initial hostname SSH failed due local SSH config permissions, then DNS lookup
  with `-F /dev/null` failed for hostname `thinkcentre`.
- Read-only SSH using `192.168.50.225` succeeded.
- The likely secret/log/cache name scan reported `dispatch.log` only.
- No `.env`, obvious secret, token, key, database, sqlite, cache, virtualenv, or
  `__pycache__` path was reported by name in the max-depth-4 scan.
- `git -C /srv/model-dispatch status --short` printed no changes.
- `git -C /srv/model-dispatch branch --show-current` printed `main`.
- `git -C /srv/model-dispatch log --oneline -5` printed
  `ef65a5c initialize model dispatch service repo`.
- `git -C /srv/model-dispatch remote -v` printed no remotes.
- `git diff --check` passed with no output.
- `git diff --stat` reported tracked changes in `AGENT_STATUS.md`. The new
  untracked live inventory file is visible in `git status --short` but not
  included in tracked `git diff --stat` output until staged.
- `git status --short` shows:
  - `M AGENT_STATUS.md`
  - `?? inventory/model-dispatch-live-inventory-2026-05-17.md`
  - `?? tools/`

## Known risks or blockers

- `config.json` was identified by name only and still needs user review for
  secrets before any copy.
- `app.py` was identified by name only and may contain embedded operational
  details that need review before source promotion.
- The live `.git/` directory should not be copied into the Strix source repo
  candidate by default.
- `dispatch.log` and timestamped `.bak` files should be excluded by default.
- Open WebUI currently depends on `model-dispatch`; this inventory does not
  permit deployment changes.
- Direct AMD routing and LiteLLM rollback must remain available until later
  validated replacement slices.
- No known blocker for this documentation-only slice.

## User approval needed

No approval is needed for this docs-only update.

Approval will be needed before any live service change, OpenCode config change,
MCP enablement, repo migration, Docker/systemd change, or `model-dispatch`
deployment.

## Recommended next action

Review `inventory/model-dispatch-live-inventory-2026-05-17.md`, then decide
whether to approve the next narrow step: creating a Strix source repo candidate
from the reviewed include list only. If `config.json` has not been manually
reviewed safe, review it before copying it.

## Archived Status History

Older status entries remain below for continuity. They are not the active slice.

## Previous status — Slice 1 repo preparation plan

Slice 1 `model-dispatch` first-class repo preparation was completed and made
ready for review.

Previous task:
Prepare the plan and operator approval brief for making `model-dispatch` a
first-class source-controlled repo without changing the live service.

What changed:

- `CURRENT_SLICE.md` defined the active slice as
  "model-dispatch first-class repo preparation."
- `inventory/model-dispatch-first-class-repo-plan.md` was added with purpose,
  current documented live state, target repo layout, proposed future repo
  contents, exact non-goals, risks, rollback thinking, validation needed before
  touching the live service, operator approval brief template, and proposed
  future command blocks clearly marked `NOT RUN`.
- `AGENT_STATUS.md` was updated with that handoff while preserving older history
  below.

What did not change:
No live services, production configs, OpenCode config, MCP config, or
`model-dispatch` runtime files were changed.

No Docker state, systemd state, repo locations, scripts, daemons, watchers,
hidden automation, paid-provider fallback, model API calls, network calls, or
`tools/` files were changed.

No `/srv/projects/model-dispatch` repo was created. No `/srv/model-dispatch`
files were copied or inspected directly.

Files changed:

- `CURRENT_SLICE.md`
- `inventory/model-dispatch-first-class-repo-plan.md`
- `AGENT_STATUS.md`

Checks run:

- `git diff --check`
- `git diff --stat`
- `git status --short`

Results:

- `git diff --check` passed with no output.
- `git diff --stat` reported tracked changes in `AGENT_STATUS.md` and
  `CURRENT_SLICE.md`; the untracked Slice 1 plan was visible in
  `git status --short`.
- `git status --short` showed `M AGENT_STATUS.md`, `M CURRENT_SLICE.md`,
  `?? inventory/model-dispatch-first-class-repo-plan.md`, and `?? tools/`.

## Previous status — Slice 0 baseline inventory

Slice 0 baseline inventory and freeze point documentation update was completed
and made ready for review.

Previous task:
Create a documentation-only baseline inventory before any live service changes.

What changed:

- `CURRENT_SLICE.md` defined the active slice as "Baseline inventory and freeze
  point."
- `inventory/baseline-2026-05-17.md` was added as the Slice 0 baseline
  inventory and freeze point.
- `AGENT_STATUS.md` was updated with that handoff while preserving older history
  below.

The baseline recorded:

- Host roles and known LAN/Tailscale IPs.
- Open WebUI route.
- `model-dispatch` service path, port, endpoint, and current/target role.
- LiteLLM rollback/history status.
- OpenRouter-free artifact posture.
- Current known model endpoints.
- OpenCode current routing posture.
- Continue.dev current routing posture.
- CodeGraphContext/MCP posture.
- Git source and mirror posture.
- Backup/off-site roles.
- Known untracked repo path: `tools/`.

What did not change:
No live services, production configs, OpenCode config, MCP config, or
`model-dispatch` runtime files were changed.

No Docker state, systemd state, repo locations, scripts, daemons, watchers,
hidden automation, paid-provider fallback, model API calls, network calls, or
`tools/` files were changed.

Files changed:

- `CURRENT_SLICE.md`
- `inventory/baseline-2026-05-17.md`
- `AGENT_STATUS.md`

Checks run:

- `git diff --check`
- `git diff --stat`
- `git status --short`

Results:

- `git diff --check` passed with no output.
- `git diff --stat` reported tracked changes in `AGENT_STATUS.md` and
  `CURRENT_SLICE.md`; the untracked baseline file was visible in
  `git status --short`.
- `git status --short` showed `M AGENT_STATUS.md`, `M CURRENT_SLICE.md`,
  `?? inventory/baseline-2026-05-17.md`, and `?? tools/`.

## Previous status — Architecture transition planning

Documentation-only architecture transition slice was started and made ready for
review. The status file was repaired so prior useful history remained available
below that handoff.

Previous task:
Start a new active slice: "Architecture transition planning and model-dispatch
repo preparation."

What changed:

- `CURRENT_SLICE.md` defined the active transition-planning slice, including
  scope, non-scope, validation steps, and definition of done.
- `DECISIONS.md` recorded the 2026-05-17 decision to centralize model routing
  through `model-dispatch`, make Strix the canonical source/code-graph host, and
  make AMD a mode-switched GPU compute worker.
- `ROADMAP.md` included the ordered architecture transition plan from slice 0
  through slice 15.
- `HOMELAB_LAYOUT.md` included the target platform architecture and final
  desired host roles.
- `WORKFLOW.md` included the Codex-assisted deployment rule.
- `AGENT_STATUS.md` preserved useful prior status history under
  `Archived Status History` instead of replacing it.

What did not change:
No live services, production configs, OpenCode config, MCP config, or
`model-dispatch` runtime files were changed.

No scripts, daemons, watchers, hidden automation, paid-provider fallback, model
API calls, or network calls were added.

Files changed:

- `CURRENT_SLICE.md`
- `DECISIONS.md`
- `ROADMAP.md`
- `HOMELAB_LAYOUT.md`
- `WORKFLOW.md`
- `AGENT_STATUS.md`

Checks run:

- `git diff --check`
- `git diff --stat`
- `git diff -- AGENT_STATUS.md | sed -n '1,260p'`

Results:

- `git diff --check` passed with no output.
- `git diff --stat` reported 6 files changed, 403 insertions, and 69 deletions
  across the full uncommitted docs diff.
- The scoped `AGENT_STATUS.md` diff showed the current architecture transition
  handoff followed by restored archived history.

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
