# model-dispatch Deployment Plan — 2026-05-17

## Purpose

Plan a future operator-approved deployment from the Strix
`model-dispatch` source repo to the live ThinkCentre service path.

This document is planning only. No deployment happens in this slice. The live
`thinkcentre:/srv/model-dispatch` directory remains untouched, and
`model-dispatch.service` remains untouched.

Dashboards, monitoring, and observability remain deferred. They are not part of
this deployment plan.

## Current Source, Mirror, and Live-Service State

| Area | Current state |
|---|---|
| Homelab latest pushed commit | `b7bd223 document model-dispatch mirror state` |
| Source repo | `strix:/srv/projects/model-dispatch` |
| Source repo status | Review-only; not deployed from this working tree yet |
| ThinkCentre mirror | `thinkcentre:/srv/git/model-dispatch.git` |
| Latest mirrored commit | `7cbb1d9 document thinkcentre mirror creation` |
| Live service path | `thinkcentre:/srv/model-dispatch` |
| Live service | `model-dispatch.service` |
| Live port | `4010` |
| Live OpenAI-compatible base URL | `http://192.168.50.225:4010/v1` |
| Current Open WebUI target | `http://192.168.50.225:4010/v1` |
| Deployment status | A deployment attempt stopped before file copy; no live files were changed |

The source repo was prepared from reviewed live files and remains separate from
the live runtime path. The live service path is still the runtime authority
until a later explicit deployment approval.

An attempted deployment from `strix:/srv/projects/model-dispatch` stopped while
creating the backup directory. The attempted backup path
`/srv/model-dispatch-backups/<timestamp>` failed with `mkdir: Permission
denied` because `/srv` is root-owned and `/srv/model-dispatch-backups` did not
exist. Validation after the failure showed the live health endpoint still
returned ok, the live `/srv/model-dispatch/app.py` timestamp remained
`2026-05-13 09:39`, and the live `/srv/model-dispatch/config.json` timestamp
remained `2026-05-11 11:33`. The deployment copy did not occur, and no live
files were changed during that failed attempt.

## Exact Non-Goals

- Do not deploy in this slice.
- Do not edit `thinkcentre:/srv/model-dispatch`.
- Do not copy files to `thinkcentre:/srv/model-dispatch`.
- Do not run `rsync`, `scp`, `cp`, `mv`, or `rm` against
  `thinkcentre:/srv/model-dispatch`.
- Do not restart or reload `model-dispatch.service`.
- Do not run `sudo`.
- Do not run Docker or systemd commands.
- Do not change Open WebUI configuration.
- Do not change OpenCode configuration.
- Do not change LiteLLM configuration.
- Do not change MCP configuration.
- Do not change reverse proxy configuration.
- Do not deploy or configure dashboards, monitoring, Prometheus, Grafana, Loki,
  Vector, observability, or service dashboards.
- Do not change OpenRouter-free discovery, pricing checks, timers, or generated
  artifacts.
- Do not expose the broad paid OpenRouter catalog.
- Do not add hidden automation, daemons, watchers, autonomous approval
  behavior, Codex automation, Claude/Codex wrappers, or paid-provider
  automation.
- Do not touch `tools/`.
- Do not commit from this planning slice.

## Pre-Deployment Validation Checklist

Complete this checklist before any future deployment command is approved:

- Confirm the source repo working tree is clean except for the reviewed release
  commit intended for deployment.
- Confirm the exact source commit to deploy and verify that it is pushed to
  `thinkcentre:/srv/git/model-dispatch.git`.
- Review `git diff` between the current live-equivalent source commit and the
  candidate deployment commit.
- Run local source checks from `strix:/srv/projects/model-dispatch`:
  - `python3 -m py_compile app.py`
  - `python3 -m json.tool config.json`
  - `python3 tests/check_config.py`
