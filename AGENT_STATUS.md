# Agent Status

## Current status

Slice 18 documentation updates are complete and ready for review.

## Current slice

Slice 18: synchronize docs with AMD 7900 XT backup provider.

## What changed

Documentation now reflects that live AMD OpenCode includes:

- `homelab-local` for AMD 3090 primary.
- `homelab-local-backup` for AMD 7900 XT backup.
- `homelab-openrouter-free` for manual free-only OpenRouter use.
- `small_model` set to `homelab-local-backup/google_gemma-4-26B-A4B-it-Q4_K_M.gguf`.
- 25 verified free OpenRouter models exposed through the manual provider.

The roadmap now treats the optional direct AMD RX 7900 XT backup provider as completed, while keeping Open WebUI migration and later LiteLLM removal/stability review pending.

## Current live state

AMD OpenCode:

- primary provider: `homelab-local`
- primary endpoint: `http://192.168.50.252:8083/v1`
- primary model: `homelab-local/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
- backup provider: `homelab-local-backup`
- backup endpoint: `http://192.168.50.252:8084/v1`
- small model: `homelab-local-backup/google_gemma-4-26B-A4B-it-Q4_K_M.gguf`
- manual provider: `homelab-openrouter-free`
- OpenRouter-free model count: 25

Unchanged:

- LiteLLM remains available for Open WebUI and OpenCode rollback.
- Open WebUI still uses LiteLLM.
- OpenRouter remains manual-only.
- No automatic OpenRouter fallback exists.

## Files that require updates

- `HOMELAB_LAYOUT.md`
- `WORKFLOW.md`
- `ROADMAP.md`
- `ROUTING_INVENTORY.md`
- `AGENT_STATUS.md`

## What did not change

No live services or live configs were changed.

Unchanged:

- LiteLLM remains available for Open WebUI and OpenCode rollback.
- Open WebUI still uses LiteLLM.
- OpenRouter remains manual-only.
- No automatic OpenRouter fallback exists.

## Files changed

- `HOMELAB_LAYOUT.md`
- `WORKFLOW.md`
- `ROADMAP.md`
- `ROUTING_INVENTORY.md`
- `AGENT_STATUS.md`

## Checks run

- Read required context docs: `AGENTS.md`, `CODEX_CONTEXT.md`, `CURRENT_SLICE.md`, `AGENT_STATUS.md`, `PROJECT_PLAN.md`, `DECISIONS.md`, `HOMELAB_LAYOUT.md`, `WORKFLOW.md`, `ROADMAP.md`, `ROUTING_INVENTORY.md`.
- `rg -n "backup|small_model|homelab-local|OpenRouter|LiteLLM|Future Routing|7900|8084|recommended next" HOMELAB_LAYOUT.md WORKFLOW.md ROADMAP.md ROUTING_INVENTORY.md AGENT_STATUS.md`
- `rg -n "homelab-local-backup|small_model|8084|OpenRouter remains manual-only|automatic OpenRouter fallback|LiteLLM remains|RX 7900 XT|Future Routing Work" HOMELAB_LAYOUT.md WORKFLOW.md ROADMAP.md ROUTING_INVENTORY.md AGENT_STATUS.md`
- `git diff --stat`
- `git status --short`

## Results of checks

- Required context files were present and readable.
- Search identified the documentation sections updated for Slice 18.
- Post-edit search confirmed the backup provider, `small_model`, 8084 endpoint, manual-only OpenRouter, no automatic OpenRouter fallback, and LiteLLM rollback/Open WebUI wording are present.
- Git status shows only the five slice-scoped documentation files modified.

## Known risks or blockers

- No known blockers.
- These edits are documentation-only and assume the live state provided in `CURRENT_SLICE.md` is authoritative.

## User approval needed

No approval is needed for the documentation-only changes already made.

## Constraints honored

Documentation-only.

No:

- live config edits
- service restarts
- OpenRouter calls
- OpenCode changes
- LiteLLM changes
- Open WebUI changes
- remote mutation

## Recommended next action

Review the git diff, then commit Slice 18 if it matches the live OpenCode state.
