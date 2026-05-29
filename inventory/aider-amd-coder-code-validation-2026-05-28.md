# Aider AMD Coder Code Validation - 2026-05-28

Purpose: record the first tiny code-file Aider edit through AMD
`local/amd-coder`.

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

Aider created exactly one tracked code file:

- `/srv/projects/cubie-camera-node/scripts/cubie-node-summary`

The helper prints:

```text
project=cubie-camera-node
source_host=strix
deployment_status=not-deployed
```

Aider history files were pointed outside the repo:

- `/tmp/aider-amd-code-input.history`
- `/tmp/aider-amd-code-chat.history.md`
- `/tmp/aider-amd-code-llm.history`

Committed and pushed in `cubie-camera-node`:

- `d6246ef add Cubie node summary helper`

## Validation

- Aider exited `0`.
- `git diff --check` passed.
- Final diff was one new executable shell script.
- `bash -n scripts/cubie-node-summary` passed.
- `scripts/cubie-node-summary` printed the expected output.
- Push to `thinkcentre:/srv/git/cubie-camera-node.git` succeeded.

## Boundary

This validates a tiny one-file shell-script edit only.

It does not validate:

- multi-file code edits
- test-suite edits
- long-context coding work
- autonomous coding workflows
- service edits
- deployment changes
- Docker or systemd changes

Keep AMD `local/amd-coder` as a validated bounded patch-tool candidate, not a
default autonomous coder.
