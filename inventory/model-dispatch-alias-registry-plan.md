# model-dispatch Alias Registry Cleanup Plan

## Purpose

Plan stable `model-dispatch` aliases before changing OpenCode or Continue.dev.

This is a documentation-only planning slice. It does not edit
`/srv/model-dispatch`, restart services, change OpenCode, change Continue.dev,
deploy dashboards, or change live routing behavior.

## Current Documented Routing State

`model-dispatch` is live on ThinkCentre and is the active Open WebUI
OpenAI-compatible endpoint:

```text
Host: thinkcentre
Path: /srv/model-dispatch
Service: model-dispatch.service
Endpoint: http://192.168.50.225:4010/v1
```

Current client posture:

- Open WebUI uses `model-dispatch`.
- OpenCode still uses direct AMD routing.
- Continue.dev still uses the older documented LiteLLM-routed route.
- LiteLLM remains rollback/history.
- Dashboards, monitoring, and observability remain deferred.

## Current Exposed model-dispatch IDs

Current documented local auto routes:

- `auto-local`
- `auto-coding-local`
- `auto-reasoning-local`
- `auto-small-local`

Current documented explicit local models:

- `strix-reasoning-qwen3.6-65k`
- `strix-coder-qwen3-coder-next-65k`
- `amd-coder-qwen3-coder-30b-32k`
- `amd-backup-gemma4-26b-8k`

Current documented OpenRouter-free forms:

- `openrouter-free/openrouter/auto-free-router`
- `openrouter-free/<verified-model>:free`

Current direct OpenCode IDs outside `model-dispatch`:

- `homelab-local/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
- `homelab-local-backup/google_gemma-4-26B-A4B-it-Q4_K_M.gguf`

Current Continue.dev route:

- Continue.dev uses LiteLLM-routed verbose model IDs from
  `http://192.168.50.225:4000/v1`.

## Proposed Stable Alias Classes

Stable aliases should be short, role-oriented, and client-safe. They should hide
implementation details such as host, quantization filename, and current upstream
endpoint where possible.

Proposed primary role aliases:

| Alias | Intended role | Initial target behavior |
|---|---|---|
| `advisor` | General planning and workflow advisor | Local-first route, currently equivalent to `auto-local` |
| `reasoning` | Long planning and decision-heavy prompts | Prefer Strix reasoning capacity |
| `coding` | Normal coding chat and agent work | Prefer local coding capacity |
| `small` | Short lightweight prompts | Prefer small or cheapest local-capable route that fits |
| `review` | Code and diff review | Prefer reasoning/coding-capable local route with enough context |
| `long-code` | Large code context and long diffs | Prefer highest-context local coding/reasoning route |

Proposed explicit implementation aliases:

| Alias | Intended target |
|---|---|
| `local/strix-reasoning` | `strix-reasoning-qwen3.6-65k` |
| `local/strix-coder` | `strix-coder-qwen3-coder-next-65k` |
| `local/amd-coder` | `amd-coder-qwen3-coder-30b-32k` |
| `local/amd-small` | `amd-backup-gemma4-26b-8k` |

Proposed free-cloud alias:

| Alias | Intended target |
|---|---|
| `free-cloud` | `openrouter-free/openrouter/auto-free-router` |

`free-cloud` must remain explicit/manual. It must not become an automatic hidden
fallback for local aliases.

## Display Name Requirements

Stable alias IDs are for client stability. They may be short, role-based, and
insulated from implementation details so Open WebUI, OpenCode, Continue.dev,
and scripts do not have to change every time the backing model changes.

Open WebUI display names are for human operator clarity. Where known, display
names should include:

- model family
- parameter count
- quantization
- context window
- host or role

Examples:

| Alias ID | Open WebUI display name |
|---|---|
| `local/amd-coder` | `AMD Qwen3-Coder 30B Q4_K_M 32k` |
| `local/amd-small` | `AMD Gemma 4 26B Q4_K_M 8k` |
| `local/strix-coder` | `Strix Qwen3-Coder-Next UD-Q4_K_XL 65k` |
| `local/strix-reasoning` | `Strix Qwen3.6 35B-A3B UD-Q4_K_XL 65k` |

The alias ID should stay stable for clients; the display name should stay
descriptive enough for an operator to infer the model family, size,
quantization, context window, and host or role when choosing a model in Open
WebUI.

## Compatibility Aliases to Preserve

Do not remove existing names during the first alias deployment.

Preserve current `model-dispatch` aliases:

