# AMD Runtime Baseline

Status: native Vulkan baseline passed
Host under test: `192.168.50.252`
Operator surface: Codex Desktop only

## Current Measured Baseline

Native llama.cpp Vulkan is the first working RTX 3090 coding lane.

- Host: `192.168.50.252`
- Runtime: llama.cpp `b9536` Ubuntu Vulkan prebuilt
- GPU path: `NVIDIA GeForce RTX 3090`
- Managed by: `scripts/amd-llamacpp-native`
- Model: `unsloth/Qwen3.6-27B-GGUF`
- File: `/srv/projects/llm/models/qwen3.6-27b-gguf/Qwen3.6-27B-Q4_K_M.gguf`
- SHA256: `5ed60d0af4650a854b1755bd392f9aef4872643dc25a254bc68043fa638392a0`
- Alias: `qwen3.6-27b-q4km-amd-rtx3090-vulkan`
- Endpoint: `http://127.0.0.1:8001/v1` on `192.168.50.252` only
- Context: `32768`
- Reasoning: off
- Result file:
  `tools/bench/results/runtime-qwen36-27b-q4km-amd-rtx3090-vulkan-20260606T002947Z.jsonl`
- Result: `agent_candidate`, 6/6 cases passed

Measured summary:

- short chat: passed, about `32.4` completion tokens/sec
- stream chat: passed, TTFT about `0.29` seconds
- exact JSON: passed
- OpenAI-style tool call: passed
- long-context marker recall: passed at `32768` input characters

## Control Commands

```sh
scripts/amd-llamacpp-native status
scripts/amd-llamacpp-native fetch-runtime
scripts/amd-llamacpp-native fetch-qwen36
scripts/amd-llamacpp-native start
scripts/amd-llamacpp-native bench --warmup --long-chars 32768
```

The endpoint is loopback-only on `192.168.50.252`. Codex Desktop reaches it by
running the benchmark over SSH to `192.168.50.252`.

## Next Comparisons

- llama.cpp CUDA build, if built locally or packaged cleanly.
- TabbyAPI/ExLlamaV2 with an EXL2 quant around 4.5 bpw.
- `Q5_K_M` only if it leaves enough VRAM for the needed context.
- LAN-visible gateway exposure only after the local loopback lane remains
  stable under the validation loop.
