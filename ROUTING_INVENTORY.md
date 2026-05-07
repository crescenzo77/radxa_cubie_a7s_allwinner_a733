# Routing Inventory

Date: 2026-05-06

## Purpose

Capture the current live routing state for OpenCode, Open WebUI, LiteLLM, and OpenRouter configuration.

This is a read-only inventory. No service or config changes were made.

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

- `OPENAI_API_BASE_URLS: "http://192.168.50.225:4000/v1"`

Conclusion:

Open WebUI currently still routes through LiteLLM.

Older direct-endpoint examples exist in backup/commented files under `/srv/openwebui/`.

## ThinkCentre LiteLLM

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

Using `main-latest` is not ideal for a security-sensitive routing service. Since LiteLLM is no longer the default OpenCode path and Open WebUI routing will be reevaluated later, this is recorded as a transition risk rather than fixed immediately.

Current role:

- Still active for Open WebUI.
- Retained for OpenCode rollback.
- Not the default OpenCode path anymore.

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

The useful logic is the free-model discovery and zero-price filtering. The generated target should move from LiteLLM config to neutral/OpenCode-safe artifacts under `/srv/openrouter-free/`.

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

The AMD `8083` direct-local endpoint is now the default OpenCode path through `homelab-local`. The AMD `8084` direct-local endpoint is now the OpenCode backup `small_model` path through `homelab-local-backup`. Open WebUI still uses LiteLLM and can be reevaluated in a later slice.

## Current recommended next actions

Do not stop LiteLLM yet.
Do not claim Open WebUI has migrated until its live config changes.
Keep OpenRouter manual-only in OpenCode.
Keep the direct AMD RX 7900 XT backup provider documented as the OpenCode `small_model` path.
