# Strix Concurrent Model Variant Comparison - 2026-05-28

Purpose: explain why Strix previously ran Qwen3.6 and Qwen3-Coder-Next at the
same time, while the current vLLM AWQ pair does not safely do so.

## Current Safe State

After the second failed concurrent vLLM attempt and reboot recovery:

- Strix is back in `tool` mode.
- Qwen3.6 AWQ vLLM is live on `8010`.
- `local/tool-test` passes through model-dispatch.
- The temporary Coder-Next direct-test container was removed.
- ThinkCentre model-dispatch remains unchanged.

## Previously Concurrent Pair

The old pair that could run at the same time used llama.cpp with Vulkan and
GGUF model files:

| Container | Image | Host port | Model |
| --- | --- | --- | --- |
| `qwen3-6` | `ghcr.io/ggml-org/llama.cpp:server-vulkan` | `8081` | `Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf` |
| `qwen3-coder` | `ghcr.io/ggml-org/llama.cpp:server-vulkan` | `8082` | `Qwen3-Coder-Next-UD-Q4_K_XL.gguf` |

Both used:

- llama.cpp server
- Vulkan backend
- GGUF files mounted under `/models`
- `-ngl 99`
- `-c 65536`
- `--flash-attn on`
- `--no-mmap`
- KV cache flags `-ctk q8_0` and `-ctv q8_0`

Their shutdown memory summaries showed they were able to coexist with
substantial free Vulkan memory:

- `qwen3-6`: about `22371 MiB` self/model/context/compute with about
  `55385 MiB` free shown in its memory breakdown.
- `qwen3-coder`: about `48415 MiB` self/model/context/compute with about
  `55385 MiB` free shown in its memory breakdown.

This does not mean they were small. It means the llama.cpp/Vulkan/GGUF harness
managed memory differently enough that the pair could coexist.

## Current Failing Pair

The current validated tool-call harness uses vLLM with AWQ Hugging Face model
packages:

| Runtime | Image | Port | Model |
| --- | --- | --- | --- |
| Qwen3.6 tool | `docker.io/kyuz0/vllm-therock-gfx1151:stable` | `8010` | `cyankiwi/Qwen3.6-35B-A3B-AWQ-4bit` |
| Coder-Next test | `docker.io/kyuz0/vllm-therock-gfx1151:stable` | tested on `8011` | `cyankiwi/Qwen3-Coder-Next-AWQ-4bit` |

These are not the same variants as the old concurrently running pair:

- Different serving harness: vLLM instead of llama.cpp.
- Different backend stack: TheRock/ROCm-style vLLM container instead of
  llama.cpp Vulkan.
- Different model packaging: Hugging Face AWQ packages instead of GGUF files.
- Different memory policy: vLLM reserves according to
  `--gpu-memory-utilization` and KV-cache planning.
- Different validated behavior goal: OpenAI-style tool calls through
  model-dispatch.

## Failed Direct Concurrent vLLM Attempts

Attempt 1:

- Qwen3.6 stayed live on `8010`.
- Coder-Next was moved to `8011`.
- Coder-Next kept `--gpu-memory-utilization 0.70`.
- vLLM refused startup because it wanted about `81.2 GiB`, while only about
  `35.08 GiB` was free.

Attempt 2:

- Coder-Next was lowered to `--gpu-memory-utilization 0.25`.
- Strix became too unresponsive for SSH and required a reboot.

Attempt 3:

- Direct-only temporary Coder-Next test on `8011`.
- No model-dispatch, Aider, Open WebUI, or repo changes.
- Coder-Next used `--max-model-len 2048` and
  `--gpu-memory-utilization 0.10`.
- The container began loading the model.
- Strix again stopped accepting SSH banner exchange and required reboot.

## Conclusion

The old fact remains true: Strix has previously run a Qwen3.6 model and a
Qwen3-Coder-Next model at the same time.

That fact does not carry over to the current vLLM AWQ tool-call harness. The
current vLLM AWQ pair is not safe to run concurrently in the tested shape, even
with a reduced Coder-Next context and low memory utilization.

## Recommended Direction

Do not retry concurrent vLLM AWQ startup with smaller numeric tweaks.

Safer next options:

1. Keep the current one-port manual mode switch for the validated vLLM
   tool-call harness.
2. If concurrent serving is required, revisit the older llama.cpp/GGUF pair as
   a separate path and test whether it can satisfy the needed Aider or tool-call
   behavior.
3. Evaluate whether one model can serve both needs instead of keeping both live.
4. Consider a separate host for the code model if simultaneous vLLM tool-call
   behavior is required.

Do not change model-dispatch or Aider to assume `local/code-test` is always
live until a stable always-live code backend is proven.
