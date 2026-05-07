# Agent Status

## Current status

Slice 18 is ready to synchronize documentation with the live AMD 7900 XT backup provider.

## Current slice

Slice 18: synchronize docs with AMD 7900 XT backup provider.

## Why this is needed

Live AMD OpenCode now includes:

- `homelab-local` for AMD 3090 primary.
- `homelab-local-backup` for AMD 7900 XT backup.
- `homelab-openrouter-free` for manual free-only OpenRouter use.

The repo was synchronized after OpenRouter-free was added, but now needs a smaller update to include the 7900 XT backup provider.

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

## Constraints

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

Transfer these files into `strix:/srv/projects/homelab/`, commit the slice transition, then perform documentation edits only.
