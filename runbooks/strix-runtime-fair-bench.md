# Strix Runtime Fair Benchmark

Status: native Vulkan baseline passed
Host under test: `192.168.50.11`
Operator surface: Codex Desktop only

## Purpose

Use this bench to choose the best Strix runtime for long-context review and
agent-facing local inference.

The comparison is runtime-focused. It must use the same model file,
quantization, context length, prompts, max output tokens, and concurrency for
each tested runtime.

## Candidate Runtime Order

1. Native llama.cpp Vulkan.
2. Containerized llama.cpp Vulkan.
3. Native llama.cpp CPU or partial-offload fallback.
4. ROCm/HIP only if it becomes competitive or solves a concrete Vulkan blocker.

Vulkan is first-class on Strix. ROCm is not required unless Vulkan fails on
speed, long context, API behavior, or agent compatibility.

## Current Measured Baseline

Native llama.cpp Vulkan is the first working Strix lane.

- Host: `192.168.50.11`
- Runtime: llama.cpp `b9536` Ubuntu Vulkan prebuilt
- GPU path: `Radeon 8060S Graphics (RADV STRIX_HALO)`
- Managed by: `scripts/strix-llamacpp-native`
- Model: `unsloth/Qwen3.6-27B-GGUF`
- File: `/srv/projects/llm/models/qwen3.6-27b-gguf/Qwen3.6-27B-Q4_K_M.gguf`
- SHA256: `5ed60d0af4650a854b1755bd392f9aef4872643dc25a254bc68043fa638392a0`
- Alias: `qwen3.6-27b-q4km-native-vulkan`
- Endpoint: `http://127.0.0.1:8082/v1` on `192.168.50.11` only
- Context: `65536`
- Reasoning: off
- Result file:
  `tools/bench/results/strix-runtime-qwen36-27b-q4km-native-vulkan-20260606T001323Z.jsonl`
- Result: `agent_candidate`, 6/6 cases passed

Measured summary:

- short chat: passed, about `11.4` completion tokens/sec
- stream chat: passed, TTFT about `0.44` seconds
- exact JSON: passed
- OpenAI-style tool call: passed
- long-context marker recall: passed at `65536` input characters

This does not prove maintainer-grade reasoning. It proves the Strix native
Vulkan lane is compatible enough to use as a serious reviewer/backend candidate.

## Fairness Rules

- Run exactly one Strix model server during each benchmark.
- Use the same GGUF/model artifact for every runtime.
- Use the same context length, batch settings, and prompt set.
- Bind the tested server to Strix loopback unless remote access is explicitly
  being measured.
- Run the benchmark from Codex by streaming the bench script over SSH to Strix.
- Do not use Mac containers.
- Do not compare a warmed runtime against a cold runtime; use the same warmup
  setting for every run.
- Keep raw JSONL output for every run.

## Benchmark Command

Start and inspect the managed native Vulkan lane from Codex Desktop:

```sh
scripts/strix-llamacpp-native status
scripts/strix-llamacpp-native fetch-qwen36
scripts/strix-llamacpp-native start
scripts/strix-llamacpp-native bench --warmup --long-chars 65536
```

The default benchmark target is an OpenAI-compatible endpoint local to
`192.168.50.11` at
`http://127.0.0.1:8082/v1`:

```sh
scripts/strix-runtime-bench \
  --warmup \
  --long-chars 65536
```

Native Vulkan example:

```sh
STRIX_BENCH_TARGET=native-llamacpp-vulkan \
STRIX_BENCH_BASE_URL=http://127.0.0.1:8082/v1 \
scripts/strix-runtime-bench --warmup --long-chars 65536
```

Containerized Vulkan example:

```sh
STRIX_BENCH_TARGET=container-llamacpp-vulkan \
STRIX_BENCH_BASE_URL=http://127.0.0.1:8083/v1 \
scripts/strix-runtime-bench --warmup --long-chars 65536
```

CPU fallback example:

```sh
STRIX_BENCH_TARGET=native-llamacpp-cpu \
STRIX_BENCH_BASE_URL=http://127.0.0.1:8084/v1 \
scripts/strix-runtime-bench --warmup --long-chars 65536
```

Results are written locally under:

```text
tools/bench/results/
```

## Cases Measured

- `/v1/models` health and selected model.
- Short non-streaming chat latency and completion throughput.
- Streaming chat TTFT and output character rate.
- JSON instruction following.
- OpenAI-style tool-call behavior.
- Long-context prompt handling with a digest marker.

## Interpretation

The summary record includes `agent_grade`:

- `agent_candidate`: chat, tool call, JSON, and long-context cases passed.
- `agent_candidate_json_weak`: tool calls work, but JSON reliability needs work.
- `agent_candidate_long_context_weak`: basic agent behavior works, but long
  context failed.
- `review_only_no_tool_calls`: useful for review/summarization, but not for
  tool-call agents.
- `blocked_no_chat`: not usable as an OpenAI-compatible runtime.

If Vulkan lands in `review_only_no_tool_calls`, it can still be useful for
Strix semantic review. It should not be promoted to an agent tool-loop backend
unless the intended agent does not require tool calls.
