# AMD Temporary vLLM Runtime Test Plan

## Purpose

Plan the first approved temporary AMD vLLM runtime test while preserving the
healthy current llama.cpp endpoints. This plan does not start vLLM, stop
containers, change routing, change Open WebUI, run Aider, pull models, or edit
live service files.

The future test should answer only one question: can the already inspected
local vLLM image serve an appropriate local HF/safetensors-style model on AMD
through an OpenAI-compatible API long enough for curl-only validation?

## Current Proven Facts

- Latest homelab commit before this slice:
  `fc15397 document amd vllm phase 2 image inspection`.
- AMD Phase 1 live-state recheck is documented.
- AMD Phase 2 local vLLM image/runtime inspection is documented.
- Local AMD Docker image exists: `vllm/vllm-openai:latest`.
- The image provides:
  - `python3`
  - Python `3.12.13`
  - torch `2.10.0+cu129`
  - CUDA `12.9`
  - vLLM `0.19.0`
- The image can see RTX 3090 when run with `--gpus all`.
- Existing AMD containers remained healthy after dry checks:
  - `qwen3-coder-30b` on port `8083`
  - `gemma4-7900xt` on port `8084`
- RTX 3090 VRAM is mostly occupied by `qwen3-coder-30b`.
- vLLM has not been started.
- `qwen3-coder-30b` has not been stopped.
- `model-dispatch` and Open WebUI remain unchanged.

## Why The Test Must Be Temporary

AMD is currently serving useful local endpoints. The first vLLM runtime test is
not a migration, not a routing change, and not a replacement for the current
llama.cpp containers.

The test must be temporary because:

- RTX 3090 VRAM is already occupied by the healthy `qwen3-coder-30b` service.
- Stopping that service would temporarily remove the active AMD coder endpoint.
- The vLLM model format and candidate model are not yet proven.
- A temporary container with an explicit name, temporary port, and explicit
  rollback command is easier to review and undo.
- `model-dispatch` and Open WebUI should not point at vLLM until direct
  curl-only checks prove the endpoint shape.

## Candidate Image

Exact candidate image:

```text
vllm/vllm-openai:latest
```

This is the local AMD image already inspected in Phase 2. Do not pull a new
image during the runtime-test execution slice unless a separate approval brief
explicitly changes the image candidate.

## Candidate Model

Exact candidate model for the future command should be a local
HF/safetensors-style Qwen coder model directory, if one is already present on
AMD.

Proposed placeholder until local path is proven:

```text
/models/<local-hf-safetensors-qwen-coder-model>
```

The future runtime execution slice must replace this placeholder with an exact
local path from a read-only model inventory before any container is stopped.

## Model Format Concern

vLLM generally expects Hugging Face-style model directories with supported
config/tokenizer files and weight formats such as safetensors or compatible
PyTorch checkpoints.

The current AMD Qwen coder artifact is a GGUF model served by llama.cpp. GGUF
is the right artifact type for llama.cpp, but it is likely unsuitable for this
vLLM test.

Do not treat the existing GGUF artifact as the vLLM candidate unless a later
read-only inspection proves the installed vLLM version and launch path support
that exact GGUF model. The conservative assumption is that the GGUF model is
not suitable for vLLM.

Strong warning:

- Do not stop `qwen3-coder-30b` until the model candidate and vLLM model format
  are proven.
- If no HF/safetensors model is present locally, stop and plan model
  acquisition separately instead of trying to force vLLM to serve GGUF.

## Candidate Port Selection

Use a temporary port that does not collide with current AMD services.

Known occupied AMD ports:

- `8083`: `qwen3-coder-30b`
- `8084`: `gemma4-7900xt`

Candidate temporary port:

```text
18000
```

Rationale:

- Avoids the current 8083 and 8084 endpoints.
- Avoids common default `8000` if another local experiment uses it.
- Makes temporary validation obvious in command history and curl checks.

The future execution slice should confirm the port is free before launch with a
read-only check.

## Resource And VRAM Issue

The RTX 3090 is the intended GPU for the first AMD vLLM test. It is currently
mostly occupied by `qwen3-coder-30b`, so a real vLLM launch may fail with
insufficient VRAM unless the current coder container is stopped first.

That stop decision is operationally meaningful because it affects the healthy
AMD coder endpoint on port `8083`. It must happen only after:

- An exact local HF/safetensors-compatible model path is proven.
- The future Docker command is reviewed.
- The operator explicitly approves the temporary interruption.

