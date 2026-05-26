# AMD vLLM Manual Mode-Switch Runbook

## Purpose

This runbook documents the manual, temporary AMD RTX 3090 mode switch from the
normal `qwen3-coder-30b` llama.cpp service on port `8083` to vLLM on port
`18000`, then back to `qwen3-coder-30b`.

Do not execute this procedure as part of this documentation slice.

## Critical Warning

This procedure intentionally takes `amd:8083` offline while vLLM owns RTX 3090.
Do not run this during work that depends on `qwen3-coder-30b`.

Do not add restart policies, Compose files, systemd units, wrappers, or
automation. Do not edit `model-dispatch` or Open WebUI as part of the mode
switch.

## When To Use It

Use this procedure only when an operator explicitly needs the proven temporary
AMD vLLM endpoint for a bounded manual test, such as:

- direct curl validation of vLLM response shape
- direct Aider-to-vLLM validation against one planned file
- short manual experiments that can tolerate `amd:8083` being offline

Use it only when the operator is prepared to restore `qwen3-coder-30b`
immediately afterward.

## When Not To Use It

Do not use this procedure when:

- current work depends on `qwen3-coder-30b` on port `8083`
- Open WebUI or another client expects normal AMD coder availability
- the operator cannot monitor the switch and rollback
- the goal is to add persistent vLLM infrastructure
- the goal is to change `model-dispatch`, Open WebUI, OpenCode, Continue.dev,
  LiteLLM, dashboard, monitoring, or routing configuration
- the goal can be handled by the still-running `gemma4-7900xt` backup on port
  `8084`

## Prerequisites

- Operator shell access on AMD.
- The RTX 3090 is currently assigned to normal `qwen3-coder-30b` mode.
- The `gemma4-7900xt` backup container is expected to remain running.
- The Hugging Face model directory exists at
  `/srv/llm/hf/Qwen2.5-Coder-7B-Instruct`.
- The vLLM image is available or can be pulled intentionally by the operator:
  `vllm/vllm-openai:latest`.
- No one is relying on `amd:8083` during the temporary vLLM window.
- The operator has reviewed this runbook and accepts that `8083` and `18000`
  are mutually exclusive RTX 3090 modes.

## Exact Runtime Facts

Normal RTX 3090 mode:

```text
container: qwen3-coder-30b
port: 8083
model: Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf
```

Gemma backup mode that should remain running:

```text
container: gemma4-7900xt
port: 8084
model: google_gemma-4-26B-A4B-it-Q4_K_M.gguf
```

Temporary vLLM mode:

```text
container: amd-vllm-temp-test
host port: 18000
container port: 8000
model path: /srv/llm/hf/Qwen2.5-Coder-7B-Instruct
served model: amd-vllm-temp-qwen2.5-coder-7b
image: vllm/vllm-openai:latest
dtype: float16
max model length: 16384
gpu memory utilization: 0.90
generation config: vllm
```

Relevant paths and endpoints:

```text
homelab repo: /srv/projects/homelab
model-dispatch live path, do not edit: /srv/model-dispatch
model-dispatch source path, do not edit: /srv/projects/model-dispatch
normal qwen endpoint: http://192.168.50.252:8083/v1
gemma backup endpoint: http://192.168.50.252:8084/v1
temporary vLLM endpoint: http://192.168.50.252:18000/v1
```

## Preflight Checks

