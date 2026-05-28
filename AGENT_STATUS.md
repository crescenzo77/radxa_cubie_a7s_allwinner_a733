# Agent Status

## Current status

The active slice is `Strix vLLM local-agent validation checkpoint complete`.

## Current task

Preserve the current validated Strix vLLM and Aider compatibility state. Do not
promote Aider or change default routes without a new explicit slice.

## What changed

- Added and validated the Strix Qwen3.6 AWQ Compose runtime.
- Added and validated the Coder-Next AWQ manual test runtime.
- Added `scripts/model-tool-loop-smoke` and defaulted it to `local/tool-test`.
- Added `scripts/strix-vllm-mode` to switch the one-port Strix runtime between
  `tool` and `code` modes with readiness and smoke validation.
- Proved `local/tool-test` and `local/code-test` through model-dispatch.
- Proved Aider `0.86.2` can make one bounded throwaway edit through
  `local/code-test`.
- Added `scripts/aider-code-test` to preserve the validated Aider command shape
  while refusing to run unless Coder-Next is active.
- Documented the decisions and runbook updates for these validations.

## What did not change

- Aider was not promoted into the core walking skeleton.
- Aider was not run against the homelab repo for a real workflow edit.
- No auto routes or default model routes were changed.
- `local/tool-test` remains manual/test-only.
- `local/code-test` remains manual/test-only.
- Only one Strix vLLM runtime is active on port `8010` at a time.
- Strix was restored to `tool` mode after Coder-Next and Aider tests.
- No `/srv/model-dispatch` files were changed in this checkpoint.
- No Open WebUI config was changed.
- No OpenCode config was changed.
- No Continue.dev config was changed.
- No LiteLLM config was changed.
- No dashboard, monitoring, or observability config was changed.
- No systemd units, daemons, watchers, schedulers, hidden jobs, or approval
  automation were added.

## Files changed

Recently changed by this checkpoint:

- `DECISIONS.md`
- `docs/aider-workflow.md`
- `runbooks/strix-vllm-qwen36-awq-agent.md`
- `runtime/strix-qwen3-coder-next-awq-test/compose.yml`
- `scripts/aider-code-test`
- `scripts/strix-vllm-mode`
- `CURRENT_SLICE.md`
- `PROJECT_PLAN.md`
- `AGENT_STATUS.md`
- `ROADMAP.md`
- `WORKFLOW.md`

## Checks run

- `scripts/model-tool-loop-smoke`
- `scripts/model-tool-loop-smoke --model local/code-test`
- `scripts/strix-vllm-mode code`
- `scripts/strix-vllm-mode tool`
- `scripts/aider-code-test` failure path in `tool` mode.
- `scripts/aider-code-test` success path in a throwaway repo while in `code`
  mode.
- `bash -n scripts/aider-code-test`
- `git diff --check`
- `git status --short`

## Results of checks

- `local/tool-test` passes through model-dispatch when Qwen3.6 is active.
- `local/code-test` passes through model-dispatch when Coder-Next is active.
- Aider edited only the requested file in throwaway repos and exited `0`.
- `scripts/aider-code-test` refuses to run when the wrong Strix runtime is
  active.
- Final live Strix state after tests: `active_mode=tool`.
- Latest pushed checkpoint before this status alignment:
  `6ee8fc0 add local code-test aider helper`.

## Known risks or blockers

- `local/tool-test` and `local/code-test` share Strix port `8010`; they are
  mode-specific, not simultaneously live.
- Aider compatibility is still only proven for tiny, explicit, one-file edits.
- Aider is not validated for broad repo maps, long context, multi-file edits,
  auto-commits, or autonomous coding workflows.
- The existing `/home/enzo/.local/bin/aider-strix-coder` launcher still points
  at the older `8082` llama.cpp/GGUF path, not the validated vLLM Coder-Next
  path.

## User approval needed

Approval is needed before promoting Aider into normal workflow, changing
default routes, making Coder-Next persistent, adding concurrent Strix serving,
editing Open WebUI defaults, changing `model-dispatch`, or adding automation.

## Recommended next action

Stop here or choose one non-critical repo for a real bounded
`scripts/aider-code-test` edit, with manual diff review before commit.

## Archived Status History

Older status entries remain below for continuity. They are not the active task.

## Previous status - Aider compatibility planning

The active slice was `Aider compatibility planning`.

This slice planned how to diagnose why Aider gets empty responses from local
`model-dispatch` aliases without running more Aider trials.

Completed changes:

- Updated `CURRENT_SLICE.md` so the active slice was
  `Aider compatibility planning`.
- Updated `PROJECT_PLAN.md` so the current build stage was
  `Slice 9: Aider compatibility planning`.
- Created `inventory/aider-compatibility-plan.md`.
- Documented observed Aider failures with `openai/coding` and
  `openai/local/amd-coder`.
- Documented likely hypotheses around Aider response format expectations,
  `model-dispatch` alias compatibility, generic aliases versus explicit model
  IDs, and possible Aider metadata, edit format, or provider configuration
  needs.
- Documented local `model-dispatch` checks, direct AMD endpoint checks,
  verified OpenRouter-free fallback rules, what not to do, and validation
  commands for a later slice.

## Previous status - Aider workflow integration

The active slice was `Aider workflow integration`.

This slice updated the homelab workflow docs to reflect the corrected agent
strategy: Codex remains primary for planning, sequencing, and risky
live-service work; Claude Code remains a frontier-code alternative; Aider is
added as the bounded patch assistant for small repo edits; OpenCode is demoted
to a later local-agent experiment; Continue.dev remains editor assist; and
Cline remains sandbox-only.

