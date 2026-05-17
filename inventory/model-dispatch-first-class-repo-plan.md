# model-dispatch First-Class Repo Plan

## Purpose

Prepare `model-dispatch` to become a first-class, source-controlled repo without
changing the live service in this slice.

The goal is to move from an incidental live service directory toward a reviewed
source repo and mirror layout:

```text
Target source repo: strix:/srv/projects/model-dispatch
Target tier-1 mirror: thinkcentre:/srv/git/model-dispatch.git
Documented live service path: thinkcentre:/srv/model-dispatch
```

This document is planning and approval preparation only. It does not create the
repo, copy runtime files, restart services, edit service units, or deploy
anything.

## Current Documented Live State

From `ROUTING_INVENTORY.md`, `HOMELAB_LAYOUT.md`,
`DECISIONS.md`, and `inventory/baseline-2026-05-17.md`:

| Field | Documented value |
|---|---|
| Host | `thinkcentre` |
| Live path | `/srv/model-dispatch` |
| Service | `model-dispatch.service` |
| Port | `4010` |
| Endpoint | `http://192.168.50.225:4010/v1` |
| Current role | Active Open WebUI OpenAI-compatible endpoint |
| Current clients | Open WebUI |
| Future target clients | Open WebUI, OpenCode, Continue.dev, scripts |
| Open WebUI model API target | `http://192.168.50.225:4010/v1` |
| LiteLLM status | Rollback/history only |
| Direct AMD routing status | Current OpenCode default and future rollback until replaced |

Documented exposed model categories:

- `auto-local`
- `auto-coding-local`
- `auto-reasoning-local`
- `auto-small-local`
- `strix-reasoning-qwen3.6-65k`
- `strix-coder-qwen3-coder-next-65k`
- `amd-coder-qwen3-coder-30b-32k`
- `amd-backup-gemma4-26b-8k`
- `openrouter-free/openrouter/auto-free-router`
- `openrouter-free/<verified-model>:free` entries

Documented behavior to preserve:

- Local-first routing.
- Explicit local model selection.
- Explicit/manual OpenRouter-free exposure.
- Fail-closed free-model filtering through a verified allowlist.
- Forced `stream: false` for upstream chat completion requests where
  `model-dispatch` expects non-streaming JSON responses.
- No exposure of the broad paid OpenRouter catalog.

## Target Repo Layout

Target canonical source repo:

```text
strix:/srv/projects/model-dispatch
```

Target tier-1 mirror:

```text
thinkcentre:/srv/git/model-dispatch.git
```

Live service path remains separate until a later approved deployment slice:

```text
thinkcentre:/srv/model-dispatch
```

Planned ownership model:

- Strix repo is the source-of-truth working tree.
- ThinkCentre bare repo is the tier-1 mirror.
- ThinkCentre live path remains the runtime deployment path.
- Live path is updated only by an approved operator action after validation.

## Proposed Future Repo Contents

The exact file inventory must be confirmed by a read-only inspection of
`/srv/model-dispatch` in a later approved step. Expected repo shape:

```text
model-dispatch/
  README.md
  DECISIONS.md
  DEPLOYMENT.md
  ROUTING.md
  SERVICE.md
  .gitignore
  pyproject.toml or requirements.txt
  src/ or app files copied from the live service
  config/
    model registry and route definitions
    OpenRouter-free allowlist inputs or references
  tests/
    unit or smoke tests for route selection and non-streaming upstream behavior
  docs/
    validation notes
    rollback notes
```

Suggested minimum docs:

- `README.md`: what the service does, clients, local development basics.
- `ROUTING.md`: stable aliases, endpoint classes, fallback rules, and non-goals.
- `SERVICE.md`: service name, port, live path, environment assumptions, and
  operator-only restart/deploy notes.
- `DEPLOYMENT.md`: reviewed deployment path, validation, rollback commands, and
  explicit approval requirements.
- `DECISIONS.md`: local decision log for routing changes.

Suggested `.gitignore` policy:

- Ignore secrets and `.env` files.
- Ignore caches, virtualenvs, logs, request logs, generated runtime files, and
  local test artifacts.
- Do not ignore source, route definitions, test fixtures, or docs needed to
  reproduce behavior.

## Exact Non-Goals

- Do not create `strix:/srv/projects/model-dispatch` in this slice.
- Do not create `/srv/projects/model-dispatch` in this slice.
- Do not create `thinkcentre:/srv/git/model-dispatch.git` in this slice.
- Do not copy `/srv/model-dispatch` in this slice.
- Do not edit `/srv/model-dispatch`.
- Do not edit `model-dispatch.service`.
- Do not restart or reload `model-dispatch.service`.
- Do not change Open WebUI config.
- Do not change OpenCode config.
- Do not change Continue.dev config.
- Do not change LiteLLM config.
- Do not change Docker or systemd state.
- Do not enable MCP.
- Do not add scripts in this repo.
- Do not add hidden automation, daemons, watchers, scheduled sync, autonomous
  approval behavior, paid fallback, or broad orchestration.
- Do not expose paid OpenRouter models.

## Risks

- The documented live path may contain secrets, `.env` files, logs, generated
  files, caches, or machine-local artifacts that must not be committed.
- Copying live files without a review step could accidentally source-control
  runtime-only state.
- Changing the live service path, unit, or config could break Open WebUI because
  `model-dispatch` is the active OpenAI-compatible endpoint.