Run read-only checks before changing anything:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'qwen3-coder-30b|gemma4-7900xt|amd-vllm-temp-test'
curl -fsS http://127.0.0.1:8083/v1/models
curl -fsS http://127.0.0.1:8084/v1/models
test -d /srv/llm/hf/Qwen2.5-Coder-7B-Instruct
nvidia-smi
```

Expected preflight state:

- `qwen3-coder-30b` is running.
- `gemma4-7900xt` is running.
- `amd-vllm-temp-test` is not running.
- `8083` responds before the switch.
- `8084` responds before the switch.
- RTX 3090 has enough freeable VRAM after `qwen3-coder-30b` is stopped.

If any expectation fails, stop and decide whether to fix the existing service
state or postpone the test. Do not continue into vLLM mode from an unclear
baseline.

## Stop qwen3-coder-30b

Stop only the RTX 3090 normal-mode container:

```bash
docker stop qwen3-coder-30b
```

Confirm that port `8083` is intentionally offline and that `gemma4-7900xt`
remains running:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'qwen3-coder-30b|gemma4-7900xt|amd-vllm-temp-test'
curl -fsS http://127.0.0.1:8084/v1/models
nvidia-smi
```

Do not stop or restart `gemma4-7900xt`.

## Start Temporary vLLM

Start the temporary vLLM container manually:

```bash
docker run --rm -d \
  --name amd-vllm-temp-test \
  --gpus all \
  -p 18000:8000 \
  -v /srv/llm/hf/Qwen2.5-Coder-7B-Instruct:/model:ro \
  vllm/vllm-openai:latest \
  --model /model \
  --host 0.0.0.0 \
  --port 8000 \
  --served-model-name amd-vllm-temp-qwen2.5-coder-7b \
  --dtype float16 \
  --max-model-len 16384 \
  --gpu-memory-utilization 0.90 \
  --generation-config vllm
```

Do not add `--restart`, Compose, systemd, wrappers, or any background
automation.

Use the NVIDIA Docker runtime path for this vLLM test. The previously validated
working command used `--gpus all` against the RTX 3090. Do not substitute ROCm
device flags for this NVIDIA-backed vLLM container.

## Wait For vLLM Checks

In another shell, wait for vLLM to appear and become responsive:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep amd-vllm-temp-test
docker logs --tail 80 amd-vllm-temp-test
curl -fsS http://127.0.0.1:18000/v1/models
nvidia-smi
```

Expected state:

- `amd-vllm-temp-test` is running.
- `18000` is mapped to container port `8000`.
- logs show the OpenAI-compatible server is ready.
- `nvidia-smi` shows RTX 3090 memory owned by vLLM.
- `gemma4-7900xt` remains running separately on `8084`.

## vLLM /v1/models Check

Validate the served model name:

```bash
curl -fsS http://127.0.0.1:18000/v1/models
```

Expected model ID:

```text
amd-vllm-temp-qwen2.5-coder-7b
```

If the served model ID differs, do not use the endpoint for Aider or routing
tests until the mismatch is understood.

## vLLM /v1/chat/completions Check

Validate a small non-streaming chat completion:

```bash
curl -fsS http://127.0.0.1:18000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "amd-vllm-temp-qwen2.5-coder-7b",
    "messages": [
      {
        "role": "user",
        "content": "Reply with exactly: vllm-ready"
      }
    ],
    "max_tokens": 16,
    "temperature": 0,
    "stream": false
  }'
```

Expected result:

- HTTP request succeeds.
- JSON response includes a `choices` array.
- The assistant content is short and confirms readiness.

## Optional Aider Direct Endpoint Command Shape

Use Aider only for a separately approved bounded one-file edit. Keep it direct
to vLLM; do not route through `model-dispatch` for this mode-switch procedure.

Command shape:

```bash
OPENAI_API_BASE=http://192.168.50.252:18000/v1 \
OPENAI_API_KEY=local-not-needed \
aider --model openai/amd-vllm-temp-qwen2.5-coder-7b path/to/one-file.md
```

Operator rules:

- one repo
- one planned file
- no commits by Aider unless explicitly requested
- decline requests to add context/control files
- stop if Aider asks for broader repo or workflow changes

## Rollback To qwen3-coder-30b

Stop the temporary vLLM container:

```bash
docker stop amd-vllm-temp-test
```

Start the normal RTX 3090 container:

```bash
docker start qwen3-coder-30b
```

Do not restart `gemma4-7900xt`.

## Wait For qwen3-coder-30b Health Checks

Wait until `qwen3-coder-30b` is running and `8083` responds:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'qwen3-coder-30b|gemma4-7900xt|amd-vllm-temp-test'
curl -fsS http://127.0.0.1:8083/v1/models
nvidia-smi
```

