# Current Slice

## Slice 18: Synchronize docs with AMD 7900 XT backup provider

Update homelab documentation so the repo reflects the current live OpenCode backup-provider state.

## Purpose

AMD OpenCode now has a direct local backup provider in addition to the direct 3090 primary provider and manual OpenRouter-free provider.

Current live OpenCode state:

- primary provider: `homelab-local`
- primary endpoint: `http://192.168.50.252:8083/v1`
- primary model: `homelab-local/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
- backup provider: `homelab-local-backup`
- backup endpoint: `http://192.168.50.252:8084/v1`
- small model: `homelab-local-backup/google_gemma-4-26B-A4B-it-Q4_K_M.gguf`
- manual provider: `homelab-openrouter-free`
- OpenRouter-free model count: 25
- LiteLLM unchanged
- Open WebUI unchanged

## Scope

Documentation-only updates:

- `HOMELAB_LAYOUT.md`
- `WORKFLOW.md`
- `ROADMAP.md`
- `ROUTING_INVENTORY.md`
- `AGENT_STATUS.md`

## Constraints

- No live config changes.
- No service restarts.
- No OpenRouter calls.
- No OpenCode config edits.
- No LiteLLM changes.
- No Open WebUI changes.
- No remote mutation.

## Required documentation changes

### HOMELAB_LAYOUT.md

Update model role assignments and OpenCode section to show:

- `homelab-local` as primary direct provider.
- `homelab-local-backup` as direct backup provider.
- `homelab-openrouter-free` as manual-only provider.
- `small_model` now points to AMD 7900 XT backup.
- LiteLLM remains rollback/Open WebUI only.

### WORKFLOW.md

Update coding workflow notes:

- OpenCode default remains AMD 3090 direct local.
- OpenCode `small_model` is AMD 7900 XT direct backup.
- OpenRouter-free remains manual-only.
- LiteLLM remains outside default OpenCode execution path.

### ROADMAP.md

Mark completed:

- optional direct AMD backup provider for RX 7900 XT endpoint.

Keep pending:

- Open WebUI migration away from LiteLLM.
- any later LiteLLM removal/stability review.

### ROUTING_INVENTORY.md

Update AMD OpenCode section:

- enabled providers include:
  - `homelab-local`
  - `homelab-local-backup`
  - `homelab-openrouter-free`
- `small_model` is `homelab-local-backup/google_gemma-4-26B-A4B-it-Q4_K_M.gguf`
- backup endpoint is `http://192.168.50.252:8084/v1`
- backup endpoint exposes `google_gemma-4-26B-A4B-it-Q4_K_M.gguf`

## Acceptance Criteria

- Repo docs match live OpenCode provider state.
- AMD 7900 XT backup provider is documented.
- OpenRouter remains documented as manual-only.
- LiteLLM remains documented as Open WebUI/rollback only.
- No live services or configs are changed.
- Git diff is shown before commit.
