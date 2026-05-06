# OpenRouter Free Artifact Plan

## Purpose

Preserve the useful part of the current LiteLLM setup: OpenRouter free-model discovery and zero-price filtering.

Move generated outputs away from LiteLLM-specific config and toward neutral artifacts that can be consumed by OpenCode and later Open WebUI.

## Source of truth

Current source logic:

- `/srv/litellm/render-config.py`

Useful behavior to preserve:

- Fetch OpenRouter model catalog.
- Keep only models whose IDs end in `:free`.
- Verify prompt and completion prices are both zero.
- Exclude anything that cannot be verified as free.
- Fail closed instead of exposing paid models.

## Target directory

Create a neutral directory on ThinkCentre:

- `/srv/openrouter-free/`

## Generated artifacts

- `free-models.raw.json`: raw OpenRouter model response for audit/debugging.
- `free-models.allowlist.json`: filtered verified-free model list.
- `opencode.generated.json`: OpenCode-compatible provider fragment.
- `openwebui.generated.env`: future helper artifact for Open WebUI direct/free-only config.

## OpenCode provider target

Target provider name:

- `homelab-openrouter-free`

Target base URL:

- `https://openrouter.ai/api/v1`

OpenCode currently accepts provider fields shaped like:

- `provider.<name>.npm`
- `provider.<name>.name`
- `provider.<name>.options.baseURL`
- `provider.<name>.options.apiKey`
- `provider.<name>.models`

Safety rules:

- Do not use OpenCode's broad built-in OpenRouter provider if it exposes paid models.
- Generate only explicit free model entries.
- Do not configure automatic fallback to OpenRouter.
- OpenRouter use must be manual.

## Local OpenCode provider target

OpenCode should eventually get a direct local provider:

- Provider name: `homelab-local`
- Base URL: `http://192.168.50.252:8083/v1`
- API key: `dummy`
- Default model: `homelab-local/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`

Optional direct providers can be added later for AMD backup and Strix models. Do not overpack the first migration.

## Fail-closed rules

The generator must:

- Exclude models without `:free` suffix.
- Exclude models with missing pricing fields.
- Exclude models with non-zero prompt price.
- Exclude models with non-zero completion price.
- Produce an empty allowlist if no models pass.
- Avoid producing a broad OpenRouter provider entry.
- Avoid automatic fallback behavior.

## Rollback

Do not delete LiteLLM.

Rollback remains:

- Restore OpenCode config to the current `homelab` provider using `http://192.168.50.225:4000/v1`.
- Restore Open WebUI `OPENAI_API_BASE_URLS` to `http://192.168.50.225:4000/v1`.
- Keep `/srv/litellm/` intact until direct OpenCode and Open WebUI paths are proven.

## Next implementation slice

Create `/srv/openrouter-free/` on ThinkCentre and write a new generator that produces neutral artifacts.

Do not change:

- OpenCode live config.
- Open WebUI live config.
- LiteLLM service.
- systemd timers.

First implementation should only generate and inspect artifacts.

## Implementation note: 2026-05-06

Initial neutral artifact generator created on ThinkCentre at:

- `/srv/openrouter-free/generate.py`

Generated artifacts were produced successfully:

- `/srv/openrouter-free/free-models.raw.json`
- `/srv/openrouter-free/free-models.allowlist.json`
- `/srv/openrouter-free/opencode.generated.json`
- `/srv/openrouter-free/openwebui.generated.env`

Result:

- 25 verified free OpenRouter models generated.
- No live LiteLLM, OpenCode, Open WebUI, Docker, or systemd configuration changed.

Open issue:

- OpenCode environment-variable interpolation for generated provider API keys still needs verification before live integration.

