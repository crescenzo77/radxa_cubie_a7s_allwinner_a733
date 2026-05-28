# Local Model Role Reset - 2026-05-28

Purpose: record the decision to return Strix to the former llama.cpp/GGUF
multi-model harness and use AMD for fast agentic work plus experiments.

## Direction

Use the existing llama.cpp/GGUF containers as the default always-live local
model menu:

| Host | Alias | Container | Harness | Model | Port | Role |
| --- | --- | --- | --- | --- | --- | --- |
| Strix | `local/strix-reasoning` | `qwen3-6` | llama.cpp Vulkan | `Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf` | `8081` | long-context reasoning/review |
| Strix | `local/strix-coder` | `qwen3-coder` | llama.cpp Vulkan | `Qwen3-Coder-Next-UD-Q4_K_XL.gguf` | `8082` | always-live local code model candidate |
| AMD 3090 | `local/amd-coder` | `qwen3-coder-30b` | llama.cpp CUDA | `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` | `8083` | fast agentic coding workhorse |
| AMD 7900 XT | `local/amd-small` | `gemma4-7900xt` | llama.cpp ROCm | `google_gemma-4-26B-A4B-it-Q4_K_M.gguf` | `8084` | backup/experimental lane |

Keep the vLLM Qwen3.6 AWQ runtime as a validated tool-call harness, but do not
treat it as the default always-live Strix setup while it prevents the two-model
Strix layout.

## Why

The current vLLM AWQ Qwen3.6 runtime works for OpenAI-style tool calling, but
it reserves a large memory pool:

- model load around `23 GiB`
- KV cache reservation around `54 GiB`
- visible system memory use around `86 GiB`

That makes concurrent vLLM serving unsafe on Strix in the tested shape.

The older llama.cpp/GGUF pair previously ran together and has now been restored.
It better matches Strix's strength: large unified memory and multiple local
models available at once.

## Validation

After restoring the llama.cpp/GGUF setup:

- `qwen3-6` is healthy on Strix port `8081`.
- `qwen3-coder` is healthy on Strix port `8082`.
- `qwen3-coder-30b` is healthy on AMD port `8083`.
- `gemma4-7900xt` is healthy on AMD port `8084`.
- model-dispatch aliases tested:
  - `local/strix-reasoning` returned `ok`.
  - `local/strix-coder` returned `ok`.
  - `local/amd-coder` returned `ok`.
  - `local/amd-small` responded, but emitted reasoning text instead of clean
    content for a tiny prompt.

## Caveats

- The llama.cpp/GGUF Strix Coder-Next path has not yet been revalidated for
  Aider.
- The llama.cpp/GGUF Strix Qwen3.6 path has not yet been revalidated for clean
  OpenAI-style tool calls.
- `local/amd-small` should not be treated as a clean agent model until its
  thinking/output behavior is controlled.
- The vLLM Qwen3.6 AWQ path remains useful as a reference tool-call harness,
  but it is not the multi-model default.

## Qwen 3.7 Status

As of this checkpoint, Qwen 3.7 appears to be a proprietary/preview/API topic,
not a locally available open-weight model suitable for immediate 7900 XT
testing. Do not plan local 7900 XT testing around Qwen 3.7 until official
open weights or a concrete compatible quant are available.

Use the 7900 XT lane for newer open-weight or quantized models once a concrete
candidate exists.

## Next Work

Recommended next slices:

1. Revalidate Aider against `local/strix-coder` or the direct Strix
   llama.cpp Coder-Next endpoint.
2. Validate AMD `local/amd-coder` for the agentic workload that should run on
   the RTX 3090.
3. Pick a real open-weight 7900 XT experiment model and test it separately from
   mission-critical routes.