- Confirm `app.py` still preserves or intentionally updates these runtime
  assumptions:
  - live base path `/srv/model-dispatch`
  - `config.json` path `/srv/model-dispatch/config.json`
  - `dispatch.log` path `/srv/model-dispatch/dispatch.log`
  - OpenRouter-free allowlist path
    `/srv/openrouter-free/free-models.allowlist.json`
  - `OPENROUTER_API_KEY` environment-first loading behavior
  - `/srv/litellm/.env` fallback behavior, if still present
- Confirm `config.json` contains no API key, password, token credential,
  secret, bearer token, private key, database, or request log data.
- Confirm route aliases match the documented baseline unless a separate
  approved routing change exists.
- Confirm OpenRouter-free entries are still sourced from verified free-only
  metadata and fail closed if verification is missing or invalid.
- Confirm the rollback command block has been reviewed before deployment.
- Confirm a live backup/snapshot will be taken before copying any source files.
- Confirm Open WebUI validation has a human operator ready to test after the
  service is restarted in a later approved deployment slice.

## Files Eligible for Deployment

Only these reviewed source files are eligible for deployment to
`thinkcentre:/srv/model-dispatch` in a later approved slice:

- `app.py`
- `config.json`
- `.gitignore`
- `.cgcignore`

Documentation and tests remain source-repo artifacts by default. They may be
copied to the live path only if the operator explicitly approves deploying docs
alongside runtime files.

Candidate source-repo docs:

- `README.md`
- `SERVICE.md`
- `DEPLOYMENT.md`
- `ROUTING.md`
- `DECISIONS.md`
- `TESTING.md`
- `AGENT_STATUS.md`
- `tests/check_config.py`

## Files Explicitly Excluded From Deployment

Exclude these from any deployment copy:

- `.git/`
- `dispatch.log`
- `*.log`
- `*.bak`
- `.env`
- `*.env`
- files or directories matching `*secret*`, `*token*`, or `*key*`
- `*.db`
- `*.sqlite`
- `*.sqlite3`
- `__pycache__/`
- `.pytest_cache/`
- `.mypy_cache/`
- `.ruff_cache/`
- `.venv/`
- `venv/`
- `node_modules/`
- generated runtime files
- request logs
- local temporary files

Observed live files that must remain excluded:

- `/srv/model-dispatch/dispatch.log`
- `/srv/model-dispatch/app.py.20260511-113634.bak`
- `/srv/model-dispatch/app.py.20260511-114112.bak`
- `/srv/model-dispatch/app.py.20260513-093223.bak`
- `/srv/model-dispatch/app.py.20260513-093708.bak`
- `/srv/model-dispatch/config.json.20260511-113332.bak`
- `/srv/model-dispatch/config.json.20260511-113634.bak`

## Live Backup/Snapshot Plan Before Any Deployment

Before a future deployment, create a timestamped backup of only the live runtime
files required for rollback. Do not include logs, caches, secrets, or generated
runtime data in the source repo.

The backup should stay on ThinkCentre inside the existing live service path,
under `/srv/model-dispatch/backups/<timestamp>`. This keeps the backup under
the `enzo`-owned `/srv/model-dispatch` directory. The earlier proposed
`/srv/model-dispatch-backups/<timestamp>` path failed during a deployment
attempt because `/srv` is root-owned and the backup directory could not be
created without elevated permissions.

The exact timestamped path must be recorded in `AGENT_STATUS.md` before
deployment proceeds.

The backup must include:

- `/srv/model-dispatch/app.py`
- `/srv/model-dispatch/config.json`
- `/srv/model-dispatch/.gitignore`, if present
- `/srv/model-dispatch/.cgcignore`, if present

The backup must not include:

- `/srv/model-dispatch/dispatch.log`
- secrets or env files
- caches
- virtualenvs
- databases
- `.git/`

## Proposed Deployment Command Block — NOT RUN

The following is a proposed future operator command block. It was not run in
this slice.

