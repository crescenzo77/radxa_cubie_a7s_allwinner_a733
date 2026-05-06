# Agent Status

## Current status

Slice 10 is complete for syntax validity.

OpenCode supports this generated provider API key placeholder:

```json
"apiKey": "{env:OPENROUTER_API_KEY}"
```

Official OpenCode config documentation confirms `{env:VARIABLE_NAME}` substitution in config files, including provider `options.apiKey`. If the environment variable is unset, OpenCode substitutes an empty string.

## Current slice

Slice 12: draft OpenCode direct-provider migration.

## What changed

Updated repo state docs only:

- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`

Slice 12 is now the active next slice.

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

No OpenRouter model calls were made.

## Slice 12 task

Prepare a non-live draft migration from the current OpenCode LiteLLM-only configuration to:

- direct local provider for AMD `local-coder`
- generated `homelab-openrouter-free` provider for manual OpenRouter free-only use

Allowed work:

- inspect current AMD OpenCode config read-only using the normal SSH alias
- inspect `/srv/openrouter-free/opencode.generated.json` read-only using the normal SSH alias
- design a proposed `opencode.json` shape
- document rollback path

Not allowed:

- editing `/home/enzo/.config/opencode/opencode.json`
- changing OpenCode live provider settings
- altering LiteLLM or Open WebUI
- calling any OpenRouter model
- making live service changes
- printing secrets

## Checks run

Documentation reads for this slice setup:

- `AGENTS.md`
- `CODEX_CONTEXT.md`
- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`
- `ROADMAP.md`
- `WORKFLOW.md`
- `HOMELAB_LAYOUT.md`
- `DECISIONS.md`

No remote inspection was run during this slice-creation step.

## Results of checks

The repo docs support Slice 12 as the next narrow step in the router transition:

- AMD is the current OpenCode execution host.
- The target OpenCode path is direct local-coder on AMD.
- OpenRouter remains allowed only as generated free-only manual fallback.
- LiteLLM remains temporary rollback and must not be altered during this draft.

## Known risks or blockers

- Normal SSH from the Codex environment previously failed on the system SSH client config permission error, even though user-run diagnostics reportedly worked with normal aliases.
- The migration draft depends on read-only inspection of the AMD OpenCode config and generated OpenRouter-free artifact.
- Any live OpenCode config change remains out of scope until a later approval brief.

## User approval needed

No approval is needed for the repo-doc update already made.

Approval will be needed before:

- editing live OpenCode config
- changing OpenCode provider settings
- altering LiteLLM or Open WebUI
- calling any OpenRouter model
- making live service changes
- mutating any remote host

## Recommended next action

Run Slice 12 as a read-only draft:

1. Inspect AMD OpenCode config with the normal SSH alias.
2. Inspect `/srv/openrouter-free/opencode.generated.json` with the normal SSH alias.
3. Draft the proposed `opencode.json` shape and rollback path in `AGENT_STATUS.md`.
4. Stop before any live config edit.
