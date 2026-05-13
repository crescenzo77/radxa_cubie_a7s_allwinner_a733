# Routing Inventory

Date: 2026-05-11

## Purpose

Capture the current live routing state for OpenCode, Open WebUI, model-dispatch, LiteLLM, and OpenRouter configuration.

This is a read-only inventory. No service or config changes were made.

## Routing health check

Run from the homelab repo on `strix`:

```bash
scripts/routing-health
```

This checks the model-list endpoints for LiteLLM rollback, AMD 3090 local coder, AMD 7900 XT backup, Strix reasoning, and Strix coder testbed. It is read-only and does not change routing state.

## AMD OpenCode

OpenCode is installed on AMD.

Observed:

- Version: `1.14.39`
- Config path: `/home/enzo/.config/opencode/opencode.json`
- Default provider: `homelab-local`
- Default provider name: `Homelab Local`
- Default base URL: `http://192.168.50.252:8083/v1`
- Default model: `homelab-local/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
- Backup provider: `homelab-local-backup`
- Backup provider name: `Homelab Local Backup`
- Backup base URL: `http://192.168.50.252:8084/v1`
- Backup endpoint model: `google_gemma-4-26B-A4B-it-Q4_K_M.gguf`
- Small model: `homelab-local-backup/google_gemma-4-26B-A4B-it-Q4_K_M.gguf`
- Manual provider: `homelab-openrouter-free`
- Manual provider model count: 25 verified free OpenRouter models
- OpenRouter default usage: disabled/manual-only
- Automatic OpenRouter fallback: none
- LiteLLM rollback provider: `homelab`
- LiteLLM rollback base URL: `http://192.168.50.225:4000/v1`

Conclusion:

AMD OpenCode no longer defaults through LiteLLM. The default path is direct AMD local-coder through `homelab-local`. The `small_model` path is the direct AMD RX 7900 XT backup provider through `homelab-local-backup`. OpenRouter is available only through `homelab-openrouter-free` when selected manually, with no automatic OpenRouter fallback.

## ThinkCentre Open WebUI

Open WebUI compose path:

- `/srv/openwebui/docker-compose.yml`

Current live setting:

- `OPENAI_API_BASE_URLS: "http://192.168.50.225:4010/v1"`

Conclusion:

Open WebUI currently routes through `model-dispatch`, not LiteLLM.

Older direct-endpoint examples exist in backup/commented files under `/srv/openwebui/`.

### Validated web-search state

- `auto-local` web search works.
- `openrouter-free/openrouter/auto-free-router` web search works.
- SearXNG JSON search works from inside the Open WebUI container.
- Open WebUI logs show successful `save_docs_to_vector_db`, embeddings generation, collection insert, and `query_doc:result`.
- Stable posture: `BYPASS_WEB_SEARCH_WEB_LOADER=true`, `TASK_MODEL_EXTERNAL=amd-coder-qwen3-coder-30b-32k`, and `TASK_MODEL=amd-coder-qwen3-coder-30b-32k`.
- Working path is snippet-based SearXNG retrieval, not full-page fetch.

## ThinkCentre model-dispatch

Service details:

- Host: `thinkcentre`
- Path: `/srv/model-dispatch`
- Service: `model-dispatch.service`
- Port: `4010`
- Endpoint: `http://192.168.50.225:4010/v1`

Open WebUI visible model IDs:

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

Validated behavior:

- `auto-local` selected AMD Qwen 32k for a normal prompt.
- `auto-small-local` skipped AMD Gemma 8k when estimated total tokens were about 18k and routed to AMD Qwen 32k.
- 25 verified OpenRouter free model entries were exposed.
- `openrouter-free/openrouter/auto-free-router` appears before specific free models.

Current role:

- Active Open WebUI OpenAI-compatible endpoint.
- Local-first model dispatch.
- Explicit local model selection.
- Explicit/manual OpenRouter-free exposure.
- Fail-closed free-model filtering through the verified allowlist.

