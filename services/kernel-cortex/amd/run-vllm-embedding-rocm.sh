#!/usr/bin/env bash
set -euo pipefail

host="${AMD_EMBEDDING_HOST:-192.168.50.252}"
port="${AMD_EMBEDDING_PORT:-8091}"
model="${EMBEDDING_MODEL:-BAAI/bge-large-en-v1.5}"
image="${VLLM_ROCM_IMAGE:-vllm/vllm-openai-rocm:latest}"
rocr_visible_devices="${ROCR_VISIBLE_DEVICES:-0}"
hip_visible_devices="${HIP_VISIBLE_DEVICES:-0}"
pytorch_rocm_arch="${PYTORCH_ROCM_ARCH:-gfx1100}"

exec docker run --rm \
  --name kernel-cortex-embedding \
  --group-add=video \
  --group-add=render \
  --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined \
  --device=/dev/kfd \
  --device=/dev/dri \
  --ipc=host \
  -p "${host}:${port}:8000" \
  -v /srv/projects/kernel-cortex/cache/huggingface:/root/.cache/huggingface \
  -e "ROCR_VISIBLE_DEVICES=${rocr_visible_devices}" \
  -e "HIP_VISIBLE_DEVICES=${hip_visible_devices}" \
  -e "PYTORCH_ROCM_ARCH=${pytorch_rocm_arch}" \
  "${image}" \
  "${model}" \
  --runner pooling \
  --convert embed \
  --host 0.0.0.0 \
  --port 8000