Completed changes:

- Updated `WORKFLOW.md` with agent division of labor.
- Added the Aider use rule to `WORKFLOW.md`.
- Created `docs/aider-workflow.md`.
- Updated `CURRENT_SLICE.md` so the active slice was
  `Aider workflow integration`.
- Updated `PROJECT_PLAN.md`, `DECISIONS.md`, `ROADMAP.md`,
  `HOMELAB_LAYOUT.md`, and `CODEX_CONTEXT.md` so the corrected strategy was
  reflected across workflow and planning docs.
- Preserved prior Aider elimination and OpenCode routing history as historical
  context instead of deleting it.

## Previous status - additive alias deployment planning

The active slice is `additive model-dispatch alias deployment planning`.

This slice produced a documentation-only deployment plan for adding
`model-dispatch` aliases later. No live routing behavior was changed.

## Current task

Plan an additive `model-dispatch` alias deployment from the reviewed source
repo. Do not change live routing yet.

## What changed

- Updated `CURRENT_SLICE.md` so the active slice is
  `additive model-dispatch alias deployment planning`.
- Created `inventory/model-dispatch-additive-alias-deployment-plan.md`.
- Documented current aliases and IDs to preserve:
  - `auto-local`
  - `auto-coding-local`
  - `auto-reasoning-local`
  - `auto-small-local`
  - explicit Strix and AMD model IDs
  - OpenRouter-free model forms
  - OpenCode direct AMD rollback IDs
  - Continue.dev and LiteLLM rollback posture
- Documented additive aliases to add:
  - `advisor`
  - `reasoning`
  - `coding`
  - `small`
  - `review`
  - `long-code`
  - `local/strix-reasoning`
  - `local/strix-coder`
  - `local/amd-coder`
  - `local/amd-small`
  - `free-cloud`
- Documented required Open WebUI display names.
- Documented exact future `config.json` additions for local aliases.
- Documented that `free-cloud` needs a reviewed source change because current
  `app.py` generates OpenRouter-free IDs outside `config.json`, and the current
  validator rejects route targets not present in `models`.
- Documented files eligible for a later alias deployment.
- Documented backup path as `/srv/model-dispatch/backups/<timestamp>/`.
- Documented future validation commands and rollback plan.
- Documented non-goals.
- Preserved prior slice history below in `CURRENT_SLICE.md`.

## What did not change

- No `/srv/model-dispatch` files were touched.
- No `/srv/projects/model-dispatch` files were touched.
- No service restart or reload was run.
- No Docker, systemd, sudo, deployment, or live endpoint-changing command was
  run.
- No dashboard, monitoring, or observability deployment was started.
- No OpenCode, Continue.dev, Open WebUI, LiteLLM, MCP, reverse proxy, or live
  service config was changed.
- No commit was made.

## Files changed

- `CURRENT_SLICE.md`
- `inventory/model-dispatch-additive-alias-deployment-plan.md`
- `AGENT_STATUS.md`

## Checks run

- Read required homelab docs:
  - `AGENTS.md` from the user-provided repo instructions
  - `CODEX_CONTEXT.md`
  - `CURRENT_SLICE.md`
  - `AGENT_STATUS.md`
  - `PROJECT_PLAN.md`
  - `DECISIONS.md`
  - `HOMELAB_LAYOUT.md`
  - `WORKFLOW.md`
  - `ROADMAP.md`
- Read user-requested docs:
  - `inventory/model-dispatch-alias-registry-plan.md`
  - `inventory/model-dispatch-deployment-plan-2026-05-17.md`
  - `inventory/model-dispatch-deployment-approval-brief-2026-05-17.md`
  - `ROUTING_INVENTORY.md`
- Inspected reviewed source repo docs/config only:
  - `/srv/projects/model-dispatch/config.json`
  - `/srv/projects/model-dispatch/ROUTING.md`
  - `/srv/projects/model-dispatch/app.py`
  - `/srv/projects/model-dispatch/tests/check_config.py`
- Requested final checks:
  - `git diff --check`
  - `git diff --stat`
  - `git status --short`

## Results of checks

- `git diff --check`: passed with no output.
- `git diff --stat`:
  - `AGENT_STATUS.md  | 137 +++++++++++++++++++++++++++++++++++--------------------`
  - `CURRENT_SLICE.md |  91 +++++++++++++++++++++++++++---------`
  - `2 files changed, 157 insertions(+), 71 deletions(-)`
  - Note: `git diff --stat` does not include the untracked additive alias
    deployment plan until it is staged or committed.
- `git status --short`:
  - `M AGENT_STATUS.md`
  - `M CURRENT_SLICE.md`
  - `?? inventory/model-dispatch-additive-alias-deployment-plan.md`

## Known risks or blockers

- Alias deployment would affect model routing and needs a separate explicit
  deployment slice.
- The `free-cloud` alias is not a pure `config.json` addition in the current
  reviewed source shape. It needs a small reviewed source change so it maps
  exactly to `openrouter-free/openrouter/auto-free-router` instead of falling
  through to `auto-local`.
- OpenCode and Continue.dev changes should remain separate explicit slices after
  aliases are validated.
- Existing model IDs should be preserved during any first alias deployment to
  avoid breaking Open WebUI or rollback paths.
- `long-code` points to `auto-coding-local` for now and needs large-context
  validation because the first target in that route is the AMD 32k coder.
- Direct AMD routing and LiteLLM rollback should remain documented until
  replacement paths are validated.
