# Kernel Cortex Service Templates

These files describe the private kernel knowledge-cortex sidecar.

Current bringup proof:

- `task-packets/kernel/research/cortex-bringup-proof-20260606.md`

They are templates only. Do not commit service data, Qdrant storage, raw crawls,
model caches, `.env` files, or logs.

Default placement:

- ThinkCentre `192.168.50.225`: Qdrant, ingestion worker, persistent storage
- AMD `192.168.50.252`: RX 7900 XT ROCm embedding endpoint
- Mac mini: Codex Desktop dispatcher only

Current service endpoints:

- ThinkCentre Qdrant: `http://127.0.0.1:6333` on `192.168.50.225`
- AMD embeddings: `http://192.168.50.252:8091/v1`
- AMD research model: `http://127.0.0.1:8092/v1` on `192.168.50.252`

Use `scripts/kernel-cortex deploy-plan` from the repo root to print the
operator-approved deployment command block.
