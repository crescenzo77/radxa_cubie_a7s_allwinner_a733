# model-dispatch Additive Alias Deployment Record — 2026-05-18

## Result

Additive aliases were deployed to live ThinkCentre `model-dispatch`.

## Source

- Source repo: `strix:/srv/projects/model-dispatch`
- Source commit: `bf49923 add additive dispatch aliases`
- Mirror: `thinkcentre:/srv/git/model-dispatch.git`
- Live path: `thinkcentre:/srv/model-dispatch`
- Live service: `model-dispatch.service`
- Backup path: `/srv/model-dispatch/backups/20260518-093534`

## Files deployed

- `app.py`
- `config.json`

## Validation

- `/health` returned `{"status": "ok"}`
- `/v1/models` listed:
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
- `/v1/chat/completions` with `advisor` returned a valid OpenAI-compatible response.
- `/v1/chat/completions` with `local/amd-coder` returned a valid OpenAI-compatible response.
- Tested aliases selected `amd-coder-qwen3-coder-30b-32k`.

## What did not change

- No Open WebUI config change.
- No OpenCode config change.
- No Continue.dev config change.
- No LiteLLM removal.
- No dashboard deployment.
- No monitoring or observability deployment.
- No model endpoint host changes.

## Rollback

1. Restore `app.py` and `config.json` from `/srv/model-dispatch/backups/20260518-093534`.
2. Validate Python and JSON.
3. Restart `model-dispatch.service`.
4. Check `/health`.
