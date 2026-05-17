# model-dispatch Deployment Approval Brief — 2026-05-17

## Decision requested

Approve deploying the reviewed Strix `model-dispatch` source repo to the live ThinkCentre runtime path.

## Source

- Source repo: `strix:/srv/projects/model-dispatch`
- Source commit: `7cbb1d9 document thinkcentre mirror creation`
- Mirror: `thinkcentre:/srv/git/model-dispatch.git`
- Live path: `thinkcentre:/srv/model-dispatch`
- Live service: `model-dispatch.service`

## Files to deploy

- `app.py`
- `config.json`
- `.gitignore`
- `.cgcignore`

## Files excluded

- `.git/`
- `dispatch.log`
- `*.bak`
- `.env`
- `*.env`
- `*secret*`
- `*token*`
- `*key*`
- `*.db`
- `*.sqlite`
- `*.sqlite3`
- `__pycache__/`
- `.venv/`
- `venv/`
- caches
- generated runtime files
- request logs
- docs/tests unless separately approved

## Required backup before deployment

Back up the current live runtime files before copying anything:

- `/srv/model-dispatch/app.py`
- `/srv/model-dispatch/config.json`
- `/srv/model-dispatch/.gitignore`
- `/srv/model-dispatch/.cgcignore`, if present

Backup destination:

- `/srv/model-dispatch-backups/<timestamp>/`

## Deployment commands

To be run only after explicit approval:

- copy approved files from `strix:/srv/projects/model-dispatch` to `thinkcentre:/srv/model-dispatch`
- validate Python syntax
- validate JSON config
- restart `model-dispatch.service`

## Rollback

Restore the backed-up files from `/srv/model-dispatch-backups/<timestamp>/`, validate Python and JSON, then restart `model-dispatch.service`.

## Validation

After deployment:

- check `http://192.168.50.225:4010/health`
- check `http://192.168.50.225:4010/v1/models`
- send one short `auto-local` chat completion request
- confirm Open WebUI still works
- confirm OpenRouter-free remains explicit/manual and fail-closed

## Not included

This approval does not include:

- dashboard deployment
- monitoring/observability deployment
- Open WebUI config changes
- OpenCode migration
- Continue.dev migration
- LiteLLM removal
- model alias redesign
