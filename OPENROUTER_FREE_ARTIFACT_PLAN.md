# OpenRouter Free Artifact Plan

## Purpose

Preserve the useful part of the current LiteLLM setup: OpenRouter free-model discovery and zero-price filtering.

Move generated outputs away from LiteLLM-specific config and toward neutral artifacts consumed by OpenCode and model-dispatch for Open WebUI.

## Source of truth

Current source logic:

- `/srv/litellm/render-config.py`

Useful behavior to preserve:

- Fetch OpenRouter model catalog.
- Keep only models whose IDs end in `:free`.
- Verify prompt and completion prices are both zero.
- Exclude anything that cannot be verified as free.
- Fail closed instead of exposing paid models.

## Artifact directory

Neutral directory on ThinkCentre:

- `/srv/openrouter-free/`

## Generated artifacts

- `free-models.raw.json`: raw OpenRouter model response for audit/debugging.
- `free-models.allowlist.json`: filtered verified-free model list.
- `opencode.generated.json`: OpenCode-compatible provider fragment.
- `openwebui.generated.env`: helper artifact for Open WebUI direct/free-only config.

## OpenCode provider status

Live manual provider name:

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

## Local OpenCode provider status

OpenCode now uses a direct local provider by default:

- Provider name: `homelab-local`
- Base URL: `http://192.168.50.252:8083/v1`
- API key: `dummy`
- Default model: `homelab-local/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`

Optional direct providers can be added later for AMD backup and Strix models. Do not overpack the first migration.

## Open WebUI model-dispatch status

Open WebUI now points to model-dispatch:

- Endpoint: `http://192.168.50.225:4010/v1`
- Service: `model-dispatch.service`
- Path: `/srv/model-dispatch`
- Host: `thinkcentre`

model-dispatch consumes `/srv/openrouter-free/free-models.allowlist.json` for Open WebUI OpenRouter-free exposure.

Visible OpenRouter-free entries include:

- `openrouter-free/openrouter/auto-free-router`
- `openrouter-free/<verified-model>:free`

Safety rules:

- Keep OpenRouter choices explicit/manual in Open WebUI.
- Expose only verified free models from `free-models.allowlist.json`.
- Keep the paid OpenRouter catalog hidden.
- Fail closed if the allowlist is missing, stale, malformed, or contains unverifiable pricing.

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

- Restore OpenCode config to the rollback `homelab` provider using `http://192.168.50.225:4000/v1`.
- Restore Open WebUI `OPENAI_API_BASE_URLS` to `http://192.168.50.225:4000/v1`.
- Keep `/srv/litellm/` intact because Open WebUI and OpenCode rollback may depend on it if LiteLLM is explicitly reactivated.

## Implementation status

Direct local OpenCode and manual OpenRouter-free provider integration are live on AMD OpenCode. Open WebUI now consumes the free-model allowlist through model-dispatch. OpenRouter remains manual-only, and there is no automatic cloud fallback.

Do not change as part of this documentation slice:

- OpenCode live config.
- Open WebUI live config.
- model-dispatch code or service.
- LiteLLM service.
- systemd timers.

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
- Generated provider is now live on AMD OpenCode as `homelab-openrouter-free`.
- Direct local provider is now live on AMD OpenCode as `homelab-local`.
- OpenRouter remains manual-only.
- No automatic cloud fallback exists.
- Open WebUI now routes through model-dispatch, which consumes `free-models.allowlist.json` and exposes `openrouter-free/openrouter/auto-free-router` plus verified free model entries.

Resolved issue:

- OpenCode provider integration was verified during the later live migration slice.
