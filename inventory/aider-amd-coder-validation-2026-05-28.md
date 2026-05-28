# Aider AMD Coder Validation - 2026-05-28

Purpose: record the first bounded Aider edit through AMD `local/amd-coder`.

## Validated Path

- Host: `amd`
- Repo edited: `/srv/projects/cubie-camera-node`
- Endpoint: `http://192.168.50.225:4010/v1`
- model-dispatch alias: `local/amd-coder`
- Container: `qwen3-coder-30b`
- Harness: llama.cpp CUDA
- Model: `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
- Aider: `0.86.2`
- Aider model argument: `openai/local/amd-coder`
- Edit format: `diff`
- Streaming: disabled
- Repo map: disabled with `--map-tokens 0`
- Auto-commits: disabled
- Gitignore edits: disabled

## Result

Aider edited exactly one tracked file:

- `/srv/projects/cubie-camera-node/README.md`

Aider history files were pointed outside the repo:

- `/tmp/aider-amd-coder-input.history`
- `/tmp/aider-amd-coder-chat.history.md`
- `/tmp/aider-amd-coder-llm.history`

Committed and pushed in `cubie-camera-node`:

- `cd4b5a1 validate AMD coder bounded patch`

## Validation

- AMD `qwen3-coder-30b` was healthy on port `8083`.
- model-dispatch `local/amd-coder` returned clean `ok`.
- Aider exited `0`.
- `git diff --check` passed.
- Final diff was one README sentence.
- Push to `thinkcentre:/srv/git/cubie-camera-node.git` succeeded.

## Boundary

This validates a tiny one-file documentation edit only.

It does not validate:

- broad repo maps
- long context
- multi-file edits
- autonomous coding workflows
- service edits
- deployment changes
- tool-call loop behavior

Keep AMD `local/amd-coder` as a validated bounded patch-tool candidate, not a
default autonomous coder.
