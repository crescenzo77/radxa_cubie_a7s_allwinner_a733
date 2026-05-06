# Agent Status

## Current status

Slice 14 is ready to execute the first controlled live OpenCode migration on AMD.

## Current slice

Slice 14: execute AMD OpenCode direct-local migration.

## Why this is next

Slice 13 produced the approval brief for a narrow direct-local migration.

The next logical step is to execute only that narrow change:

- direct AMD local-coder provider
- no OpenRouter provider yet
- no LiteLLM removal
- no Open WebUI changes

## Safety posture

This is a live OpenCode config change on AMD.

The rollback path is documented before execution.

The migration intentionally does not:

- add OpenRouter
- call OpenRouter
- alter LiteLLM
- alter Open WebUI
- restart Docker services
- delete old config
- set `small_model` to the AMD 3090 model

## Commands to run

Use the commands in `CURRENT_SLICE.md`.

Run in this order:

1. backup current live config
2. create candidate direct-local config
3. validate candidate JSON
4. switch live config
5. inspect live config redacted
6. run local-only OpenCode validation

## Expected success result

OpenCode should respond exactly:

```text
opencode-direct-local-ok
```

## Rollback trigger

Rollback immediately if:

- candidate JSON validation fails
- live JSON validation fails
- OpenCode cannot start
- OpenCode cannot reach the AMD 3090 endpoint
- OpenCode response is clearly not from the direct local provider
- any unexpected OpenRouter call appears likely

## Result

Not executed yet.

## Recommended next action

Transfer these files into `strix:/srv/projects/homelab/`, commit the slice, then execute the Slice 14 command blocks from `CURRENT_SLICE.md`.
