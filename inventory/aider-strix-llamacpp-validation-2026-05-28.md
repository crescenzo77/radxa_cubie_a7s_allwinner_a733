# Aider Strix llama.cpp Validation - 2026-05-28

Purpose: record the first bounded Aider edit through the restored Strix
llama.cpp/GGUF Coder-Next endpoint.

## Validated Path

- Host: `strix`
- Repo edited: `/srv/projects/cubie-camera-node`
- Endpoint: `http://127.0.0.1:8082/v1`
- Container: `qwen3-coder`
- Harness: llama.cpp Vulkan
- Model: `Qwen3-Coder-Next-UD-Q4_K_XL.gguf`
- Aider: `0.86.2`
- Aider model argument: `openai/Qwen3-Coder-Next-UD-Q4_K_XL.gguf`
- Edit format: `diff`
- Streaming: disabled
- Repo map: disabled with `--map-tokens 0`
- Auto-commits: disabled
- Gitignore edits: disabled

## Result

Aider edited exactly one tracked file:

- `/srv/projects/cubie-camera-node/README.md`

Generated Aider history files were removed before commit:

- `.aider.chat.history.md`
- `.aider.input.history`

Committed and pushed in `cubie-camera-node`:

- `8de720a clarify next hardware checklist step`

## Validation

- Direct Strix `8082` `/v1/models` returned
  `Qwen3-Coder-Next-UD-Q4_K_XL.gguf`.
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

## Repeatable Helper

Use:

```sh
cd /srv/projects/homelab
scripts/aider-strix-coder-llamacpp README.md --message "Make one narrow requested edit."
```

Run the helper from the target repository working tree when editing another
repo. It refuses to run unless Strix Coder-Next is live on `127.0.0.1:8082`.