- Dashboards, monitoring, and observability remain deferred and require a
  separate explicit slice and operator approval.

## User approval needed

No approval is needed for this documentation-only planning slice because the
user explicitly requested it.

Approval will be needed before any live `model-dispatch` config change,
source repo implementation change, OpenCode config change, Continue.dev config
change, Open WebUI config change, MCP enablement, Docker/systemd change,
monitoring/dashboard deployment, push, or deployment.

## Recommended next action

Review `inventory/model-dispatch-additive-alias-deployment-plan.md`.

If accepted, the next safe slice is a reviewed source-repo implementation in
`/srv/projects/model-dispatch` that adds the local aliases to `config.json` and
implements an exact `free-cloud` alias without touching live
`/srv/model-dispatch`.

## Previous status - alias registry cleanup planning

The active slice was `model-dispatch alias registry cleanup planning`.

That slice made a documentation-only correction to the alias registry plan. No
live routing behavior was changed.

What changed:

- Updated `CURRENT_SLICE.md` so the active slice was
  `model-dispatch alias registry cleanup planning`.
- Created `inventory/model-dispatch-alias-registry-plan.md`.
- Documented current exposed model IDs, proposed stable aliases,
  compatibility aliases to preserve, validation requirements, rollback
  expectations, and display-name requirements.

What did not change:

No `/srv/model-dispatch` files, source repo files, service state, Docker,
systemd, sudo, OpenCode, Continue.dev, Open WebUI, LiteLLM, MCP, reverse proxy,
dashboards, monitoring, observability, benchmark code, `tools/` files, or
commits were changed.

## Previous status - deployment planning correction

The active slice was `model-dispatch deployment planning only`.

The deployment docs were updated after a failed `model-dispatch` deployment
attempt. The attempt started from `strix:/srv/projects/model-dispatch` and
stopped before copying files because backup directory creation failed with
`mkdir: Permission denied` at `/srv/model-dispatch-backups/<timestamp>`.

The live service remained healthy, and no deployment completed during that
attempt.

What changed:

- Updated `inventory/model-dispatch-deployment-plan-2026-05-17.md` to:
  - replace `/srv/model-dispatch-backups/<timestamp>` with
    `/srv/model-dispatch/backups/<timestamp>`
  - document that the earlier `/srv/model-dispatch-backups/<timestamp>` path
    failed because `/srv` is root-owned and backup directory creation returned
    `mkdir: Permission denied`
  - state that the failed attempt stopped before file copy and no live files
    were changed
- Updated `inventory/model-dispatch-deployment-approval-brief-2026-05-17.md`
  to use `/srv/model-dispatch/backups/<timestamp>` for the backup destination
  and rollback reference.

What did not change:

No deployment completed. The failed deployment attempt stopped before file copy.

No live services, production configs, OpenCode config, Open WebUI config, MCP
config, Docker state, systemd state, reverse proxy settings, SearXNG settings,
monitoring stack, observability stack, dashboard stack, or `model-dispatch`
runtime files were changed.

No files were copied to `/srv/model-dispatch`.

No service restart, reload, deploy command, push, Docker command, systemd
command, sudo command, or `/srv/litellm/.env` read occurred.

No homelab `tools/` files were touched.

No `/srv/model-dispatch` files were edited.

No homelab commit was made.

Dashboards, monitoring, and observability remained deferred.

## Previous status - local smoke-check scaffold

The Strix `model-dispatch` source repo candidate at
`/srv/projects/model-dispatch` now has a local-only smoke-check scaffold and a
first local commit.

Previous task:
Record the completed next local-only `model-dispatch` candidate repo step in
the homelab handoff, without touching `tools/`, committing, changing live
services, or editing the live `/srv/model-dispatch` path.

What changed:

- Added a local smoke-check scaffold in `/srv/projects/model-dispatch`.
- Added `/srv/projects/model-dispatch/tests/check_config.py`.
- Added `/srv/projects/model-dispatch/TESTING.md`.
- Updated `/srv/projects/model-dispatch/DECISIONS.md` to record that local
  tests avoid importing `app.py` because `app.py` has live-path side effects.
- Added `/srv/projects/model-dispatch/AGENT_STATUS.md`.
- Created the local `model-dispatch` commit:
  `add local config smoke check`.
- Updated the homelab handoff.

What did not change:

No live `/srv/model-dispatch` files were edited.

No live services, production configs, OpenCode config, Open WebUI config, MCP
config, Docker state, systemd state, reverse proxy settings, SearXNG settings,
or `model-dispatch` runtime files were changed.

No service restart, deploy, push, mirror creation, endpoint call, or
`/srv/litellm/.env` read occurred.

No homelab `tools/` files were touched.

No homelab commit was made.

`__pycache__` was created by `py_compile` in `/srv/projects/model-dispatch`,
but it is ignored by `.gitignore` and is not shown in Git status.

## Previous status - source repo candidate creation

The Strix `model-dispatch` source repo candidate was created for review at
`/srv/projects/model-dispatch`.

Previous task:
Create a source repo candidate at `/srv/projects/model-dispatch` using only the
reviewed include list from `thinkcentre:/srv/model-dispatch`, without deploying
anything or touching the live service.

What changed:

- Created `/srv/projects/model-dispatch`.
- Copied only the approved files from `thinkcentre:/srv/model-dispatch` using
  the LAN IP `192.168.50.225`:
  - `app.py`
  - `config.json`
  - `.gitignore`
  - `.cgcignore`
