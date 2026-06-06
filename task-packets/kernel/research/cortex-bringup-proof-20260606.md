# Cortex Bringup Proof

Generated: 2026-06-06

## Services Started

ThinkCentre `192.168.50.225`:

- Qdrant container: `kernel-cortex-qdrant-1`
- Image: `qdrant/qdrant:latest`
- Binding: `127.0.0.1:6333-6334`
- Health check: `healthz check passed`

AMD `192.168.50.252`:

- Embedding container: `kernel-cortex-embedding`
- Image: `vllm/vllm-openai-rocm:latest`
- Binding: `192.168.50.252:8091->8000/tcp`
- Model: `BAAI/bge-large-en-v1.5`
- Vector size observed: `1024`
- Max model length reported by vLLM: `512`

AMD research endpoint:

- Process: `llama-server`
- Model alias: `qwen36-27b-7900xt-research`
- Binding: `127.0.0.1:8092`
- Device argument: `--device Vulkan2`

## Evidence Indexed

Staged source:

- `/srv/projects/kernel-services/cortex/ingest/a733-overlap-scan-20260606.md`

Qdrant collection:

- Name: `kernel_evidence`
- Status: `green`
- Vector size: `1024`
- Distance: `Cosine`
- Points count: `7`

## Proof Commands

Embedding probe from ThinkCentre to AMD returned:

```json
{"dimensions": 1024, "first3": [0.014111, 0.013908, 0.015355], "model": "BAAI/bge-large-en-v1.5"}
```

Default ingest command after chunk-size calibration returned:

```json
{"collection": "kernel_evidence", "indexed_chunks": 7}
```

Qdrant count returned:

```json
{"result":{"count":7},"status":"ok","time":0.000225026}
```

Semantic search query:

```text
What A733 kernel work conflicts with in-flight linux-sunxi RFCs?
```

Top result returned the research chunk naming:

- CCU/PRCM conflict with Junhui Liu's A733 CCU/PRCM RFC series.
- Pinctrl conflict with Andre Przywara's A733 pinctrl RFC series.

## Calibration Note

The first default ingest failed because `CORTEX_MAX_CHARS=3000` exceeded
`BAAI/bge-large-en-v1.5`'s 512-token model limit. The workflow defaults were
changed to:

- `CORTEX_MAX_CHARS=700`
- `CORTEX_OVERLAP=70`
- `CORTEX_BATCH_SIZE=16`

The default ThinkCentre ingest command passed after those settings were copied
to the remote service template.

## Sources

- vLLM pooling/embedding runner documentation:
  `https://docs.vllm.ai/en/v0.21.0/models/pooling_models/`
- vLLM embedding example:
  `https://docs.vllm.ai/en/latest/examples/pooling/embed/`
- linux-sunxi public-inbox source:
  `https://lore.kernel.org/linux-sunxi/0`

This proof records service bringup and retrieval behavior only. It is not a
kernel patch validation result.
