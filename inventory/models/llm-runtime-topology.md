# LLM Runtime Topology

## Purpose and scope

This document describes the stable structure of local LLM services across
`strix`, `thinkcentre`, and `AMD`.

It is intended for human review, Hermes, and CodeGraphContext indexing. It
captures service roles, endpoint locations, runtime families, and source/config
path hints where those are known from the current inventory snapshot and prior
validation context.

For a shorter operational map of LLM runtimes, agent/tool roles, hooks, gates,
and skill/MCP notes, read
`inventory/models/llm-agents-tools-quick-reference.md`.

## Structural inventory only

This is structural inventory, not runtime monitoring.

Do not treat this file as a daily activity log, request log, Docker status log,
health monitor, uptime record, or cache index. Transient runtime details such as
exact observation timestamps, container uptime, `Up`/`Exited` churn, health
status, Docker stats, and unrelated containers are intentionally excluded.

## Standing deployment preference

Future LLM services should be isolated as one service/model per Docker
container and managed with `docker-compose.yml`. Use a custom `Dockerfile` only
when an upstream image plus mounted configuration is not enough.

## Current compose-managed runtime snapshot

Updated: 2026-06-08

| Host | Endpoint | Container | Image/runtime | Compose path |
|---|---:|---|---|---|
| `strix` | `192.168.50.11:8080` | `qwen36-rocmfp4` | `local/rocmfp4-llama:strix` from `charlie12345/rocmfp4-llama` branch `mtp-rocmfp4-strix` | `/srv/llm/containers/rocmfp4-llama/compose.yml` |
| `amd` | `192.168.50.252:8001` | `qwen36-27b-amd-rtx3090-cuda` | `ghcr.io/ggml-org/llama.cpp:server-cuda` | `/srv/projects/llm/runtime/qwen36-27b-amd-vulkan/compose.yml` |
| `amd` | `192.168.50.252:8092` | `qwen36-27b-amd-7900xt-research` | `local/llama-vulkan-runner:ubuntu24.04` wrapping pinned llama.cpp b9536 Vulkan build | `/srv/projects/llm/runtime/qwen36-27b-amd-vulkan/compose.yml` |
| `amd` | `192.168.50.252:8091` | `kernel-cortex-embedding` | `vllm/vllm-openai-rocm:latest` | `/srv/projects/kernel-cortex/amd/compose.yml` |

Validation after migration:

- Docker health is healthy for all four containers.
- `llama-server` and `vllm` worker processes are in Docker cgroups.
- Strix `8080`, AMD `8001`, AMD `8092`, and AMD `8091` all answer
  `/v1/models`.
- Strix now serves
  `plunderstruck/Qwen3.6-27B-MTP-ROCmFP4-GGUF` file
  `Qwen3.6-27B-MTP-ROCmFP4-STRIX-imatrix-embF16-headQ6.gguf` with
  self-speculative MTP enabled, alias `qwen3.6-27b-rocmfp4-mtp`, and
  configured context `262144`.
- The previous Strix `qwen36-27b-strix-vulkan` container on `8082` was
  intentionally stopped during the self-speculative deployment.
- AMD `8091` returns an embedding vector for a smoke input.
- On 2026-06-08, Strix `8082`, AMD `8001`, and AMD `8092` were changed from
  localhost-only binds to `0.0.0.0` binds so the ThinkCentre/Open WebUI hub and
  other LAN machines can call them directly by IP address.
- No host-native `llama-server` or `vllm` runtimes were found on the known
  homelab hosts after migration.

## Host: strix

Role:

- Reasoning and validation host.
- Strix Halo vLLM validation/testbed host.
- Hosts llama.cpp Vulkan model containers that are normally part of the local
  LLM topology, but were stopped during vLLM testing in the captured snapshot.

Stable LLM services:

