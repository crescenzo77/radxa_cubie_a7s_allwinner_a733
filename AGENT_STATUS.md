# Agent Status

## Current status

Slice 15 is ready to add the generated OpenRouter-free provider to AMD OpenCode as manual-only.

## Current slice

Slice 15: add OpenRouter-free provider to OpenCode as manual-only.

## Why this is next

Slice 14 proved that AMD OpenCode works through the direct local provider:

```text
opencode-direct-local-ok
```

The next narrow step is to add the generated OpenRouter-free provider without changing the default local model.

## Safety posture

This is a live OpenCode config change on AMD.

The slice intentionally does not:

- call OpenRouter
- set OpenRouter as default
- add automatic fallback
- alter LiteLLM
- alter Open WebUI
- restart services
- remove rollback files
- use the broad built-in OpenRouter provider

## Commands to run

Use the commands in `CURRENT_SLICE.md`.

Run in this order:

1. confirm direct-local config still works
2. back up current direct-local config
3. copy generated provider from ThinkCentre to AMD
4. build candidate config
5. validate candidate JSON
6. inspect candidate redacted
7. switch live config
8. validate default still uses direct local provider

## Expected success result

OpenCode should still respond exactly:

```text
opencode-direct-local-ok
```

The output should show the AMD local model, not OpenRouter.

## Rollback trigger

Rollback immediately if:

- candidate JSON validation fails
- live JSON validation fails
- OpenCode no longer defaults to AMD direct local provider
- OpenCode attempts to use OpenRouter during the local validation
- OpenCode cannot start
- any unexpected config shape appears

## Result

Not executed yet.

## Recommended next action

Transfer these files into `strix:/srv/projects/homelab/`, commit the slice, then execute the Slice 15 command blocks from `CURRENT_SLICE.md`.