```bash
# NOT RUN - future operator-approved deployment only
set -euo pipefail

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="/srv/model-dispatch/backups/${STAMP}"

ssh thinkcentre "mkdir -p '${BACKUP_DIR}'"
ssh thinkcentre "cp -a /srv/model-dispatch/app.py '${BACKUP_DIR}/app.py'"
ssh thinkcentre "cp -a /srv/model-dispatch/config.json '${BACKUP_DIR}/config.json'"
ssh thinkcentre "test ! -f /srv/model-dispatch/.gitignore || cp -a /srv/model-dispatch/.gitignore '${BACKUP_DIR}/.gitignore'"
ssh thinkcentre "test ! -f /srv/model-dispatch/.cgcignore || cp -a /srv/model-dispatch/.cgcignore '${BACKUP_DIR}/.cgcignore'"

scp /srv/projects/model-dispatch/app.py thinkcentre:/srv/model-dispatch/app.py
scp /srv/projects/model-dispatch/config.json thinkcentre:/srv/model-dispatch/config.json
scp /srv/projects/model-dispatch/.gitignore thinkcentre:/srv/model-dispatch/.gitignore
scp /srv/projects/model-dispatch/.cgcignore thinkcentre:/srv/model-dispatch/.cgcignore

ssh thinkcentre "python3 -m py_compile /srv/model-dispatch/app.py"
ssh thinkcentre "python3 -m json.tool /srv/model-dispatch/config.json >/tmp/model-dispatch-config-json-check.txt"

# Restart/reload requires explicit operator approval in the deployment slice.
# Example only:
# ssh thinkcentre "sudo systemctl restart model-dispatch.service"
```

## Proposed Rollback Command Block — NOT RUN

The following is a proposed future rollback block. It was not run in this
slice. Replace `<STAMP>` with the backup timestamp recorded during deployment.

```bash
# NOT RUN - future operator-approved rollback only
set -euo pipefail

BACKUP_DIR="/srv/model-dispatch/backups/<STAMP>"

ssh thinkcentre "test -f '${BACKUP_DIR}/app.py'"
ssh thinkcentre "test -f '${BACKUP_DIR}/config.json'"

ssh thinkcentre "cp -a '${BACKUP_DIR}/app.py' /srv/model-dispatch/app.py"
ssh thinkcentre "cp -a '${BACKUP_DIR}/config.json' /srv/model-dispatch/config.json"
ssh thinkcentre "test ! -f '${BACKUP_DIR}/.gitignore' || cp -a '${BACKUP_DIR}/.gitignore' /srv/model-dispatch/.gitignore"
ssh thinkcentre "test ! -f '${BACKUP_DIR}/.cgcignore' || cp -a '${BACKUP_DIR}/.cgcignore' /srv/model-dispatch/.cgcignore"

ssh thinkcentre "python3 -m py_compile /srv/model-dispatch/app.py"
ssh thinkcentre "python3 -m json.tool /srv/model-dispatch/config.json >/tmp/model-dispatch-config-json-check.txt"

# Restart/reload requires explicit operator approval in the rollback slice.
# Example only:
# ssh thinkcentre "sudo systemctl restart model-dispatch.service"
```

## Proposed Post-Deployment Validation Commands — NOT RUN

The following validation commands are proposed for a later approved deployment
slice. They were not run in this slice.

```bash
# NOT RUN - future post-deployment validation only
curl -fsS http://192.168.50.225:4010/v1/models

curl -fsS http://192.168.50.225:4010/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "auto-local",
    "messages": [{"role": "user", "content": "Reply with one short sentence."}],
    "stream": false
  }'

curl -fsS http://192.168.50.225:4010/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "auto-coding-local",
    "messages": [{"role": "user", "content": "Reply with ok."}],
    "stream": false
  }'

curl -fsS http://192.168.50.225:4010/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "auto-reasoning-local",
    "messages": [{"role": "user", "content": "Reply with ok."}],
    "stream": false
  }'

curl -fsS http://192.168.50.225:4010/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "auto-small-local",
    "messages": [{"role": "user", "content": "Reply with ok."}],
    "stream": false
  }'
```

