# Agent Status

## Current status

Slice 13 approval brief has been prepared as downloadable Markdown for transfer into the homelab repo.

## Current slice

Slice 13: prepare AMD OpenCode direct-local live-change approval brief.

## What changed

Prepared documentation only:

- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`

No live config was edited.

## What did not change

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

## Slice 13 decision

The first live OpenCode migration should be narrower than the full target architecture.

Approved draft direction for the next live-change brief:

- direct AMD local provider only
- no OpenRouter provider yet
- no OpenRouter calls
- no LiteLLM removal
- no Open WebUI changes
- no automatic fallback
- no `small_model` set to the AMD 3090 model

Reason:

The direct local provider should be validated independently before introducing the generated OpenRouter-free manual provider.

## Prepared approval brief

The approval brief in `CURRENT_SLICE.md` includes:

1. AMD backup command.
2. Candidate config path.
3. Direct-local candidate config.
4. Candidate JSON validation command.
5. Live switch command.
6. Local-only OpenCode validation command.
7. Rollback command.

## Known risks or blockers

- OpenCode candidate config may need adjustment if `enabled_providers` or model naming behaves differently than expected.
- The first live test should validate AMD direct local provider only.
- Direct AMD 7900 XT backup provider is intentionally not included in this first live change.
- Generated `homelab-openrouter-free` provider is intentionally not included in this first live change.

## User approval needed

Approval is required before running any command that:

- writes `/home/enzo/.config/opencode/opencode.json`
- changes OpenCode provider settings
- calls OpenCode against any provider
- calls OpenRouter
- changes LiteLLM or Open WebUI
- restarts services
- mutates a remote host

## Recommended next action

Transfer these Markdown files into `strix:/srv/projects/homelab/`, commit them, then review the approval brief before running any live-change command.
