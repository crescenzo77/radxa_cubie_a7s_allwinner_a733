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
## Slice 14 execution result

Executed successfully on 2026-05-06.

Backup created on AMD:

```text
/home/enzo/.config/opencode/opencode.json.bak.20260506-165737
```

Live AMD OpenCode config was switched to direct local provider only:

- provider: `homelab-local`
- base URL: `http://192.168.50.252:8083/v1`
- model: `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
- OpenRouter provider: not added
- LiteLLM: unchanged
- Open WebUI: unchanged

Validation command run directly on AMD:

```bash
timeout 180 /home/enzo/.opencode/bin/opencode run "Reply with exactly: opencode-direct-local-ok"
```

Validation output:

```text
build · Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf

opencode-direct-local-ok
```

Result:

- Direct local OpenCode path works.
- No OpenRouter call was made.
- LiteLLM remains available as rollback.
- Open WebUI remains unchanged.

Recommended next action:

Create a separate slice to add the generated `homelab-openrouter-free` provider as a manual-only provider, after preserving the direct local provider as default.