| Service/container | Runtime/image family | Endpoint/port | Role/purpose | Source/config path hints |
|---|---|---:|---|---|
| `qwen36-rocmfp4` | custom `rocmfp4-llama` `llama-server`, ROCm+Vulkan container | `8080` | Qwen3.6 27B ROCmFP4 MTP self-speculative research endpoint | `/srv/llm/containers/rocmfp4-llama/compose.yml` |
| `qwen3-6` | `llama.cpp` server, Vulkan container family | normally `8081` from prior validation context | Strix reasoning/smaller model endpoint | Unknown from snapshot |
| vLLM validation repo | Ubuntu Docker vLLM validation environment | validation used `8010` | vLLM validation and testing, not a stable production router | `/srv/projects/amd-strix-halo-vllm-toolboxes` |

Validation notes:

- Port `8000` on `strix` is occupied by `legacy-printer`.
- vLLM validation therefore used port `8010`.
- The `qwen3-coder` and `qwen3-6` llama.cpp Vulkan containers were stopped
  during vLLM testing in the captured snapshot. That stopped state is not part
  of the stable topology.

## Host: thinkcentre

Role:

- Services hub for the homelab LLM workflow.
- Hosts Open WebUI, model-dispatch, Hermes Agent, and LiteLLM rollback/history.

Stable LLM and adjacent services:

| Service/container | Runtime/image family | Endpoint/port | Role/purpose | Source/config path hints |
|---|---|---:|---|---|
| `open-webui` | Open WebUI container | `3000` | Browser UI for advisor/planning and model access | `/srv/openwebui/docker-compose.yml` |
| `model-dispatch` | Local Python OpenAI-compatible dispatch service | `4010` | Active Open WebUI model endpoint and local-first routing layer | `/srv/model-dispatch` |
| `litellm` | LiteLLM container | `4000` | Rollback/history endpoint, not the active Open WebUI model endpoint | `/srv/litellm/docker-compose.yml` |
| `hermes-agent` | Hermes Agent container | `localhost:8642` | Local Hermes Agent service | Unknown from snapshot |

Notes:

- Open WebUI uses `model-dispatch` as the active OpenAI-compatible model API
  surface.
- LiteLLM remains documented as rollback/history.
- Non-LLM service containers on `thinkcentre` are excluded from this topology
  unless they directly affect model routing or the LLM workflow.

## Host: AMD

Role:

- Current kernel offload and evidence-processing host.
- Hosts the fast review lane, research lane, and embedding worker used by the
  Codex Desktop dispatcher workflow.

Stable LLM services:

| Service/container | Runtime/image family | Endpoint/port | Role/purpose | Source/config path hints |
|---|---|---:|---|---|
| `qwen36-27b-amd-rtx3090-cuda` | `llama.cpp` CUDA server container | `8001` | Fast kernel diff/log triage lane | `/srv/projects/llm/runtime/qwen36-27b-amd-vulkan/compose.yml` |
| `qwen36-27b-amd-7900xt-research` | pinned `llama.cpp` Vulkan wrapper container | `8092` | Kernel research synthesis and maintainer-risk review lane | `/srv/projects/llm/runtime/qwen36-27b-amd-vulkan/compose.yml` |
| `kernel-cortex-embedding` | `vllm` OpenAI-compatible ROCm embedding worker | `8091` | Embeddings for kernel-cortex evidence retrieval | `/srv/projects/kernel-cortex/amd/compose.yml` |

Deprecated or excluded:

- Old `autocoder-*` containers on `AMD` are exited/deprecated runtime remnants.
- They are not part of the active LLM topology and should not be indexed as
  active services.
- Older AMD `8083`/`8084` coding endpoints are historical validation context,
  not the current kernel offload path. Use `scripts/kernel-token-offload
  status` before sending dispatcher work to an AMD lane.

## Exclusions for CodeGraphContext indexing

The following are intentionally excluded from this document and should not be
treated as part of the stable model topology:

- Observer logs.
- Request logs.
- Raw terminal logs.
- Docker stats output.
- Exact timestamps, uptime, health status, and daily container status churn.
- Cache directories and cache contents.
- Secrets, tokens, private account details, and environment files.
- Unrelated non-LLM containers.
- Deprecated/exited AMD autocoder containers except as explicitly excluded
  above.

This keeps the file safe for CodeGraphContext indexing and prevents CGC from
tracking daily runtime activity as if it were architecture.
