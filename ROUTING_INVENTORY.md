# Routing Inventory

Date: 2026-05-06

## Purpose

Capture the current live routing state before changing OpenCode, Open WebUI, LiteLLM, or OpenRouter configuration.

This is a read-only inventory. No service or config changes were made.

## AMD OpenCode

OpenCode is installed on AMD.

Observed:

- Version: `1.14.39`
- Config path: `/home/enzo/.config/opencode/opencode.json`
- Current provider: `homelab`
- Current provider name: `Homelab LiteLLM`
- Current base URL: `http://192.168.50.225:4000/v1`
- Current default model: `homelab/local-coder | AMD RTX 3090 | Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
- Current small model: `homelab/local-coder-backup | AMD RX 7900 XT | Gemma 4 26B A4B Q4_K_M.gguf`

Conclusion:

OpenCode currently still routes through LiteLLM.

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

Using `main-latest` is not ideal for a security-sensitive routing service. Since the target is to remove LiteLLM from the active path, this is recorded as a transition risk rather than fixed immediately.

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

The direct-local endpoint target is viable. OpenCode and Open WebUI can be migrated away from LiteLLM after config generation and rollback steps are documented.

## Next recommended slice

Create `/srv/openrouter-free/` on ThinkCentre and migrate the free-model discovery output to neutral artifacts:

- `free-models.raw.json`
- `free-models.allowlist.json`
- `opencode.generated.json`
- `openwebui.generated.env`

Do not stop LiteLLM yet.
Do not change OpenCode or Open WebUI config yet.