- A premature repo/deploy coupling could make rollback harder than the current
  simple live directory.
- OpenRouter-free filtering must stay fail-closed; accidental paid-model
  exposure would violate standing constraints.
- OpenCode and Continue.dev migrations are later slices and should not be
  bundled into repo preparation.
- Direct AMD routing and LiteLLM rollback need to remain available until
  replacements are validated.

## Rollback Thinking

The safest transition keeps source control separate from runtime until a later
approved deployment step.

Rollback posture during repo preparation:

- Keep `thinkcentre:/srv/model-dispatch` as the untouched live runtime.
- Keep `model-dispatch.service` unchanged.
- Keep Open WebUI pointed at `http://192.168.50.225:4010/v1`.
- Keep LiteLLM as rollback/history.
- Keep OpenCode direct AMD routing unchanged.
- If a future repo copy is wrong, discard or repair the source repo before any
  deployment.
- If a future deployment breaks Open WebUI, restore the previous live
  `/srv/model-dispatch` snapshot and restart only after operator approval.

## Validation Needed Before Touching Live Service

Before any live service change, validate from reviewed source:

- The source repo excludes secrets, `.env`, logs, caches, request logs, and
  generated runtime artifacts.
- The repo contains enough code/config/docs to reproduce current behavior.
- Route aliases match the documented baseline.
- `/v1/models` returns the expected stable aliases.
- `/v1/chat/completions` works for:
  - `auto-local`
  - `auto-coding-local`
  - `auto-reasoning-local`
  - `auto-small-local`
  - one explicit Strix model
  - one explicit AMD model
  - `openrouter-free/openrouter/auto-free-router` only if intentionally tested
- Upstream forwarding still forces non-streaming JSON where required.
- OpenRouter-free entries remain verified free-only and fail-closed.
- Open WebUI can still use the endpoint after any deployment candidate.
- Rollback command block is written and reviewed before deployment.

## Operator Approval Brief Template

Decision requested:
Approve or reject the next step to create a source-controlled
`model-dispatch` repo from the current live service contents without changing
the live service.

Available options:

- Option A: Create a Strix source repo from a reviewed copy of
  `thinkcentre:/srv/model-dispatch`, excluding secrets, logs, caches, `.env`,
  generated runtime files, and machine-local artifacts. This best matches Slice
  1.
- Option B: Keep planning only and defer repo creation. This is safest if the
  live directory contents are not yet understood.
- Option C: Couple repo creation with live service deployment. This risks scope
  drift and should be rejected for Slice 1.

Recommended option:
Option A, but only after a read-only inventory of `/srv/model-dispatch` is
approved and reviewed.

What could break if the wrong option is chosen:

- Secrets or logs could be committed.
- Open WebUI could lose its active model endpoint.
- Paid OpenRouter exposure could be introduced accidentally.
- Rollback could become unclear if source-control setup and deployment are mixed.

Exact next prompt to continue safely:

```text
Proceed with a read-only inventory of thinkcentre:/srv/model-dispatch for Slice
1. Do not copy files, create repos, restart services, or edit live config. Record
the file inventory, likely include/exclude rules, and any blockers in the
homelab repo for review.
```

## Proposed Future Command Blocks — NOT RUN

These are draft operator command blocks for later review. They were not run in
this slice.

### Read-only live inventory — NOT RUN

```bash
ssh thinkcentre 'find /srv/model-dispatch -maxdepth 3 -type f -o -type d | sort'
ssh thinkcentre 'find /srv/model-dispatch -maxdepth 3 -type f -printf "%p\n" | sort'
ssh thinkcentre 'find /srv/model-dispatch -maxdepth 3 \( -name ".env" -o -name "*.log" -o -path "*/__pycache__/*" -o -path "*/.venv/*" \) -print'
```

Purpose:
Inventory file shape and identify obvious excludes. This should not read secret
contents.

### Create Strix source repo from reviewed copy — NOT RUN

```bash
mkdir -p /srv/projects/model-dispatch
rsync -a --exclude '.git/' --exclude '.env' --exclude '*.log' --exclude '__pycache__/' --exclude '.venv/' thinkcentre:/srv/model-dispatch/ /srv/projects/model-dispatch/
cd /srv/projects/model-dispatch
git init
git status --short
```

Purpose:
Create an initial source repo candidate from reviewed live files. This must not
be run until include/exclude rules are approved.

### Create ThinkCentre tier-1 mirror — NOT RUN

```bash
ssh thinkcentre 'mkdir -p /srv/git/model-dispatch.git && cd /srv/git/model-dispatch.git && git init --bare'
cd /srv/projects/model-dispatch
git remote add thinkcentre thinkcentre:/srv/git/model-dispatch.git
git push -u thinkcentre main
```

Purpose:
Create the tier-1 bare mirror after the Strix source repo is reviewed and
committed.

### Candidate validation without deployment — NOT RUN

```bash
cd /srv/projects/model-dispatch
git status --short
git diff --check
```

Purpose:
Validate the source repo candidate before any live service deployment is
considered.

## Slice 1 Definition of Done

- This plan exists in the homelab repo.
- The current documented live state is captured.
- Target repo and mirror paths are documented.
- Future repo contents and excludes are proposed.
- Non-goals, risks, rollback thinking, validation, and approval brief template
  are documented.
- Proposed commands are clearly marked `NOT RUN`.
- No live service files, repo locations, service state, or runtime config were
  changed.
