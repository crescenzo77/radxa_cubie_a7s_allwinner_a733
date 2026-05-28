# OpenCode Local Model Preflight - 2026-05-28

Purpose: record the first OpenCode local-model preflight after the
provider-neutral patch-review workflow was established.

## Installation

OpenCode was not initially present on Strix or the Mac mini.

The official installer URL failed from Strix:

```sh
curl -fsSL https://opencode.ai/install | bash
```

Failure:

```text
curl: (7) Failed to connect to opencode.ai port 443
```

Strix had general internet access, verified against GitHub, and had `npm`.
OpenCode was installed with:

```sh
npm install -g opencode-ai
```

Installed version:

```text
1.15.12
```

Binary path:

```text
/home/enzo/.local/npm-global/bin/opencode
```

## Throwaway Trial Setup

Repo:

```text
/tmp/opencode-local-trial
```

The trial used a project-local `opencode.json` with an OpenAI-compatible
provider:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "homelab": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Homelab model-dispatch",
      "options": {
        "baseURL": "http://192.168.50.225:4010/v1",
        "apiKey": "dummy"
      },
      "models": {
        "amd-coder-qwen3-coder-30b-32k": {
          "name": "AMD Qwen3-Coder 30B"
        },
        "strix-coder-qwen3-coder-next-65k": {
          "name": "Strix Qwen3-Coder-Next"
        }
      }
    }
  }
}
```

OpenCode listed both configured models:

```text
homelab/amd-coder-qwen3-coder-30b-32k
homelab/strix-coder-qwen3-coder-next-65k
```

## AMD Result

Command shape:

```sh
opencode run -m homelab/amd-coder-qwen3-coder-30b-32k \
  "Edit README.md only. Replace the line old line with exactly: opencode local amd coder test passed. Do not change opencode.json. Do not edit any other file. Do not commit."
```

Result:

- OpenCode reached model-dispatch.
- model-dispatch rejected the request before editing.
- Reason: `context_too_small`.
- Estimated total tokens: `34682`.
- AMD context: `32768`.

## Strix Result

Command shape:

```sh
opencode run -m homelab/strix-coder-qwen3-coder-next-65k \
  "Edit README.md only. Replace the line old line with exactly: opencode local strix coder test passed. Do not change opencode.json. Do not edit any other file. Do not commit."
```

Result:

- OpenCode reached the configured Strix model.
- OpenCode exited `0`.
- `README.md` was not edited.
- Exported OpenCode session showed zero recorded model tokens.
- Exported OpenCode session showed no tool calls.

## Boundary

This is not a successful OpenCode patch validation.

Validated:

- OpenCode can be installed on Strix.
- OpenCode can load a project-local OpenAI-compatible provider config.
- OpenCode can list model-dispatch-backed local models.

Not validated:

- OpenCode editing through AMD `local/amd-coder`.
- OpenCode editing through Strix `local/strix-coder`.
- OpenCode as a replacement for Aider in the patch-review workflow.

Recommended follow-ups, only if explicitly selected:

- Tune OpenCode prompt/output budget for AMD.
- Investigate the Strix zero-token/no-tool-call result.
- Test OpenCode against the validated vLLM tool-call harness.