- Initialized Git in `/srv/projects/model-dispatch`.
- Added review-only repo docs in `/srv/projects/model-dispatch`:
  - `README.md`
  - `ROUTING.md`
  - `SERVICE.md`
  - `DEPLOYMENT.md`
  - `DECISIONS.md`
- Tightened `/srv/projects/model-dispatch/.gitignore` to explicitly exclude
  logs, request logs, backups, env files, secrets, tokens, keys, caches,
  virtualenvs, databases, generated runtime files, and dependency/vendor
  directories.
- Marked files in `/srv/projects/model-dispatch` with `git add -N .` so
  `git diff` and `git diff --check` can review the candidate without staging a
  commit.

What did not change:
No live services, production configs, OpenCode config, Open WebUI config, MCP
config, Docker state, systemd state, reverse proxy settings, SearXNG settings,
or `model-dispatch` runtime files were changed.

No `/srv/model-dispatch` files were edited. No service was restarted or
reloaded. No `sudo` was used.

No `thinkcentre:/srv/git/model-dispatch.git` mirror was created. Nothing was
pushed. No commit was made in `/srv/projects/model-dispatch` or
`/srv/projects/homelab`.

No homelab `tools/` files were touched.

The live `.git/` directory, `dispatch.log`, backup snapshots, env files,
secrets, tokens, keys, databases, sqlite files, caches, virtualenvs, generated
runtime files, and request logs were not copied from the live service.

Checks run:

- Read required homelab docs:
  - `AGENTS.md`
  - `CODEX_CONTEXT.md`
  - `PROJECT_PLAN.md`
  - `CURRENT_SLICE.md`
  - `DECISIONS.md`
  - `AGENT_STATUS.md`
  - `inventory/model-dispatch-first-class-repo-plan.md`
  - `inventory/model-dispatch-live-inventory-2026-05-17.md`
- Ran candidate repo setup commands:
  - `mkdir -p /srv/projects/model-dispatch`
  - `scp -F /dev/null 192.168.50.225:/srv/model-dispatch/app.py /srv/projects/model-dispatch/app.py`
  - `scp -F /dev/null 192.168.50.225:/srv/model-dispatch/config.json /srv/projects/model-dispatch/config.json`
  - `scp -F /dev/null 192.168.50.225:/srv/model-dispatch/.gitignore /srv/projects/model-dispatch/.gitignore`
  - `scp -F /dev/null 192.168.50.225:/srv/model-dispatch/.cgcignore /srv/projects/model-dispatch/.cgcignore`
  - `git init`
  - `git add -N .`
- Ran requested validation checks:
  - `cd /srv/projects/model-dispatch && git status --short`
  - `cd /srv/projects/model-dispatch && find . -maxdepth 2 -type f | sort`
  - `cd /srv/projects/model-dispatch && git diff --check`
  - `cd /srv/projects/homelab && git status --short`
  - `cd /srv/projects/homelab && git diff --check`
  - `cd /srv/projects/homelab && git diff --stat`

Results:

- Required docs were present and readable.
- `/srv/projects/model-dispatch` `git status --short` showed intent-to-add
  entries for the candidate files.
- `/srv/projects/model-dispatch` `git diff --check` passed with no output.
- `/srv/projects/homelab` `git status --short` initially showed:
  - `?? tools/`
- `/srv/projects/homelab` `git diff --check` passed with no output.

## Previous status — Slice 1 read-only live inventory

Slice 1 read-only live inventory of `thinkcentre:/srv/model-dispatch` was
completed and made ready for review.

Previous task:
Document the live `model-dispatch` file shape for include/exclude planning
without creating repos, copying files, restarting services, editing live config,
or reading secret contents.

What changed:

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
- `AGENT_STATUS.md` was updated with that handoff while preserving older history
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

What did not change:
No live services, production configs, OpenCode config, MCP config, or
`model-dispatch` runtime files were changed.

No Docker state, systemd state, repo locations, scripts, daemons, watchers,
hidden automation, paid-provider fallback, model API calls, network calls, or
`tools/` files were changed.

No `/srv/projects/model-dispatch` repo was created. No
`thinkcentre:/srv/git/model-dispatch.git` mirror was created. No
`/srv/model-dispatch` files were copied. No file contents were printed.

Files changed:

- `inventory/model-dispatch-live-inventory-2026-05-17.md`
- `AGENT_STATUS.md`

Checks run:

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

Results:

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
- `git status --short` showed:
  - `M AGENT_STATUS.md`
  - `?? inventory/model-dispatch-live-inventory-2026-05-17.md`
  - `?? tools/`

Known risks or blockers:

- `config.json` was identified by name only and still needed user review for
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

User approval needed:
No approval was needed for that docs-only update.

Recommended next action:
Review `inventory/model-dispatch-live-inventory-2026-05-17.md`, then decide
whether to approve the next narrow step: creating a Strix source repo candidate
from the reviewed include list only. If `config.json` has not been manually
reviewed safe, review it before copying it.

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

## 2026-05-17 — model-dispatch mirror documented in source repo

The `model-dispatch` source repo on Strix is now mirrored to ThinkCentre.

Source repo:
- `strix:/srv/projects/model-dispatch`

Mirror:
- `thinkcentre:/srv/git/model-dispatch.git`

Latest mirrored commit:
- `7cbb1d9 document thinkcentre mirror creation`

Previous source repo commits:
- `02679e7 add local config smoke check`
- `43b1f72 initialize model-dispatch source candidate`

What did not change:
- No deployment to live `/srv/model-dispatch`.
- No `model-dispatch.service` restart or reload.
- No Open WebUI, OpenCode, LiteLLM, Docker, systemd, MCP, reverse proxy, dashboard, monitoring, or observability change.