- `auto-local`
- `auto-coding-local`
- `auto-reasoning-local`
- `auto-small-local`
- `strix-reasoning-qwen3.6-65k`
- `strix-coder-qwen3-coder-next-65k`
- `amd-coder-qwen3-coder-30b-32k`
- `amd-backup-gemma4-26b-8k`
- `openrouter-free/openrouter/auto-free-router`
- `openrouter-free/<verified-model>:free`

Preserve documented client rollback paths:

- OpenCode direct AMD provider:
  `homelab-local/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`.
- OpenCode direct AMD small model:
  `homelab-local-backup/google_gemma-4-26B-A4B-it-Q4_K_M.gguf`.
- Continue.dev LiteLLM-routed verbose IDs until Continue.dev migration is
  separately validated.
- LiteLLM rollback endpoint at `http://192.168.50.225:4000/v1`.

## Proposed Alias Mapping

Initial mapping for future review:

| Stable alias | Compatibility target | Notes |
|---|---|---|
| `advisor` | `auto-local` | Default Open WebUI planning choice |
| `reasoning` | `auto-reasoning-local` | Planning, architecture review, decision-heavy prompts |
| `coding` | `auto-coding-local` | OpenCode target after isolated validation |
| `small` | `auto-small-local` | Lightweight prompts only |
| `review` | `auto-reasoning-local` | Code review and diff explanation need reasoning headroom |
| `long-code` | `auto-coding-local` or `auto-reasoning-local` | Must be validated against large context before deployment |
| `free-cloud` | `openrouter-free/openrouter/auto-free-router` | Manual-only free OpenRouter route |
| `local/strix-reasoning` | `strix-reasoning-qwen3.6-65k` | Explicit Strix reasoning model |
| `local/strix-coder` | `strix-coder-qwen3-coder-next-65k` | Explicit Strix coder testbed |
| `local/amd-coder` | `amd-coder-qwen3-coder-30b-32k` | Explicit AMD coder model |
| `local/amd-small` | `amd-backup-gemma4-26b-8k` | Explicit AMD backup/small model |

`long-code` needs special validation before deployment. It should not point to a
small-context model and should not silently fall through to OpenRouter.

## What Should Not Change Yet

Do not change in this slice:

- `/srv/model-dispatch`.
- `model-dispatch.service`.
- Open WebUI live config.
- OpenCode config.
- Continue.dev config.
- LiteLLM config.
- Docker or systemd state.
- Reverse proxy, SearXNG, MCP, dashboard, monitoring, or observability config.
- OpenRouter-free allowlist behavior.
- Existing model IDs.
- Any live endpoint or route behavior.

Do not add:

- Paid-provider fallback.
- Hidden automatic cloud fallback.
- Codex or Claude automation.
- Daemons, watchers, approval systems, or background supervision.

## Validation Required Before Alias Deployment

Before any future deployment, validate from reviewed `model-dispatch` source and
an explicit operator-approved command block:

- `/v1/models` still lists all compatibility aliases.
- `/v1/models` lists each new stable alias.
- `/v1/chat/completions` works for:
  - `advisor`
  - `reasoning`
  - `coding`
  - `small`
  - `review`
  - `long-code`
  - one explicit Strix alias
  - one explicit AMD alias
- Existing Open WebUI choices still work after alias addition.
- OpenCode candidate config works in isolation before live OpenCode is changed.
- Continue.dev candidate config works in isolation before live Continue.dev is
  changed.
- Direct AMD routing remains available as OpenCode rollback.
- LiteLLM remains available as Continue.dev and historical rollback until a
  later slice changes that posture.
- OpenRouter-free aliases remain explicit, verified free-only, and fail-closed.
- Upstream calls still force non-streaming JSON where `model-dispatch` requires
  it.
- No paid OpenRouter catalog entries are exposed.

## Rollback Expectations

Future alias deployment should be additive first. Rollback should be simple:

- Keep all compatibility aliases during the first deployment.
- If stable aliases fail, remove or disable only the new alias entries and keep
  existing IDs untouched.
- Keep Open WebUI on currently working IDs until alias behavior is validated.
- Keep OpenCode direct AMD routing unchanged until a separate migration slice is
  approved and validated.
- Keep Continue.dev on its current documented route until a separate migration
  slice is approved and validated.
- Keep the previous `/srv/model-dispatch` deployment backup path documented
  before any live deployment.
- Restart or rollback services only after explicit operator approval.

## Recommended Next Action

Review this alias plan. If accepted, the next safe slice is a deployment
planning slice that prepares an additive `model-dispatch` alias change from the
reviewed source repo, including exact validation and rollback command blocks.

Do not change OpenCode or Continue.dev until the alias deployment has been
validated separately.
