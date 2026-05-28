# Strix vLLM Qwen3.6 AWQ Agent Test Runtime

Status: validated manual/test runtime  
Host: `strix`  
Purpose: agent-facing local model harness validation

## Current Purpose

This runtime is the first validated local Qwen3.6-class model/harness path for tool-loop behavior in the homelab.

It is intended for manual testing and controlled validation only. It is not yet a production/persistent inference service.

## Validated Path

client / Open WebUI / smoke test
  -> model-dispatch on thinkcentre:4010
  -> local/tool-test
  -> local/strix-qwen36-awq-agent
  -> Strix vLLM on strix:8010
  -> qwen36-awq-agent-test

## Model

Hugging Face model: cyankiwi/Qwen3.6-35B-A3B-AWQ-4bit  
Served model name: qwen36-awq-agent-test  
Engine image: docker.io/kyuz0/vllm-therock-gfx1151:stable  
Container name: vllm-strix-qwen36-awq-tools-test  
Port: 8010  
Context tested: 8192

## Required Launch Flags

- --skip-mm-profiling
- --enable-auto-tool-choice
- --tool-call-parser qwen3_xml
- --default-chat-template-kwargs '{"enable_thinking": false}'
- --generation-config vllm
- --trust-remote-code
- --enforce-eager

`--skip-mm-profiling` is important because this Qwen3.6 AWQ package includes multimodal/VL config. Without this flag, vLLM attempted a very large multimodal profiling allocation and failed before the API server came up.

## Start Command

Run from the Strix toolbox repo:

    cd /srv/projects/amd-strix-halo-vllm-toolboxes

    CONTAINER_NAME=vllm-strix-qwen36-awq-tools-test \
    ./scripts/run-ubuntu-docker-vllm.sh run -- \
      python -m vllm.entrypoints.openai.api_server \
        --host 0.0.0.0 \
        --port 8010 \
        --model cyankiwi/Qwen3.6-35B-A3B-AWQ-4bit \
        --served-model-name qwen36-awq-agent-test \
        --dtype float16 \
        --max-model-len 8192 \
        --gpu-memory-utilization 0.70 \
        --enforce-eager \
        --generation-config vllm \
        --enable-auto-tool-choice \
        --tool-call-parser qwen3_xml \
        --trust-remote-code \
        --default-chat-template-kwargs '{"enable_thinking": false}' \
        --skip-mm-profiling

The preferred runtime is now Docker Compose at `runtime/strix-qwen36-awq-agent/compose.yml`.

The direct command above is retained as a manual recovery reference, not the preferred day-to-day start path.

## Stop Command

    docker stop vllm-strix-qwen36-awq-tools-test

## Preferred Compose Runtime

The validated runtime is now managed with Docker Compose from the homelab repo:

    cd /srv/projects/homelab
    docker compose -f runtime/strix-qwen36-awq-agent/compose.yml up -d

Check status:

    docker compose -f runtime/strix-qwen36-awq-agent/compose.yml ps

Follow logs:

    docker compose -f runtime/strix-qwen36-awq-agent/compose.yml logs -f

Stop the Compose-managed runtime:

    docker compose -f runtime/strix-qwen36-awq-agent/compose.yml down

The Compose-managed container is:

    vllm-strix-qwen36-awq-agent

It uses:

    restart: unless-stopped

## Basic Validation

    curl -fsS http://127.0.0.1:8010/v1/models | python3 -m json.tool

Expected model id:

    qwen36-awq-agent-test

## model-dispatch Validation

    curl -fsS http://192.168.50.225:4010/v1/models \
      | python3 -m json.tool \
      | grep -A12 -B2 'local/tool-test\|local/strix-qwen36-awq-agent'

Expected aliases:

    local/strix-qwen36-awq-agent
    local/tool-test

## Repeatable Tool-Loop Smoke Test

Run from the homelab repo on Strix:

    cd /srv/projects/homelab
    scripts/model-tool-loop-smoke

Expected final line:

    PASS: model-dispatch tool loop completed successfully.

The default smoke-test model is:

    local/tool-test

To test the explicit backend alias directly:

    scripts/model-tool-loop-smoke --model local/strix-qwen36-awq-agent

## Validated Behavior

Validated successfully:

- Direct Strix vLLM /v1/models.
- Direct Strix vLLM normal chat.
- Direct Strix vLLM JSON-only response.
- Direct Strix vLLM OpenAI-style tool_calls.
- Direct Strix vLLM multi-turn tool-result follow-up.
- Remote Framework access to Strix vLLM.
- Open WebUI manual model selection through model-dispatch.
- model-dispatch direct chat through local/strix-qwen36-awq-agent.
- model-dispatch OpenAI-style tool call through local/strix-qwen36-awq-agent.
- model-dispatch multi-turn tool-result follow-up.
- Repeatable smoke test through scripts/model-tool-loop-smoke.
- Stable test role alias local/tool-test.

## Boundaries

- local/tool-test is manual/test-only.
- Do not add this model to auto routes yet.
- Do not make this the Open WebUI default yet.
- Docker Compose is now the preferred runtime definition for this container.
- The Coder-Next test runtime at `runtime/strix-qwen3-coder-next-awq-test/compose.yml` also uses port 8010.
- With the current one-port Strix setup, `local/tool-test` and `local/code-test` are mode-specific aliases, not simultaneously live services.
- Do not create systemd, watchdog, or additional automation until explicitly selected.
- This does not yet prove long-context stability, production reliability, speed, all-agent compatibility, or full recovery after host reboot.
- Aider is not validated for this model path. Aider connected but received an empty response and made no edit.
- Existing llama.cpp model containers on Strix and AMD were intentionally stopped during this inference-harness work.

## Related Coder-Next Test Runtime

The validated Coder-Next test runtime is:

    runtime/strix-qwen3-coder-next-awq-test/compose.yml

It serves:

    qwen3-coder-next-awq-agent-test

model-dispatch aliases:

    local/strix-qwen3-coder-next-awq-agent
    local/code-test

Use the mode-switch helper for manual one-port runtime switching:

    cd /srv/projects/homelab
    scripts/strix-vllm-mode status
    scripts/strix-vllm-mode code

The helper stops the other Compose runtime, starts the selected Compose runtime, waits for the expected served model on `127.0.0.1:8010`, then runs the matching smoke test:

- `code` validates `local/code-test`.
- `tool` validates `local/tool-test`.

To restore the current stable baseline after Coder-Next testing:

    cd /srv/projects/homelab
    scripts/strix-vllm-mode tool

The helper was validated end to end by switching from `tool` to `code`, passing the Coder-Next smoke test, then switching back to `tool` and passing the Qwen3.6 smoke test.

Qwen2.5-Coder-7B was also tested under vLLM. It passed normal chat but did not produce OpenAI-style tool calls with the tested parser setup, so it is not part of the current tool-call contract.

## Current Known Good Checkpoints

Homelab repo checkpoint after defaulting the smoke test to the role alias:

    99619f5 default tool loop smoke test to role alias

model-dispatch checkpoint after adding role aliases:

    a44126f add local tool test role alias

Homelab repo checkpoint after adding the Compose runtime:

    32ba194 add compose runtime for strix qwen36 awq vllm

Homelab repo checkpoint after preserving the Coder-Next test runtime:

    1ba8b71 add qwen3 coder next awq test runtime

Homelab repo checkpoint after adding and validating the mode-switch helper:

    9fc1776 add strix vllm mode switch helper