Current boundary:
- `model-dispatch` is now source-controlled on Strix and mirrored to ThinkCentre.
- It remains review-only.
- Deployment requires a later explicit deployment slice and rollback brief.

## 2026-05-17 — model-dispatch deployment documented in source repo

The live `model-dispatch` deployment was completed and documented in the `model-dispatch` source repo.

Source repo:
- `strix:/srv/projects/model-dispatch`

Latest source repo commit:
- `54e89c5 document live deployment`

Mirror:
- `thinkcentre:/srv/git/model-dispatch.git`

Live path:
- `thinkcentre:/srv/model-dispatch`

Backup:
- `/srv/model-dispatch/backups/20260517-212158`

Validation:
- `/health` returned `{"status": "ok"}`.
- `/v1/models` returned local routes and OpenRouter-free entries.
- `/v1/chat/completions` using `auto-local` returned a valid OpenAI-compatible response.
- `auto-local` selected `amd-coder-qwen3-coder-30b-32k`.
- Test response content was `OK`.

Cleanup:
- Removed accidental empty `main` file from `/srv/projects/model-dispatch` before commit.

What did not change:
- No Open WebUI config change.
- No OpenCode config change.
- No LiteLLM config change.
- No Docker, MCP, reverse proxy, dashboard, monitoring, or observability change.

Known follow-up:
- `model-dispatch.service` has a pre-existing invalid `Restart=unless-stopped` warning. Consider a separate tiny service-unit fix later.

## 2026-05-17 — model-dispatch systemd restart policy fixed

Fixed the pre-existing invalid restart policy in the live ThinkCentre systemd unit for `model-dispatch.service`.

Change:
- Replaced invalid `Restart=unless-stopped`
- With valid `Restart=on-failure`

Backup:
- `/etc/systemd/system/model-dispatch.service.backup.20260517-212830`

Validation:
- `systemctl daemon-reload` completed.
- `model-dispatch.service` restarted successfully.
- Service is active/running.
- `/health` returned `{"status": "ok"}`.
- `/v1/chat/completions` using `auto-local` returned a valid OpenAI-compatible response.
- `auto-local` selected `amd-coder-qwen3-coder-30b-32k`.
- Response content was `ok`.

What did not change:
- No Open WebUI config change.
- No OpenCode config change.
- No LiteLLM config change.
- No Docker, MCP, reverse proxy, dashboard, monitoring, or observability change.

## 2026-05-18 — additive model-dispatch aliases implemented in source repo

The additive alias implementation was completed in the `model-dispatch` source repo.

Source repo:
- `strix:/srv/projects/model-dispatch`

Latest source commit:
- `bf49923 add additive dispatch aliases`

What changed in source:
- Added additive aliases in `config.json`.
- Added descriptive Open WebUI display names.
- Added nested route expansion in `app.py`.
- Added explicit `free-cloud` handling so it resolves to `openrouter-free/openrouter/auto-free-router`.
- Updated `tests/check_config.py` to validate direct and expanded route targets.
- Updated `TESTING.md`, `DECISIONS.md`, and `AGENT_STATUS.md`.

Validation:
- `git diff --check` passed.
- `python3 -m py_compile app.py` passed.
- `python3 -m json.tool config.json` passed.
- `python3 tests/check_config.py` passed with `config check passed`.
- Source repo was pushed to `thinkcentre/main`.

What did not change:
- No live `/srv/model-dispatch` deployment.
- No `model-dispatch.service` restart or reload.
- No Open WebUI config change.
- No OpenCode config change.
- No Continue.dev config change.
- No Docker, systemd, MCP, dashboard, monitoring, or observability change.

Next:
- Prepare a deployment approval brief for the additive alias deployment before touching live `/srv/model-dispatch`.

## 2026-05-18 — additive alias deployment committed to homelab docs

The additive `model-dispatch` alias deployment record was committed and pushed.

Homelab commit:
- `24ce0dd document additive alias deployment`

Deployment state:
- Additive aliases are live.
- `/health` validated.
- `/v1/models` lists the new aliases.
- `advisor` and `local/amd-coder` validated through `/v1/chat/completions`.

Backup:
- `/srv/model-dispatch/backups/20260518-093534`

Next:
- Update `CURRENT_SLICE.md` to mark additive alias deployment complete.

## Aider bounded patch trial — local model response failure

Aider was tested on one harmless docs-only edit using the local `model-dispatch` alias `coding`.

Command shape:
- `aider docs/aider-workflow.md --model openai/coding --no-auto-commits`

Result:
- Aider started successfully.
- Aider was limited to `docs/aider-workflow.md`.
- Aider asked whether to add `AGENT_STATUS.md`; user answered no.
- Aider asked whether to add `CURRENT_SLICE.md`; user skipped additional files.
- The local model returned an empty response.
- No edit was made to `docs/aider-workflow.md`.

What changed:
- `CURRENT_SLICE.md` contains the manually added Aider bounded patch test slice.

What did not change:
- No live service was touched.
- No `/srv/model-dispatch` file was touched.
- No OpenCode, Continue.dev, Open WebUI, LiteLLM, Docker, systemd, dashboard, monitoring, or observability config changed.
- Aider did not commit.

Conclusion:
- Aider is installed and can be constrained to one file.
- The local `coding` alias is not yet proven usable with Aider.
- Next Aider trial should use a known-working frontier model or a separately validated Aider-compatible local model profile.

## Aider local-model compatibility trial

Aider was tested with local `model-dispatch` aliases.