Expected state:

- `qwen3-coder-30b` is running.
- `amd-vllm-temp-test` is not running.
- `8083` responds with the normal qwen model.
- RTX 3090 memory is owned by `qwen3-coder-30b`.
- `gemma4-7900xt` is still running.

## 8083 And 8084 Validation Checks

Validate both normal and backup endpoints:

```bash
curl -fsS http://127.0.0.1:8083/v1/models
curl -fsS http://127.0.0.1:8084/v1/models
```

Expected IDs:

```text
8083: Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf
8084: google_gemma-4-26B-A4B-it-Q4_K_M.gguf
```

Run one small chat completion against `8083`:

```bash
curl -fsS http://127.0.0.1:8083/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
    "messages": [
      {
        "role": "user",
        "content": "Reply with exactly: qwen-ready"
      }
    ],
    "max_tokens": 16,
    "temperature": 0,
    "stream": false
  }'
```

Run one small chat completion against `8084`:

```bash
curl -fsS http://127.0.0.1:8084/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "google_gemma-4-26B-A4B-it-Q4_K_M.gguf",
    "messages": [
      {
        "role": "user",
        "content": "Reply with exactly: gemma-ready"
      }
    ],
    "max_tokens": 16,
    "temperature": 0,
    "stream": false
  }'
```

## GPU Validation Checks

Use GPU checks at three points:

```bash
nvidia-smi
```

Checkpoints:

- before stopping `qwen3-coder-30b`
- after vLLM is ready
- after `qwen3-coder-30b` is restored

Expected interpretation:

- RTX 3090 is used by `qwen3-coder-30b` in normal mode.
- RTX 3090 is used by `amd-vllm-temp-test` in temporary vLLM mode.
- RX 7900 XT remains available to `gemma4-7900xt`; validate that separately
with container health and the `8084` endpoint rather than using RTX 3090
`nvidia-smi` output.

If GPU ownership is unclear, stop and inspect before running Aider or any
longer prompt.

## Failure Handling

If vLLM fails to start:

1. Capture the relevant `docker logs --tail 120 amd-vllm-temp-test` output.
2. Stop `amd-vllm-temp-test` if it exists.
3. Start `qwen3-coder-30b`.
4. Validate `8083` and `8084`.
5. Record the failure in `AGENT_STATUS.md` or a future runbook revision.

If `8083` does not recover:

1. Confirm `amd-vllm-temp-test` is stopped.
2. Inspect `docker ps -a` for `qwen3-coder-30b`.
3. Inspect recent `qwen3-coder-30b` logs.
4. Leave `gemma4-7900xt` running as the backup on `8084`.
5. Stop and ask for operator review before changing service definitions or
   container configuration.

If `8084` is affected:

1. Do not continue the vLLM test.
2. Do not restart unrelated services casually.
3. Restore normal `qwen3-coder-30b` mode first if possible.
4. Capture status and ask for operator review.

## What Not To Change

- Do not edit `model-dispatch`.
- Do not edit `/srv/model-dispatch`.
- Do not edit `/srv/projects/model-dispatch`.
- Do not change Open WebUI.
- Do not change OpenCode.
- Do not change Continue.dev.
- Do not change LiteLLM.
- Do not add a `model-dispatch` alias.
- Do not route Open WebUI `auto-local` or `auto-coding-local` to vLLM.
- Do not add restart policies.
- Do not add Compose files.
- Do not add systemd units.
- Do not add wrappers.
- Do not add daemons, watchers, schedulers, or automation.
- Do not assume `qwen3-coder-30b` on `8083` and vLLM on `18000` are available
  at the same time.
