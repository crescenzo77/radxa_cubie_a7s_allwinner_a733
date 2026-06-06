# model-dispatch Route Audit

Generated: `2026-06-06T18:14:53.511499Z`
Status: `needs-reconciliation`

## Source

| field | value |
| --- | --- |
| host | `192.168.50.11` |
| dir | `/srv/projects/model-dispatch` |
| commit | `524a201c293ebeb669201d221f227c16e463b482` |
| status | `clean` |
| probe host | `192.168.50.225` |

## Expected Kernel Lanes

| lane | endpoint | expected model | reachable from probe host | model advertised | configured exactly |
| --- | --- | --- | --- | --- | --- |
| amd-fast | `http://192.168.50.252:8001/v1` | `qwen3.6-27b-q4km-amd-rtx3090-vulkan` | no | no | no |
| amd-research | `http://192.168.50.252:8092/v1` | `qwen36-27b-7900xt-research` | no | no | no |
| strix-review | `http://192.168.50.11:8082/v1` | `qwen3.6-27b-q4km-native-vulkan` | no | no | no |

## Configured Endpoint Models

| id | endpoint | served model | reachable | served model advertised | routes | error |
| --- | --- | --- | --- | --- | --- | --- |
| `strix-reasoning-qwen3.6-65k` | `http://192.168.50.11:8081/v1` | `Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf` | no | no | auto-local, auto-coding-local, auto-reasoning-local, auto-small-local, local/strix-reasoning, review/strix-halo-llamacpp-qwen36-35b-udq4xl-65k | URLError: <urlopen error [Errno 111] Connection refused> |
| `strix-coder-qwen3-coder-next-65k` | `http://192.168.50.11:8082/v1` | `Qwen3-Coder-Next-UD-Q4_K_XL.gguf` | no | no | auto-local, auto-coding-local, auto-reasoning-local, local/strix-coder, review/strix-halo-llamacpp-qwen3-coder-next-udq4xl-65k, agent/qwen-code-strix-halo-llamacpp-qwen3-coder-next-udq4xl-65k, patch/aider-strix-halo-llamacpp-qwen3-coder-next-udq4xl-65k | URLError: <urlopen error [Errno 111] Connection refused> |
| `amd-coder-qwen3-coder-30b-32k` | `http://192.168.50.252:8083/v1` | `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` | no | no | auto-local, auto-coding-local, auto-reasoning-local, auto-small-local, local/amd-coder, agent/qwen-code-amd3090-llamacpp-qwen3-coder-30b-q4km-32k, patch/aider-amd3090-llamacpp-qwen3-coder-30b-q4km-32k | URLError: <urlopen error [Errno 111] Connection refused> |
| `amd-backup-gemma4-26b-8k` | `http://192.168.50.252:8084/v1` | `google_gemma-4-26B-A4B-it-Q4_K_M.gguf` | no | no | auto-small-local, local/amd-small | URLError: <urlopen error [Errno 111] Connection refused> |
| `local/strix-qwen36-awq-agent` | `http://192.168.50.11:8010/v1` | `qwen36-awq-agent-test` | no | no | test/strix-halo-vllm-qwen36-awq-tool-8k, local/tool-test | URLError: <urlopen error [Errno 111] Connection refused> |
| `local/strix-qwen3-coder-next-awq-agent` | `http://192.168.50.11:8010/v1` | `qwen3-coder-next-awq-agent-test` | no | no | test/strix-halo-vllm-qwen3-coder-next-awq-code-8k, local/code-test | URLError: <urlopen error [Errno 111] Connection refused> |

## Required Action

Do not deploy `model-dispatch` for the kernel workflow until stale configured models are reconciled and all expected lanes are configured exactly.

If expected endpoints are reachable only through host-local `127.0.0.1` bindings, choose an explicit access pattern before repair: LAN-bind those services, add reviewed tunnels, or keep `model-dispatch` outside the kernel workflow.

This audit is read-only and does not change live services, systemd, Open WebUI, or model routes.