Trials:
- `openai/coding`
- `openai/local/amd-coder`

Result:
- Aider started successfully.
- Aider could be constrained to `docs/aider-workflow.md`.
- Aider asked to add extra files; user declined/skipped them.
- Both local model attempts returned an empty response.
- No repository files were changed by Aider.

Conclusion:
- Aider is installed and can be constrained to one file.
- The current local `model-dispatch` aliases are not yet proven compatible with Aider's edit workflow.
- Non-Codex agentic work must use either a local LLM or a verified free OpenRouter model from the allowlist.
- Do not use paid frontier models for Aider/OpenCode/Cline-style agentic work.

Next:
- Create a dedicated Aider compatibility slice before further Aider trials.

## AMD and Strix vLLM readiness inspection

Read-only AMD, Strix, and ThinkCentre routing inspection was performed for the Codex/Aider/vLLM architecture plan.

AMD findings:
- Host `AMD` is reachable.
- RTX 3090 is visible through `nvidia-smi`.
- NVIDIA driver reports CUDA 13.2 support.
- RTX 3090 VRAM is mostly occupied by the current `qwen3-coder-30b` llama.cpp container.
- `rocm-smi` is present and reports AMD GPU devices, but emitted a low-power/device warning.
- Current model containers are healthy:
  - `qwen3-coder-30b` on port 8083.
  - `gemma4-7900xt` on port 8084.
- Existing AMD model endpoints return OpenAI-compatible `/v1/models`.
- `vllm` was not found in the current user path.
- Python is 3.14.4.

Strix findings:
- Host `strix` is reachable.
- Strix Halo Vulkan/RADV device is visible as `Radeon 8060S Graphics (RADV STRIX_HALO)`.
- `rocm-smi` and `rocminfo` are not available.
- `vllm` and `lemonade` were not found in the current user path.
- Current Strix llama.cpp Vulkan containers are healthy:
  - `qwen3-6` on port 8081.
  - `qwen3-coder` on port 8082.
- Existing Strix model endpoints return OpenAI-compatible `/v1/models`.
- Port 8000 is already used by `legacy-printer-app`.

ThinkCentre/model-dispatch findings:
- `model-dispatch` health returned `{"status": "ok"}`.
- `model-dispatch` exposes local AMD and Strix aliases plus OpenRouter-free entries.
- Open WebUI remains routed to `http://192.168.50.225:4010/v1`.
- Open WebUI has Ollama disabled and web search enabled.

Conclusion:
- AMD is the better first vLLM candidate because the NVIDIA/CUDA path is already visible and the coding model role lives there.
- Strix should remain a later vLLM/Lemonade/ROCm readiness slice because ROCm tools are not currently present and port 8000 is occupied.
- Do not run vLLM yet.
- Do not stop existing model containers yet.
- Do not change model-dispatch or Open WebUI routing yet.

Next:
- Plan an AMD-first vLLM validation slice.
- That slice must account for current RTX 3090 VRAM usage before starting any vLLM server.

## AMD vLLM validation planning

The active slice is `AMD vLLM validation planning`.

What changed:
- Updated `CURRENT_SLICE.md` for the AMD-first vLLM validation planning slice.
- Updated `PROJECT_PLAN.md` so the current build stage is `Slice 13: AMD vLLM validation planning`.
- Created `inventory/amd-vllm-validation-plan.md`.

Purpose:
- Plan AMD-first vLLM validation without starting vLLM, installing vLLM, stopping existing containers, changing `model-dispatch`, or changing Open WebUI.

Key planning constraints:
- AMD is the first vLLM candidate because the RTX 3090 and CUDA path are visible.
- The current `qwen3-coder-30b` llama.cpp container occupies most RTX 3090 VRAM.
- Do not stop or restart `qwen3-coder-30b` or `gemma4-7900xt` without a separate explicit approval slice.
- Do not run Aider until curl-only vLLM response-shape checks pass.
- Do not add a `model-dispatch` alias until Aider/vLLM compatibility is proven.

What did not change:
- vLLM was not run.
- vLLM was not installed.
- Aider was not run.
- `model-dispatch` was not edited.
- `/srv/model-dispatch` was not touched.
- Open WebUI, OpenCode, Continue.dev, LiteLLM, dashboards, monitoring, and observability were not changed.
- No `sudo`, Docker write command, or systemd write command was run.

Next:
- Review the diff.
- If accepted, commit the AMD vLLM validation plan.
- The next slice should be Phase 1: read-only AMD live-state recheck.

## AMD vLLM Phase 1 live-state recheck

Read-only AMD live-state recheck was performed for the AMD-first vLLM validation plan.

