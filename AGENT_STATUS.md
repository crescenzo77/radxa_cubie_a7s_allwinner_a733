# Agent Status

## Current status

Slice 12 has a non-live OpenCode direct-provider migration draft based on fresh manual read-only inspection.

## Current slice

Slice 12: draft OpenCode direct-provider migration.

## What changed

Updated repo state docs only:

- `AGENT_STATUS.md`

No live config was edited.

## What did not change

No live service or client config was changed.

Not changed:

- `/home/enzo/.config/opencode/opencode.json`
- OpenCode provider settings
- Open WebUI config
- LiteLLM config or service
- Docker Compose services
- systemd services or timers
- OpenRouter model access
- remote host files

No OpenRouter model calls were made.

No service restarts were run.

## Checks run

Manual read-only inspection from `strix`:

- `ssh amd` inspected OpenCode version and redacted config.
- `ssh thinkcentre` inspected `/srv/openrouter-free/opencode.generated.json` with API key redacted.

## Results of checks

AMD OpenCode:

- Hostname: `AMD`
- OpenCode version: `1.14.39`
- Current enabled provider: `homelab`
- Current provider path: Homelab LiteLLM at `http://192.168.50.225:4000/v1`
- Current default model: `homelab/local-coder | AMD RTX 3090 | Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
- Current small model: `homelab/local-coder-backup | AMD RX 7900 XT | Gemma 4 26B A4B Q4_K_M.gguf`

Generated OpenRouter-free provider:

- Hostname: `thinkcentre`
- Path: `/srv/openrouter-free/opencode.generated.json`
- Provider name: `homelab-openrouter-free`
- Base URL: `https://openrouter.ai/api/v1`
- API key syntax: `{env:OPENROUTER_API_KEY}`
- Verified free model entries: 25

## Proposed non-live migration shape

Draft only. Do not apply without a later approval brief and live-config backup.

The first live migration should be intentionally narrow:

- Add direct `homelab-local` provider for AMD 3090 local-coder.
- Add generated `homelab-openrouter-free` provider for manual OpenRouter free-only use.
- Keep OpenRouter manual-only.
- Do not add automatic OpenRouter fallback.
- Do not remove LiteLLM from Open WebUI.
- Do not delete LiteLLM.
- Do not set `small_model` to the 3090 model.

Important correction:

- The draft must not set `small_model` to the same AMD 3090 model as `model`.
- Until a direct backup provider is added, either keep the existing LiteLLM-backed `small_model` during transition or omit `small_model` in the direct-provider draft.
- A later slice can add a direct AMD 7900 XT backup provider if desired.

## Draft provider direction

Target direct local provider:

```json
{
  "homelab-local": {
    "npm": "@ai-sdk/openai-compatible",
    "name": "Homelab Local",
    "options": {
      "baseURL": "http://192.168.50.252:8083/v1",
      "apiKey": "dummy"
    },
    "models": {
      "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf": {
        "name": "local-coder | AMD RTX 3090 | Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf"
      }
    }
  }
}
```

Target generated OpenRouter-free provider should be copied from:

```text
/srv/openrouter-free/opencode.generated.json
```

Current generated model count:

```text
25
```

## Rollback path

Before any future live migration:

1. Back up `/home/enzo/.config/opencode/opencode.json` on AMD without printing secrets.
2. Apply the approved migration only to `/home/enzo/.config/opencode/opencode.json`.
3. Validate OpenCode against AMD local endpoint only.
4. If validation fails, restore the previous OpenCode config that uses provider `homelab` and LiteLLM base URL `http://192.168.50.225:4000/v1`.

Rollback target:

- provider: `homelab`
- base URL: `http://192.168.50.225:4000/v1`
- default model: `homelab/local-coder | AMD RTX 3090 | Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
- small model: `homelab/local-coder-backup | AMD RX 7900 XT | Gemma 4 26B A4B Q4_K_M.gguf`

Do not stop or delete LiteLLM during rollback preparation.

## Known risks or blockers

- `OPENROUTER_API_KEY` must be present in the OpenCode runtime environment before manual OpenRouter-free use; otherwise OpenCode substitutes an empty string.
- `enabled_providers` should be checked against the installed OpenCode version before applying live.
- The first live test should validate only the direct AMD local provider before any OpenRouter provider is used.
- Direct backup provider for AMD 7900 XT is not included in the first narrow migration draft.

## User approval needed

Approval is required before:

- editing `/home/enzo/.config/opencode/opencode.json`
- changing OpenCode provider settings
- altering LiteLLM or Open WebUI
- calling any OpenRouter model
- restarting services
- mutating any remote host

## Recommended next action

Prepare a live-change approval brief for a narrow AMD OpenCode config migration:

1. Backup current AMD OpenCode config.
2. Write a candidate config file beside the live config.
3. Validate candidate JSON.
4. Switch OpenCode to direct AMD local provider only.
5. Test local-only OpenCode.
6. Add generated OpenRouter-free provider only after local direct provider is proven.