`gemma4-7900xt` on port `8084` should not be stopped for this test.

## Decision Point For Stopping `qwen3-coder-30b`

Before runtime execution, stop and ask for approval with a plain-English brief
if all of these are true:

- A suitable local HF/safetensors-style model directory exists.
- The model is a useful vLLM candidate for coding or endpoint-shape validation.
- Port `18000` or the selected temporary port is free.
- The future command is ready and includes a rollback command.
- The only remaining blocker is RTX 3090 VRAM currently used by
  `qwen3-coder-30b`.

Do not ask to stop `qwen3-coder-30b` if the model candidate is still a
placeholder or only a GGUF artifact is available.

## Proposed Future Docker Run Shape

Do not run this in this planning slice.

Future reviewed shape, with placeholders that must be resolved first:

```bash
docker run --rm --name amd-vllm-temp-test \
  --gpus all \
  -p 18000:8000 \
  -v /models/<local-hf-safetensors-qwen-coder-model>:/model:ro \
  vllm/vllm-openai:latest \
  --model /model \
  --host 0.0.0.0 \
  --port 8000 \
  --served-model-name amd-vllm-temp-qwen-coder
```

Future execution notes:

- The exact host model path must be proven before approval.
- The container name should stay temporary and explicit.
- The model mount should be read-only.
- The served model name should be temporary and must not be added to
  `model-dispatch` during the first curl-only test.
- Do not add restart policy, daemon behavior, Compose files, or systemd units.

## Curl-Only Validation Checks

After a future approved runtime launch, validate directly against the temporary
vLLM endpoint only.

Model list:

```bash
curl -sS http://127.0.0.1:18000/v1/models
```

Minimal chat completion:

```bash
curl -sS http://127.0.0.1:18000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "amd-vllm-temp-qwen-coder",
    "messages": [
      {"role": "user", "content": "Reply with exactly: vllm-ok"}
    ],
    "max_tokens": 16,
    "temperature": 0
  }'
```

Response-shape checks:

- `/v1/models` returns parseable JSON.
- The advertised model ID matches `amd-vllm-temp-qwen-coder` or the reviewed
  served-model name.
- `/v1/chat/completions` returns parseable JSON.
- `choices[0].message.content` is present and non-empty.
- No `model-dispatch`, Open WebUI, Aider, OpenCode, Continue.dev, LiteLLM, or
  monitoring path is involved.

## Stop And Rollback Command

Future rollback command for the temporary vLLM container:

```bash
docker stop amd-vllm-temp-test
```

If `qwen3-coder-30b` was explicitly stopped for VRAM, the future execution
slice must include the exact operator-approved command to restore it before any
stop happens. Do not infer or invent that restore command in this planning
slice.

## What Not To Change

- Do not start vLLM in this slice.
- Do not stop or restart `qwen3-coder-30b`.
- Do not stop or restart `gemma4-7900xt`.
- Do not run Aider.
- Do not edit `model-dispatch`.
- Do not edit `/srv/model-dispatch`.
- Do not change Open WebUI.
- Do not change OpenCode.
- Do not change Continue.dev.
- Do not change LiteLLM.
- Do not change dashboards, monitoring, or observability.
- Do not add Docker Compose files, systemd units, restart policies, daemons,
  watchers, wrappers, or hidden background jobs.
- Do not run `sudo`, Docker write commands, or systemd write commands in this
  planning slice.
- Do not commit in this slice.

## Go/No-Go Criteria Before Runtime Execution

Go only if all are true:

- Exact local HF/safetensors-style model path is known.
- The model directory is plausibly compatible with vLLM.
- The candidate image remains `vllm/vllm-openai:latest` unless separately
  approved.
- Temporary port is proven free.
- The operator approves any interruption to `qwen3-coder-30b`.
- The launch command and rollback command are both reviewed.
- The test remains direct curl-only and does not touch routing or clients.

No-go if any are true:

- The only available Qwen coder artifact is GGUF.
- The model path is still a placeholder.
- Stopping `qwen3-coder-30b` has not been explicitly approved.
- The proposed command would add persistent runtime behavior.
- The test requires editing `model-dispatch`, Open WebUI, OpenCode,
  Continue.dev, LiteLLM, dashboards, monitoring, or observability.

Recommended next action after this docs slice:

1. Open a read-only model inventory slice on AMD.
2. Prove whether a local HF/safetensors-style candidate exists.
3. If no local candidate exists, stop and plan model acquisition separately.
4. Only after a candidate is proven, request approval for a temporary runtime
   execution window.