Findings:
- AMD host is reachable.
- RTX 3090 is visible through `nvidia-smi`.
- NVIDIA driver is `595.71.05`.
- `nvidia-smi` reports CUDA `13.2`.
- `nvcc` is present and reports CUDA toolkit `12.4`.
- RTX 3090 VRAM is mostly occupied: about `18299 MiB / 24576 MiB`.
- The active RTX 3090 compute process is `/app/llama-server`, using about `18276 MiB`.
- `qwen3-coder-30b` is running and healthy on port `8083`.
- `gemma4-7900xt` is running and healthy on port `8084`.
- Both existing endpoints return OpenAI-compatible `/v1/models`.
- Both existing endpoints returned simple chat completions.
- `vllm` was not found in the current user path.
- A local Docker image exists for `vllm/vllm-openai:latest`.
- Existing model artifacts found:
  - `/srv/llm/qwen3-coder-30b/models/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
  - `/srv/llm/gemma4-rocm/models/google_gemma-4-26B-A4B-it-Q4_K_M.gguf`

Conclusion:
- AMD remains the correct first vLLM candidate.
- The next step should be read-only inspection of the existing `vllm/vllm-openai:latest` image.
- Do not start vLLM yet because RTX 3090 VRAM is currently occupied by the healthy `qwen3-coder-30b` endpoint.
- Do not stop or restart `qwen3-coder-30b` or `gemma4-7900xt` without a separate approval slice.

What did not change:
- vLLM was not started.
- vLLM was not installed.
- Aider was not run.
- No containers were stopped or restarted.
- No Docker write command was run.
- No systemd or sudo command was run.
- `model-dispatch` and Open WebUI routing were not changed.

Next:
- Phase 2: read-only inspect the local `vllm/vllm-openai:latest` image and candidate runtime method.

## AMD vLLM Phase 2 local image/runtime inspection

Read-only inspection of the local `vllm/vllm-openai:latest` image was performed.

Findings:
- Local image `vllm/vllm-openai:latest` exists on AMD.
- Initial dry-run with `python` failed because the image provides `python3`, not `python`.
- `python3` exists inside the image.
- `vllm` exists inside the image.
- Image Python version is `3.12.13`.
- Torch version is `2.10.0+cu129`.
- Torch CUDA version is `12.9`.
- vLLM version is `0.19.0`.
- The vLLM OpenAI API server help is available through `python3 -m vllm.entrypoints.openai.api_server --help`.
- With `--gpus all`, the image can see the RTX 3090.
- CUDA is available inside the image.
- The image reports one CUDA device:
  `NVIDIA GeForce RTX 3090`.
- Container-visible GPU memory was about:
  - free: `5836898304`
  - total: `25298141184`
- Existing containers remained running after dry checks:
  - `qwen3-coder-30b`
  - `gemma4-7900xt`

Conclusion:
- The local vLLM image is viable enough for a future approved runtime test.
- The next blocker is not image availability; it is RTX 3090 VRAM availability.
- Do not start vLLM yet because `qwen3-coder-30b` is still using most RTX 3090 VRAM.
- Do not stop or restart `qwen3-coder-30b` without a separate approval slice.

What did not change:
- vLLM was not started as a server.
- No vLLM package was installed.
- No image was pulled.
- No containers were stopped or restarted.
- No model-dispatch or Open WebUI routing was changed.
- No Aider trial was run.

Next:
- Plan the approved temporary runtime test, including port, model choice, VRAM freeing decision, exact start command, curl-only checks, and rollback command.

## AMD vLLM local model inventory

A read-only AMD model inventory was performed to determine whether a local HF/safetensors-style model candidate exists for vLLM.

Findings:
- Local HF/safetensors-style model directories were found under `/home/enzo/.cache/huggingface/hub/`.
- Candidate local HF-style models include:
  - `Qwen2.5-1.5B-Instruct`
  - `Qwen2.5-7B-Instruct`
  - `Qwen2.5-Coder-7B-Instruct`
  - `Qwen3-14B-AWQ`
  - `Qwen3.5-35B-A3B-GPTQ-Int4`
  - `cyankiwi/Qwen3-Coder-30B-A3B-Instruct-AWQ-4bit`
- Active llama.cpp GGUF artifacts remain:
  - `/srv/llm/qwen3-coder-30b/models/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
  - `/srv/llm/gemma4-rocm/models/google_gemma-4-26B-A4B-it-Q4_K_M.gguf`
- The HF-like directory summary found tokenizer files and safetensors weights for multiple Qwen candidates.
- `qwen3-coder-30b` remained healthy on port `8083`.
- `gemma4-7900xt` remained healthy on port `8084`.
- RTX 3090 VRAM remained mostly occupied by `/app/llama-server`.

Conclusion:
- Model acquisition is not the immediate next step.
- The next step should be read-only inspection of exact candidate model directories.
- The existing GGUF artifacts remain unsuitable as the first vLLM candidate unless separately proven otherwise.
- Do not stop `qwen3-coder-30b` yet.

Candidate priority:
- For a no-interruption vLLM smoke test, inspect `Qwen2.5-1.5B-Instruct`.
- For a coding-relevant vLLM test, inspect `Qwen2.5-Coder-7B-Instruct`.
- For a larger coding candidate, inspect `cyankiwi/Qwen3-Coder-30B-A3B-Instruct-AWQ-4bit`, but assume it may require freeing RTX 3090 VRAM.

What did not change:
- vLLM was not started.
- No model was downloaded.
- No containers were stopped or restarted.
- No Docker write command was run.
- No model-dispatch or Open WebUI routing was changed.

Next:
- Read-only inspect the exact local candidate directories and choose the first runtime candidate.

## AMD temporary vLLM runtime test succeeded and rolled back

A temporary AMD vLLM runtime test was performed using the downloaded
`Qwen2.5-Coder-7B-Instruct` HF/safetensors model.

Model acquisition:
- Hugging Face authentication was configured on AMD outside Git.
- HF username verification succeeded without exposing the token.
- `Qwen/Qwen2.5-Coder-7B-Instruct` was downloaded to:
  `/srv/llm/hf/Qwen2.5-Coder-7B-Instruct`
- The model directory is about `15G`.
- Safetensors shards are real multi-GB files, not placeholder cache entries.

Temporary vLLM runtime:
- `qwen3-coder-30b` was stopped to free RTX 3090 VRAM.
- `gemma4-7900xt` remained running on port `8084`.
- Temporary vLLM container was started:
  `amd-vllm-temp-test`