## ThinkCentre LiteLLM Rollback/History

LiteLLM files:

- `/srv/litellm/config.yaml`
- `/srv/litellm/docker-compose.yml`
- `/srv/litellm/.env`
- `/srv/litellm/generated/litellm.config.yaml`
- `/srv/litellm/render-config.py`

Container:

- Name: `litellm`
- Image: `ghcr.io/berriai/litellm:main-latest`
- Port mapping: `0.0.0.0:4000->4000/tcp`
- Status at inventory time: running

Security note:

Using `main-latest` is not ideal for a security-sensitive routing service. Since LiteLLM is no longer the default OpenCode path and no longer the active Open WebUI path, this is recorded as a rollback/history risk rather than fixed immediately.

Current role:

- Retained for OpenCode rollback.
- Not the default OpenCode path anymore.
- Retained for Open WebUI rollback/history unless explicitly reactivated.

## OpenRouter free-model refresh

Timer:

- `litellm-free-models-refresh.timer`
- Enabled and active
- Runs every six hours with jitter

Service:

- `litellm-free-models-refresh.service`
- Last observed run succeeded
- Last observed output: generated LiteLLM config with 25 specific OpenRouter free models

Refresh script:

- `/usr/local/sbin/litellm-refresh-free-models`

Renderer:

- `/srv/litellm/render-config.py`

Current behavior:

1. Fetch OpenRouter model catalog.
2. Keep only model IDs ending in `:free`.
3. Verify prompt and completion prices are zero.
4. Generate `/srv/litellm/generated/litellm.config.yaml`.
5. Replace `/srv/litellm/config.yaml`.
6. Recreate the LiteLLM container.

Conclusion:

The useful logic is the free-model discovery and zero-price filtering. Neutral artifacts under `/srv/openrouter-free/` now feed direct OpenCode provider generation and model-dispatch Open WebUI exposure.

## Direct local endpoints

All direct local model endpoints responded successfully.

### Strix

- `http://192.168.50.11:8081`
  - Health: ok
  - Model: `Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf`

- `http://192.168.50.11:8082`
  - Health: ok
  - Model: `Qwen3-Coder-Next-UD-Q4_K_XL.gguf`

### AMD

- `http://192.168.50.252:8083`
  - Health: ok
  - Model: `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`

- `http://192.168.50.252:8084`
  - Health: ok
  - Model: `google_gemma-4-26B-A4B-it-Q4_K_M.gguf`

Conclusion:

The AMD `8083` direct-local endpoint is now the default OpenCode path through `homelab-local`. The AMD `8084` direct-local endpoint is now the OpenCode backup `small_model` path through `homelab-local-backup`. Open WebUI uses model-dispatch at `http://192.168.50.225:4010/v1`.

## Current recommended next actions

Do not stop LiteLLM yet.
Keep LiteLLM documented as rollback/history only unless explicitly reactivated.
Keep OpenRouter manual-only in OpenCode.
Keep OpenRouter free choices explicit/manual in Open WebUI.
Keep the direct AMD RX 7900 XT backup provider documented as the OpenCode `small_model` path.
Improve model-dispatch token estimation in a later slice.

## 2026-05-13 — Force non-streaming upstream calls in model-dispatch

Decision:
`model-dispatch` now forces `stream: false` when forwarding chat completion requests to local and OpenRouter-free upstreams.

Rationale:
Open WebUI sends streaming chat requests. The local OpenAI-compatible backends return `text/event-stream` chunks for streaming responses. `model-dispatch` is not a streaming proxy and expects one JSON response object, so it failed with `no capable model available` after trying to parse SSE output as JSON.

Consequence:
Open WebUI can continue using streaming behavior at its own API boundary, while `model-dispatch` normalizes upstream calls to non-streaming JSON. Local model routing through `auto-local` is working again.
