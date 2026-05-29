# OpenCode Local Model Follow-Up - 2026-05-28

Purpose: record the follow-up after the initial OpenCode local-model preflight.

## Goal

Check whether the AMD OpenCode failure was only caused by OpenCode's default
large output budget.

## Throwaway Repo

All OpenCode tests remained in:

```text
/tmp/opencode-local-trial
```

No real project repository was edited by OpenCode.

## AMD Output Budget Change

The throwaway `opencode.json` AMD model entry was changed to:

```json
"limit": {
  "context": 32768,
  "output": 4096
}
```

This removed the earlier model-dispatch `context_too_small` rejection.

## OpenCode AMD Result

After lowering the output budget, OpenCode no longer failed with the
context-size error.

It still did not edit `README.md`.

Exported OpenCode session for the AMD attempt showed:

- zero recorded input tokens
- zero recorded output tokens
- zero recorded reasoning tokens
- no tool calls
- no file diffs

## Plain Chat Result

Plain OpenCode chat was tested with:

```sh
opencode run --format json -m homelab/amd-coder-qwen3-coder-30b-32k \
  "Reply with exactly: ok"

opencode run --format json -m homelab/strix-coder-qwen3-coder-next-65k \
  "Reply with exactly: ok"
```

Both emitted only:

- `step_start`
- `step_finish`

Both recorded zero model tokens and no visible model text.

## Direct Tool-Loop Control Check

The same model-dispatch coder aliases passed the existing direct tool-loop
smoke:

```sh
scripts/model-tool-loop-smoke --model local/amd-coder
scripts/model-tool-loop-smoke --model local/strix-coder
```

Both completed successfully.

## Conclusion

The local llama.cpp coder backends and model-dispatch can perform OpenAI-style
tool calls directly.

The current blocker is specific to OpenCode's local provider/run path.

OpenCode remains installed, but it is not validated as a patch tool.

Aider remains the validated bounded patch-tool path.

## Boundary

Do not promote OpenCode into the normal workflow.

Do not change model-dispatch, Open WebUI, Docker, systemd, or routing for
OpenCode unless a separate explicit debugging slice selects that work.