- Image:
  `vllm/vllm-openai:latest`
- Model path:
  `/srv/llm/hf/Qwen2.5-Coder-7B-Instruct`
- Served model:
  `amd-vllm-temp-qwen2.5-coder-7b`
- Host port:
  `18000`
- vLLM loaded the model as `Qwen2ForCausalLM`.
- vLLM loaded all four safetensors checkpoint shards successfully.
- vLLM started the OpenAI-compatible server successfully.

Curl validation:
- `GET /v1/models` returned HTTP 200 and listed:
  `amd-vllm-temp-qwen2.5-coder-7b`
- `POST /v1/chat/completions` returned HTTP 200.
- Completion content was:
  `vllm-ok`

Rollback:
- Temporary vLLM container `amd-vllm-temp-test` was stopped.
- `qwen3-coder-30b` was restarted.
- `qwen3-coder-30b` returned healthy on port `8083`.
- `gemma4-7900xt` remained healthy on port `8084`.
- `8083 /v1/models` again returned:
  `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
- `8084 /v1/models` continued returning:
  `google_gemma-4-26B-A4B-it-Q4_K_M.gguf`
- RTX 3090 VRAM returned to the expected llama.cpp state, with `/app/llama-server`
  using about `18212 MiB`.

What changed:
- A real HF/safetensors model now exists at:
  `/srv/llm/hf/Qwen2.5-Coder-7B-Instruct`
- Runtime state was temporarily changed during the approved test and then rolled
  back.

What did not change:
- `model-dispatch` was not edited.
- Open WebUI routing was not changed.
- Aider was not run.
- No vLLM endpoint was added to model-dispatch.
- No persistent vLLM container, Compose file, systemd unit, restart policy,
  wrapper, watcher, or daemon was created.

Conclusion:
- Direct temporary vLLM serving on AMD is proven with a real HF/safetensors
  coding model.
- The next decision is whether to test Aider directly against the temporary vLLM
  endpoint, or first create a dedicated model-dispatch alias plan.

## Direct Aider vLLM one-file docs trial succeeded

Aider was tested directly against the temporary AMD vLLM endpoint.

Endpoint:
- `http://192.168.50.252:18000/v1`

Model:
- `openai/amd-vllm-temp-qwen2.5-coder-7b`

Task:
- One small docs-only edit to `docs/aider-workflow.md`.
- Add section: `Direct vLLM Trial Note`.

Result:
- Aider connected to the direct vLLM endpoint.
- Aider returned a non-empty response.
- Aider edited only `docs/aider-workflow.md`.
- Aider asked to add extra files:
  - `AGENT_STATUS.md`
  - `CURRENT_SLICE.md`
  - `PROJECT_PLAN.md`
  - `AGENTS.md`
  - `CODEX_CONTEXT.md`
  - `DECISIONS.md`
- The user declined each extra file request.
- Aider did not commit.
- `git diff --check` passed.
- `git diff --stat` showed only:
  `docs/aider-workflow.md | 4 ++++`

Conclusion:
- Direct Aider against temporary AMD vLLM is now proven for a one-file docs edit.
- The previous empty-response failure appears tied to the earlier local alias/model-dispatch path, not Aider itself.
- Aider still tries to add context/control files when they are mentioned, so future trials must continue to decline extra files or avoid naming out-of-scope files in the prompt where practical.

What did not change:
- No model-dispatch alias was added.
- Open WebUI routing was not changed.
- No service config was changed.
- No Docker/systemd persistent unit, wrapper, restart policy, or daemon was created.

Next:
- Decide whether to run a second Aider trial with a slightly more realistic one-file patch, or plan a dedicated model-dispatch alias for the proven vLLM endpoint.

## Second direct Aider vLLM one-file docs trial succeeded

A second direct Aider trial was run against the temporary AMD vLLM endpoint.

Endpoint:
- `http://192.168.50.252:18000/v1`

Model:
- `openai/amd-vllm-temp-qwen2.5-coder-7b`

Task:
- Update only `docs/aider-workflow.md`.
- Replace the one-sentence `Direct vLLM Trial Note` with a structured bullet list.

Result:
- Aider connected to the direct AMD vLLM endpoint.
- Aider returned a non-empty response.
- Aider edited only `docs/aider-workflow.md`.
- Aider asked to add extra files:
  - `AGENTS.md`
  - `AGENT_STATUS.md`
  - `CODEX_CONTEXT.md`
  - `CURRENT_SLICE.md`
  - `DECISIONS.md`
  - `PROJECT_PLAN.md`
- The user declined each extra file request.
- Aider did not commit.
- `git diff --check` passed.
- `git diff --stat` showed only:
  `docs/aider-workflow.md | 6 +++++-`

Rollback:
- Temporary vLLM container `amd-vllm-temp-test` was stopped.
- `qwen3-coder-30b` was restarted and became healthy on port `8083`.
- `gemma4-7900xt` stayed healthy on port `8084`.
- `8083 /v1/models` returned:
  `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
- `8084 /v1/models` returned:
  `google_gemma-4-26B-A4B-it-Q4_K_M.gguf`
- RTX 3090 returned to the expected llama.cpp state, with `/app/llama-server`
  using about `18212 MiB`.

Conclusion:
- Direct Aider against AMD vLLM is now proven twice for bounded one-file docs edits.
- Aider still asks to add context/control files, but it respected declined file additions.
- The next sensible step is to plan a dedicated model-dispatch alias for the proven vLLM endpoint, or decide that direct Aider-to-vLLM is sufficient for now.
