# Current Slice

## Slice 19: Document Open WebUI model-dispatch migration

Update homelab documentation so the repo reflects the current live Open WebUI routing state.

## Purpose

Open WebUI no longer uses LiteLLM as its active model endpoint.

Current live path:

- Open WebUI endpoint: `http://192.168.50.225:3000`
- Open WebUI model API target: `http://192.168.50.225:4010/v1`
- ThinkCentre dispatcher path: `/srv/model-dispatch`
- ThinkCentre dispatcher service: `model-dispatch.service`
- Dispatcher port: `4010`

The dispatcher provides:

- OpenAI-compatible `/v1/models`
- OpenAI-compatible `/v1/chat/completions`
- context-window-aware local routing
- local-first dispatch
- explicit local model selection
- verified OpenRouter free-only model exposure
- OpenRouter free auto-router exposure
- fail-closed free-model filtering

## Current visible Open WebUI model classes

Auto local routes:

- `auto-local`
- `auto-coding-local`
- `auto-reasoning-local`
- `auto-small-local`

Explicit local models:

- `strix-reasoning-qwen3.6-65k`
- `strix-coder-qwen3-coder-next-65k`
- `amd-coder-qwen3-coder-30b-32k`
- `amd-backup-gemma4-26b-8k`

OpenRouter free choices:

- `openrouter-free/openrouter/auto-free-router`
- `openrouter-free/<verified-model>:free`

## Scope

Documentation-only updates:

- `HOMELAB_LAYOUT.md`
- `WORKFLOW.md`
- `ROADMAP.md`
- `ROUTING_INVENTORY.md`
- `OPENROUTER_FREE_ARTIFACT_PLAN.md`
- `DECISIONS.md`
- `CURRENT_SLICE.md`

## Constraints

- No live service changes.
- No Open WebUI config changes.
- No model-dispatch code changes.
- No LiteLLM changes.
- No OpenRouter calls.
- No Framework-local canonical state.

## Acceptance Criteria

- Docs no longer claim Open WebUI actively routes through LiteLLM.
- Docs identify LiteLLM as rollback/history, not active Open WebUI path.
- Docs list `model-dispatch` path, service, port, and endpoint.
- Docs list current dispatcher model IDs.
- Docs include `openrouter-free/openrouter/auto-free-router`.
- Docs preserve OpenRouter paid-catalog exclusion.
- Git diff is reviewed before commit.