Expected validation:

- `/v1/models` returns the documented local auto routes.
- `/v1/models` returns explicit local model entries.
- `/v1/models` returns only verified OpenRouter-free entries, if any
  OpenRouter-free entries are present.
- Chat completions return OpenAI-compatible JSON.
- Routing remains local-first.
- Upstream calls remain non-streaming where `model-dispatch` expects one JSON
  response.

## Open WebUI Validation Plan

After a future approved deployment and service restart, validate Open WebUI
manually from the browser at:

```text
http://192.168.50.225:3000
```

Manual checks:

- Confirm Open WebUI still lists `model-dispatch` models.
- Confirm these local route aliases are visible:
  - `auto-local`
  - `auto-coding-local`
  - `auto-reasoning-local`
  - `auto-small-local`
- Confirm explicit local model entries are still visible.
- Send a short prompt to `auto-local`.
- Send a short prompt to `auto-coding-local`.
- Send a planning prompt to `auto-reasoning-local`.
- Confirm the response works without switching Open WebUI back to LiteLLM.
- Confirm OpenRouter-free choices remain explicit/manual and are not used as
  hidden fallback.
- Do not change Open WebUI configuration during validation unless a separate
  operator-approved rollback instruction says to do so.

## OpenRouter-Free Fail-Closed Validation Plan

Validate free-only behavior before and after any future deployment:

- Confirm the broad paid OpenRouter catalog is not exposed through
  `/v1/models`.
- Confirm OpenRouter entries, if exposed, use the `openrouter-free/` prefix.
- Confirm exposed specific OpenRouter model IDs end in `:free`.
- Confirm `openrouter-free/openrouter/auto-free-router` appears only as an
  explicit selectable route.
- Confirm there is no automatic OpenRouter fallback from local routes.
- Confirm missing or invalid free-model metadata causes OpenRouter-free models
  to be omitted or rejected rather than exposing paid models.
- Confirm no OpenRouter API key value is printed, copied, or committed.

Proposed future commands for metadata checks must be reviewed in the deployment
slice and kept read-only. They are not run in this slice.

## Known Risks

- Open WebUI depends on the live ThinkCentre `model-dispatch` endpoint, so a
  bad deployment could interrupt the current advisor/planning surface.
- The source candidate preserves live runtime path assumptions and is not yet
  portable outside the ThinkCentre live path.
- `app.py` may read OpenRouter credentials from the process environment or
  `/srv/litellm/.env`; validation must not expose secret contents.
- Copying the wrong files could overwrite live backups, logs, or runtime state.
- Deploying docs/tests to the live service path could confuse the runtime
  boundary unless explicitly approved.
- Skipping the live backup would make rollback slower and riskier.
- Restart behavior is intentionally not exercised in this planning slice, so
  systemd-level problems would only be found in a later approved deployment
  slice.
- OpenRouter-free fail-closed behavior must be preserved; accidental exposure
  of paid models would violate standing constraints.
- Dashboards, monitoring, and observability are deferred. Bundling them into
  deployment would broaden scope and require a separate slice.

## Approval Requirements

A future deployment requires explicit operator approval before any command is
run that writes to `thinkcentre:/srv/model-dispatch`, restarts or reloads
`model-dispatch.service`, changes live config, or changes Open WebUI behavior.

The approval brief must include:

- exact source commit to deploy
- exact files to copy
- exact files excluded
- live backup destination
- exact deployment command block
- exact rollback command block
- validation commands
- Open WebUI manual validation steps
- OpenRouter-free fail-closed validation steps
- confirmation that dashboards, monitoring, and observability remain deferred

Recommended next operator instruction for a future deployment slice:

```text
Proceed with a deployment approval brief for model-dispatch. Do not run the
deployment yet. Confirm the exact source commit, backup path, eligible files,
excluded files, rollback block, and validation block before asking for final
operator approval.
```
