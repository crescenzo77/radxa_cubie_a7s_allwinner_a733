# Local AI Mainline Coding Stack

Date: 2026-06-05

Purpose: define the current practical state of tools, models, agents,
harnesses, skills, hooks, and local hardware roles for doing A733/Cubie A7S
Linux kernel work at a standard that could survive maintainer review.

This is not a promise that local AI can produce accepted kernel patches
unsupervised. It is a design for using local AI without letting it create
unreviewable, overclaimed, or process-invalid work.

## Executive Assessment

The best local setup is not a fully autonomous "AI kernel maintainer." The best
setup is a constrained local engineering cell:

- Codex Desktop as the only operator-facing dispatcher
- one fast coding endpoint on the RTX 3090
- one long-context semantic review endpoint on Strix Halo
- optional secondary review and retrieval services on the 7900 XT
- deterministic routing, not an LLM dispatcher
- command-line coding agents only
- custom hooks that prevent dirty candidate work from advancing
- MCP servers that expose narrow kernel-specific tools instead of arbitrary
  shell access
- a human gate for sign-off, evidence acceptance, and final submission
- no Docker Desktop or containerized inference on the Mac Mini by default

The local models can investigate, draft, refactor, summarize logs, propose patch
splits, and run validation loops. They should not decide that a patch is
mainline-ready. That decision remains human because the Linux process depends
on technical judgment, DCO responsibility, review etiquette, and narrow claims.

Throughout this document, a local `PASS` means only that a recorded command
returned exit code 0 under the captured environment. It does not mean that a
patch is mainline-ready or maintainer-approved. The intended output of this
stack is a patch candidate packet:

- a small, reviewable diff
- proof logs with exact commands and hashes
- provenance for any tool-generated content
- subsystem and maintainer routing evidence
- semantic rejection risks
- a hard stop for human ownership

## Kernel Process Boundary

The pipeline must be designed as a reproducible patch-candidate factory, not an
autonomous maintainer simulator.

Non-negotiable process rules:

- AI agents must not add `Signed-off-by:` trailers.
- AI agents must not add `Reviewed-by:`, `Acked-by:`, `Tested-by:`, or similar
  human authority trailers.
- AI agents must not send email or create public submissions.
- AI agents must not declare a patch mainline-ready.
- A human must review, understand, and be able to defend every submitted change.
- A human must decide whether and how to disclose AI/tool assistance, including
  any `Assisted-by:` trailer or cover-letter disclosure.

The stack should preserve enough information to support transparent disclosure:

- model and quantization used
- agent or harness used
- specialized tools used beyond ordinary build tools
- prompt summary or prompt digest
- files and portions affected by tool-generated output
- proof logs for validation and testing

If the human operator cannot explain why the resulting code is correct, the
pipeline must stop. Passing local tools is not a substitute for understanding.

## Hardware Roles

### `192.168.50.248`: Framework laptop

Use this as the physical hands-on client only.

Role:

- keyboard, display, browser, and Chrome Remote Desktop client
- no model serving requirement
- no dispatcher logic requirement
- no kernel validation burden unless explicitly chosen later

The operator sits at the Framework laptop, but the actual orchestration surface
is Codex Desktop running through the Mac remote session.

### `192.168.50.164`: Mac Mini, Apple M4, 16 GB unified memory

Use this as the Codex Desktop dispatcher and document/control-plane workspace.

Recommended role:

- run Codex Desktop
- hold orchestration scripts and runbooks
- SSH into `192.168.50.252`, `192.168.50.11`, and `192.168.50.225`
- collect benchmark and proof-log artifacts
- coordinate deterministic routing decisions

Do not use the Mac Mini for Docker Desktop, validation containers, or sustained
LLM serving by default. It has limited headroom and is already the interactive
control surface. If a Mac-side container ever becomes necessary, treat that as a
separate design decision and compare Colima, a Linux VM, and moving the work to
a Linux host before proceeding.

### `192.168.50.225`: ThinkCentre Ubuntu headless service host

Use this as the low-power Linux service/control-plane candidate.

Recommended role:

- deterministic gateway or proxy host, if a LAN-visible gateway is needed
- proof-log index, dashboard, or lightweight coordination service
- container host for non-GPU services
- not a serious LLM inference host

This is the preferred place for always-on lightweight Linux services because it
does not steal memory or thermal headroom from the Mac dispatcher or GPU hosts.

### `192.168.50.252`: AMD rig, Ryzen 9 7900X, RTX 3090, Radeon 7900 XT

Use this as the fast coding and validation node.

Recommended RTX 3090 role:

- primary coding model endpoint
- fast patch drafting and refactoring
- compiler-error repair
- short to medium context repo work
- agent edit loop backend

Recommended Radeon 7900 XT role:

- secondary reviewer endpoint
- embedding and reranking service
- spare local model endpoint for benchmark comparisons
- log summarizer or evidence classifier

Do not make the 7900 XT an LLM dispatcher. Dispatch should be deterministic:
task type, context size, required latency, and failure history should choose the
endpoint. A model deciding which model should receive work adds latency,
failure modes, and unreviewable delegation logic.

### `192.168.50.11`: Strix Halo desktop, AMD Strix Halo Max+ 395, 128 GB LPDDR5

Use this as the long-context semantic review and investigation node.

Recommended Strix role:

- one large-context model only
- repository and documentation investigation
- vendor/BSP comparison
- evidence matrix review
- patch split review
- cover letter review
- UART log and failure analysis
- "would a maintainer reject this?" review
- UART capture host for the Cubie A7S boards

Do not optimize Strix for fast token generation. Its value is memory capacity,
not throughput. Treat it as the patient reviewer that can hold more context,
not the machine that should hammer out edits.

## Immediate Board Targets

The most immediate kernel work is for two Radxa Cubie A7S devices:

- `cubie2`: `192.168.50.85`
- `cubie3`: `192.168.50.95`

Both boards have UART connections to `192.168.50.11`.

Observed on `192.168.50.11`:

- `/dev/ttyUSB0`
- `/dev/ttyUSB1`
- `/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0`
  points to `/dev/ttyUSB1`

Do not assume the serial-device mapping until it is confirmed by capturing boot
output from one board at a time.

There are two Wi-Fi home automation switches formerly used for Cubie power
down/power on control. Do not automate those switches until their IPs, control
API, and switch-to-board mapping are confirmed. Any power action must require
explicit human approval and must be logged as hardware evidence.

## Model Placement

### Baseline Model: Qwen3.6-27B

Use Qwen3.6-27B as the first serious baseline across the stack.

Reasons:

- official model card identifies it as a 27B model
- hybrid layout includes Gated DeltaNet and Gated Attention layers
- native context length is listed as 262,144 tokens, extensible to 1,010,000
  tokens
- official usage notes include vLLM, SGLang, KTransformers, Transformers, and
  quantized routes for llama.cpp/Ollama/LM Studio-compatible setups
- official notes include tool-call parser support and MTP/speculative decoding
  options for vLLM/SGLang
- benchmark table reports strong agentic coding results, including
  SWE-bench-style and terminal-task scores

This should be the first model tested because it is the best fit for your
stated goal: local agentic coding with large context, tool use, and enough
coding ability to be useful on real repositories.

### RTX 3090 Recommended Model

Measured operational baseline:

- `Qwen3.6-27B`
- quantization: GGUF `Q4_K_M`
- runtime: native llama.cpp Vulkan
- host: `192.168.50.252`
- model file:
  `/srv/projects/llm/models/qwen3.6-27b-gguf/Qwen3.6-27B-Q4_K_M.gguf`
- SHA256:
  `5ed60d0af4650a854b1755bd392f9aef4872643dc25a254bc68043fa638392a0`
- endpoint: `http://127.0.0.1:8001/v1` on `192.168.50.252` only
- manager script: `scripts/amd-llamacpp-native`
- GPU selector: `GGML_VK_VISIBLE_DEVICES=1`
- context tested: `32768`
- result: fair bench `agent_candidate`, 6/6 cases passed
- expected role: fast coding agent backend

Use this native Vulkan endpoint as the first measured fast-coding baseline. It
is not necessarily the final fastest runtime, but it is already usable enough to
anchor the next orchestration work.

Follow-up speed experiments:

- EXL2 4.5 bpw if a high-quality quant exists and tool calling is reliable
- GGUF `Q4_K_M` if EXL2 behavior is unstable
- GGUF `Q5_K_M` only if it still leaves enough room for the required context
- llama.cpp CUDA or TabbyAPI/ExLlamaV2 if they beat the Vulkan baseline without
  degrading JSON, tool-call, or validation-loop behavior

Do not try to run raw FP8 weights on the RTX 3090. A 27B 8-bit weight load is
larger than 24 GB before runtime overhead. FP8 KV cache or activation settings
can help memory pressure, but they are not the same as fitting unquantized FP8
weights.

Practical context target:

- 32K proven for routine coding
- 64K only after memory and prompt-ingestion behavior are measured
- benchmark 96K or higher only after confirming VRAM, TTFT, and tool-call
  reliability

### Strix Recommended Model

Measured operational baseline:

- `Qwen3.6-27B`
- quantization: GGUF `Q4_K_M`
- runtime: native llama.cpp Vulkan
- model file:
  `/srv/projects/llm/models/qwen3.6-27b-gguf/Qwen3.6-27B-Q4_K_M.gguf`
- SHA256:
  `5ed60d0af4650a854b1755bd392f9aef4872643dc25a254bc68043fa638392a0`
- endpoint: `http://127.0.0.1:8082/v1` on Strix only
- manager script: `scripts/strix-llamacpp-native`
- context tested: `65536`
- result: fair bench `agent_candidate`, 6/6 cases passed
- expected role: long-context investigation and semantic review

Start operational work with the measured `Q4_K_M` Vulkan lane. It passed health,
short chat, streaming, exact JSON, OpenAI-style tool call, and 65K-character
long-context marker recall.

Treat `Q5_K_M`, `Q6_K`, and `Q8_0` as follow-up quality experiments, not as the
first dependency. Move upward in quantization only if benchmark results show a
real review-quality gain and prompt-ingestion latency remains acceptable. The
likely bottleneck on Strix is memory bandwidth and prompt ingestion, so higher
precision may cost more latency than it returns in quality.

Practical context target:

- 64K as the first proven target
- 96K to 128K as the next long-context target
- 192K to 262K only after TTFT and stability are acceptable
- do not assume 1M context is useful just because the model architecture allows
  it

### Radeon 7900 XT Recommended Model

Use the 7900 XT as an auxiliary model host, not the core loop.

Recommended uses:

- a smaller code reviewer model
- Qwen3.6-27B GGUF `Q4_K_M` with partial offload, if stable
- embeddings and reranking
- benchmark comparison against the 3090 endpoint

Do not rely on the 7900 XT for the primary coding loop unless ROCm/HIP/Vulkan
runtime stability is proven on the exact model and harness. NVIDIA remains the
lower-friction path for fast single-GPU coding inference.

### DeepSeek V4-Flash

Treat DeepSeek V4-Flash as an experiment, not the default.

Why:

- third-party sources describe it as 284B total / 13B active MoE with a very
  large context window
- reported checkpoint size is around 160 GB, which does not fit raw in Strix
  memory
- quantized forms may fit, but prompt ingestion and MoE routing on unified
  memory are not proven for this workload
- maintainer-grade kernel work needs reliable tool use and precise evidence,
  not just attractive benchmark numbers

Test it only after Qwen3.6-27B is baselined. If it wins on semantic review,
make it a reviewer. Do not make it the first production agent backend.

### Agent and Model Update as of 2026-06-04

The newer model and agent landscape changes the benchmark matrix, not the core
architecture.

Keep:

- Codex Desktop as dispatcher/operator surface
- deterministic routing and proof logs
- Qwen3.6-27B as the first local baseline
- human stop gate before candidate promotion or trailers

Add to benchmarks:

- `gpt-oss-20b` as a local open-weight reasoning/tool-use challenger because
  it targets roughly 16 GB-class hardware and agentic use
- `gpt-oss-120b` only as a future Strix/CPU-memory experiment because its
  footprint is much larger
- DeepSeek V4-Flash/V4-Pro only through an explicit API-backed advisory lane,
  not as local default inference
- Gemini CLI, Qwen Code, OpenCode, and similar terminal agents as harness
  challengers, never as independent dispatchers
- overeager-agent and token-usage failure tests in the harness benchmark suite

The most important research lesson is that more capable agents can still do
out-of-scope work. The pipeline therefore needs tighter scope gates, narrower
tool access, and proof-log enforcement as model capability increases.

## Runtime Stack

### Best Default Runtime Mix

Use multiple runtimes because the hardware is heterogeneous:

- RTX 3090: TabbyAPI/ExLlamaV2 for EXL2 speed, or llama.cpp CUDA for GGUF
- Strix: native llama.cpp Vulkan first, then containerized Vulkan or
  KTransformers only if benchmarks justify the added complexity
- 7900 XT: llama.cpp HIP/Vulkan for GGUF and embedding workloads
- gateway: LiteLLM, llama-swap, or Olla as a deterministic front door on a
  Linux host if/when LAN-visible routing is needed

Expose every model through an OpenAI-compatible `/v1` endpoint where possible.
Most command-line agents can consume that shape, and it reduces harness-specific
configuration.

Current Strix implementation:

```text
Codex Desktop on mac-mini
  -> SSH to 192.168.50.11
  -> scripts/strix-llamacpp-native
  -> llama.cpp b9536 Vulkan
  -> 127.0.0.1:8082/v1 on 192.168.50.11
```

This keeps the Mac container-free and keeps Codex Desktop as the dispatcher
while still letting Strix run the actual model workload.

Current RTX 3090 implementation:

```text
Codex Desktop on mac-mini
  -> SSH to 192.168.50.252
  -> scripts/amd-llamacpp-native
  -> llama.cpp b9536 Vulkan
  -> 127.0.0.1:8001/v1 on 192.168.50.252
```

This gives the coding lane a measured local baseline before introducing
TabbyAPI, ExLlamaV2, CUDA builds, or LAN-visible gateway routing.

### Runtime Ranking

1. TabbyAPI/ExLlamaV2

Best for fast single-NVIDIA-GPU EXL2 inference. Use it for the RTX 3090 coding
endpoint if the quant is good and the harness can consume the chat template
cleanly.

2. llama.cpp / llama-server

Best cross-platform baseline. Use it for GGUF on Strix, the Radeon 7900 XT, and
fallback RTX 3090 runs. It is the safest runtime for heterogeneous hardware and
quantization experiments.

On Strix, native llama.cpp Vulkan is already proven with Qwen3.6-27B `Q4_K_M`
at 65K context. Treat containerized Vulkan, ROCm/HIP, and higher quants as
follow-up comparisons against this baseline.

3. SGLang

Strong option for Qwen3.6 when using official tool-call parser and MTP support.
It may be better than llama.cpp for full-precision or server-style Qwen3.6
experiments, but benchmark single-machine fit before committing to it.

4. vLLM

Excellent high-throughput server with OpenAI-compatible APIs and quantization
support. For your 3090, it is useful only if the chosen quantized model,
context length, and KV-cache settings fit. Official Qwen3.6 examples for full
context assume multi-GPU tensor parallelism, so single-3090 results must be
measured rather than assumed.

5. Ollama

Good for quick smoke tests and easy local API compatibility. Not the best
primary runtime for maintainer-grade automation because context length,
quantization details, and tool-call behavior can be less explicit. If used with
OpenHands or other large-prompt agents, set context length deliberately.

## Gateway and Routing

Use deterministic routing. Do not use an LLM as the dispatcher.

Current dispatcher:

- Codex Desktop on the Mac Mini
- local scripts in the homelab repo
- SSH to headless Linux machines
- proof logs and benchmark outputs collected back into the Codex workspace

Optional future front door:

- host on `192.168.50.225` or `192.168.50.252`, not Docker Desktop on the Mac
- use LiteLLM, llama-swap, Olla, or a small custom router only if it makes the
  Codex workflow simpler
- keep routing rules deterministic and version controlled

Possible route names:

- `qwen36-27b-fast`
- `qwen36-27b-long`
- `qwen36-27b-review`
- `gpt-oss-20b-local-test`
- `embed-code`
- `rerank-code`

Routing rules should be simple:

- edit task under 64K context: RTX 3090 fast endpoint
- semantic review over 64K context: Strix long endpoint
- evidence extraction from logs: Strix long endpoint
- style or typo pass: RTX 3090 fast endpoint
- second opinion: 7900 XT endpoint
- embeddings/reranking: 7900 XT or CPU service

The gateway should log:

- model selected
- context size
- prompt token count
- TTFT
- output tokens/sec
- tool-call validity
- whether the agent needed retry
- whether validation later passed

Those logs are how the stack improves. A model-dispatcher would hide the most
important failure data.

## Agent and Harness Recommendations

### Primary Editing Agent: Aider

Use Aider as the first production editing harness.

Why:

- terminal-native
- git-aware
- works with local and cloud models
- builds a repository map
- can run tests and lint commands
- mature enough for surgical edits

Kernel-specific rule:

- do not allow automatic commits into the candidate branch
- use scratch branches
- inspect every diff before promotion
- run hooks after every edit loop

Aider is not perfect, but it is the most practical baseline for small, reviewable
kernel patch edits.

### Best Experimental Harness: Pi Coding Agent

Use Pi for custom two-agent loops and workflow experiments.

Why:

- terminal-first
- built around agent runtime, tool calling, sessions, and extensibility
- supports multiple providers through its model layer
- has package/skill-style extension potential

Use Pi when you want:

- planner/coder/reviewer loops
- reusable kernel workflow packages
- structured task queues
- custom tools and state

Do not make Pi the mainline candidate writer until its local-model behavior is
benchmarked against Aider on the exact kernel tasks.

### Strong General CLI Agent: OpenCode

Use OpenCode as a second benchmark harness.

Why:

- terminal-native
- model-agnostic
- supports many providers and local endpoints
- can plan, edit, run terminal commands, and use MCP ecosystem tooling

Use it for:

- larger task exploration
- alternate edit loop comparisons
- MCP integration testing
- multi-session experiments

Do not let it bypass the same candidate-branch gates used for Aider.

### Qwen Code

Use Qwen Code as a serious candidate when the backend model is Qwen.

Why:

- designed around Qwen models
- terminal-first
- supports OpenAI-compatible providers
- includes agentic workflow features such as skills/subagents

Main risk:

- it may be optimized around hosted Qwen workflows and authentication paths
  rather than your exact local endpoints

Benchmark it with Qwen3.6-27B before deciding whether it beats Aider/OpenCode
for kernel work.

### OpenHands

Do not use OpenHands as the default production harness.

Use it only as a sandboxed benchmark for large autonomous tasks.

Reasons:

- it needs a powerful model
- its own docs warn local/open-weight models vary in tool-use reliability
- it has more orchestration overhead than is needed for small kernel patch
  slices
- malformed JSON/tool calls can waste time
- a headless autonomous kernel pipeline is too easy to over-trust

OpenHands is useful for stress-testing local models. It is not the right first
choice for maintainer-grade candidate patch preparation.

### SWE-agent

Use SWE-agent for benchmark-style experiments, not production kernel bring-up.

Its own docs warn that small or local models are unlikely to perform well. It
is valuable for measuring agent behavior on issue-like tasks, but the A733 work
is hardware bring-up plus upstream process discipline, not a normal GitHub bug
fix.

### Claude Code, Codex Desktop, and Local Models

Do not make Claude Code or a local-model shim inside Codex the default
local-only model stack.

Claude Code can sometimes be pointed at local or proxy endpoints, but the
cleanest local workflows still belong to agents designed for bring-your-own
model operation. Proxying Claude Code through Anthropic-compatible or
OpenAI-compatible shims adds another compatibility layer that can fail silently.

Codex Desktop is excellent as the dispatcher and operator interface. In this
design, Codex does not need to become a local model runtime. It runs the control
scripts, opens SSH sessions, starts/stops endpoints, launches benchmarks,
collects logs, edits runbooks, and keeps the human in the loop. Local models
remain behind explicit OpenAI-compatible endpoints and harness scripts.

For this project, prefer:

1. Codex Desktop as dispatcher/operator surface
2. Aider as first production edit harness
3. Pi for custom loop experiments
4. OpenCode as a second benchmark harness
5. Qwen Code as a Qwen-specific challenger
6. OpenHands only as benchmark/stress harness
7. SWE-agent only as benchmark harness

## Recommended Two-Agent Loop

Use a two-agent loop, but keep the orchestrator deterministic.

### Agent A: Investigation and Review

Runs on Strix.

Model:

- Qwen3.6-27B `Q4_K_M` native llama.cpp Vulkan as the measured baseline
- later `Q5_K_M`, `Q6_K`, or `Q8_0` only if benchmarked quality justifies it

Allowed work:

- read candidate patches
- inspect evidence matrix
- summarize vendor/reference evidence
- compare with mainline precedent
- review commit messages
- review cover letters
- analyze UART logs
- identify likely maintainer objections

Not allowed:

- direct writes to candidate branch
- adding trailers
- declaring a patch accepted

### Agent B: Coding and Repair

Runs on RTX 3090.

Model:

- Qwen3.6-27B EXL2 4.5 bpw or GGUF `Q4_K_M` / `Q5_K_M`

Allowed work:

- edit one small slice
- fix compiler warnings
- clean formatting
- adjust DTS/schema issues
- draft commit-message alternatives

Not allowed:

- broad refactors
- mixed-subsystem changes
- public candidate commits without human review
- changing evidence records to fit code

### Deterministic Orchestrator

This can be a shell script, Pi package, Make target, or small Python service.

It should:

1. assign task type to endpoint
2. create scratch branch
3. run agent edit loop
4. run hooks
5. ask Strix reviewer to inspect the result
6. write a structured result
7. stop for human promotion

The orchestrator should never say "mainline ready." It can only say which gates
passed and which evidence exists.

## Patch Intent and Context Gate

Before any model edits code, require a human-readable patch intent record. This
is Phase 0 for every task, even if the change looks trivial.

Required intent fields:

- problem statement
- affected subsystem
- expected maintainer tree or route
- base commit
- target files
- evidence sources
- hardware affected
- user-visible or ABI impact, if any
- whether this is one patch or part of a series
- explicit non-goals

The orchestrator should reject work that starts from a vague request such as
"clean this up" or "make support better." Kernel patches need a narrow claim:
fix this warning, document this compatible, disable this unsupported node, add
this proven clock, or make this one behavior match the hardware evidence.

### Context Assembly Policy

Do not use a hard "50 lines only" rule. It protects context length but can
produce plausible wrong patches. Use bounded, evidence-based context instead.

For C changes, include as needed:

- the full modified function
- relevant structs, enums, and macros
- direct callers and callees
- Kconfig and Makefile context
- nearby subsystem style
- recent git history for the touched file
- relevant documentation

For Devicetree changes, include as needed:

- the changed node and parent bus
- referenced clocks, resets, pinctrl, regulators, interrupts, and PHYs
- applicable binding schema
- existing board DTS precedent
- compatible-string documentation status
- boot log or hardware evidence supporting enabled nodes

The context should be small enough to keep the coding task direct, but complete
enough that the model cannot invent missing hardware or subsystem facts. If the
required context is too large or uncertain, route the task to Strix for
investigation before allowing an edit.

## Built-In Verification Harness

The stack needs a verification harness that forces the local model to confront
actual terminal output. A model must never be allowed to claim that
`checkpatch.pl`, `dtbs_check`, `dt_binding_check`, or a build passed because it
"expects" them to pass.

The verification harness should sit between every coding agent and promotion to
candidate work.

### Verification Loop

Use this loop for every agent-produced diff:

1. Agent edits a scratch branch.
2. Harness records branch, base commit, patch range, model, harness, endpoint,
   and task ID.
3. Harness accepts only unified diffs or ordinary git working-tree changes in
   an allowlisted path set for the task.
4. Harness rejects binary changes, generated build artifacts, private paths, and
   edits outside the declared patch intent.
5. Harness runs whitelisted validation commands.
6. Harness captures raw stdout, raw stderr, exit code, command, environment,
   working directory, start time, end time, and tool versions.
7. Harness writes a proof log with a content hash.
8. Harness feeds the relevant terminal output back to the coding model.
9. If the command failed, the model may attempt the smallest repair.
10. If the command passed, the model may summarize the result, but the proof log
   remains the authority.
11. Strix reviewer receives the diff and proof logs for semantic review.
12. Human gate decides whether the result may move toward a candidate branch.

The agent is not the verifier. The harness is the verifier.

### Required Proof Commands

Run the smallest relevant set, but do not skip a relevant command because it is
slow.

Patch mechanics:

- `git diff --check <base>..HEAD`
- `git format-patch --base=auto --cover-letter -o outgoing/ <base>..HEAD`
- `git am` of the formatted series onto a fresh branch at the recorded base
- `scripts/checkpatch.pl --strict` on the formatted patch files
- `scripts/get_maintainer.pl` on the formatted patch files for routing evidence

Devicetree:

- `make dt_binding_check` for changed bindings
- `make dtbs_check` for affected DTS/DTB targets
- targeted DTB build for the affected board
- compatible-string documentation check for any new or changed compatible
- schema ordering and license check for new or modified bindings

C driver or subsystem code:

- relevant object build
- relevant directory build where practical
- relevant `ARCH=arm64` build target
- `W=1` build for changed C code
- sparse or other static analysis when practical
- `=y`, `=m`, and `=n` config coverage for touched Kconfig symbols when
  feasible

Documentation, Kconfig, and ABI:

- `make htmldocs` or targeted documentation build for documentation changes
- Kconfig menu/default review for new or changed options
- `Documentation/ABI/` coverage for new userspace-visible interfaces
- `linux-api` routing note for userspace API changes

Hardware claims:

- build artifact hashes
- DTB hash
- kernel command line
- UART log capture
- board ID
- exact observed endpoint, such as "booted to initramfs"

### Proof Log Format

Each proof log should be a plain text or JSON file containing:

- proof ID
- task ID
- model name and quantization
- agent/harness name
- runtime endpoint
- kernel tree path
- Linux tree URL
- base commit
- branch
- patch range
- container image digest
- compiler version
- dtschema version, when applicable
- dtc version, when applicable
- sparse version, when applicable
- prompt digest or prompt summary for tool-generated edits
- command
- working directory
- environment variables that affect the result
- tool versions
- start timestamp
- end timestamp
- exit code
- raw stdout
- raw stderr
- result: `PASS`, `FAIL`, or `MISSING`
- log hash

Only the verification harness may write `PASS`. If a command emits warnings,
the result is `FAIL` until a human records a specific false-positive
justification.

### Forced Ingestion

The local model must ingest actual terminal output, not a hand-written summary.
For very large logs, the harness may provide a truncated diagnostic excerpt to
the model, but the full raw stdout and stderr must remain in the proof log.
Truncation is a context-management layer, not the evidence record.

For failures, feed back:

- exact command
- exit code
- relevant stdout/stderr excerpt
- full proof-log path
- instruction to fix only the failing issue
- count of suppressed repeated diagnostics, if log truncation occurred

For passes, feed back:

- exact command
- exit code
- proof-log path
- log hash
- warning count

The model's follow-up response must cite the proof ID when it claims a check
passed or failed. A response without a proof ID is treated as an unverified
claim.

### Verification MCP Tools

Expose verification as narrow MCP tools or harness commands, not as a general
shell.

Recommended tools:

- `verify_diff_whitespace`
- `verify_format_patch`
- `verify_git_am_fresh`
- `verify_checkpatch_strict`
- `verify_dt_binding_check`
- `verify_dtbs_check`
- `verify_arm64_build`
- `verify_object_build`
- `verify_sparse`
- `verify_uart_boot_log`
- `verify_artifact_hashes`

Each tool should:

- run exactly one class of check
- emit raw terminal output
- store a proof log
- return proof ID, exit code, result, and log path
- refuse to run from a dirty candidate tree unless the task is explicitly in a
  scratch branch

### Failure Policy

The coding agent may retry a failing check only when the repair scope is small
and explicit. Examples:

- checkpatch whitespace warning
- missing binding property description
- DTS property order error
- compiler warning caused by the current patch

The agent must stop and request human review for:

- subsystem placement uncertainty
- unexplained hardware value
- probe/reset/clock sequencing uncertainty
- any fix requiring a broader patch split
- failures that persist after two repair attempts
- conflicting evidence

The goal is not to make the agent pass checks at any cost. The goal is to make
the exact failure visible before it can become fake progress.

## MCP Server Setup

Use fewer MCP servers with tighter contracts. MCP should make agents safer and
more reproducible, not more powerful in vague ways.

### Recommended MCP Servers

1. `kernel-tree-readonly`

Purpose:

- expose read-only kernel source, `MAINTAINERS`, docs, git log, git blame,
  grep, ctags/cscope/LSP query results

Rules:

- no writes
- no shell
- no network
- return file hashes with reads

2. `evidence-ledger`

Purpose:

- store evidence matrix rows
- link claims to source paths, commits, datasheet pages, UART logs, and runtime
  hashes

Rules:

- structured records only
- every row has confidence and source
- writes require branch/series ID

3. `build-validate`

Purpose:

- run whitelisted validation commands
- return structured logs

Allowed commands:

- `git diff --check`
- `scripts/checkpatch.pl --strict`
- `make dt_binding_check`
- `make dtbs_check`
- selected `ARCH=arm64` builds
- selected object builds
- `git am` into a fresh branch

Rules:

- no arbitrary shell
- no hidden `|| true`
- every result is `PASS`, `FAIL`, or `MISSING`
- logs include base commit and patch range
- logs include raw stdout, raw stderr, exit code, command, and log hash
- agents receive proof IDs, not informal pass/fail summaries

4. `hardware-lab`

Purpose:

- manage UART capture, TFTP artifact staging, board reset, and power switch
  events

Rules:

- default read-only UART mode
- power/reset actions require explicit human confirmation unless running in a
  dedicated test window
- log image hash, DTB hash, command line, board ID, and timestamp

5. `patch-series`

Purpose:

- format patches
- extract subjects and diffstats
- run recipient checks
- create cover-letter checklist

Rules:

- cannot send email
- cannot add `Signed-off-by`
- cannot add `Assisted-by`
- cannot add `Reviewed-by`, `Acked-by`, or `Tested-by` without explicit
  recorded source
- may prepare a provenance summary for human review

6. `lore-maintainer`

Purpose:

- search lore.kernel.org, patchwork, subsystem docs, and maintainer routing
  information

Rules:

- returns links and summaries
- does not decide recipient list automatically
- marks stale guidance by date

7. `model-benchmark`

Purpose:

- run local model tasks and collect metrics

Metrics:

- TTFT
- tokens/sec
- prompt ingestion time
- VRAM/RAM use
- tool-call validity
- patch apply rate
- checkpatch result
- build result
- semantic rejection reason

### MCP Security Rules

- never install random MCP servers into the main agent profile
- pin server versions
- inspect tool descriptions before use
- disable tools that can write outside the repo
- log every tool call
- prefer resources over tools for read-only context
- expose narrow whitelisted commands instead of generic shell
- assume untrusted web content and logs can contain prompt injection

MCP is useful only if it reduces ambiguity. If it adds tool sprawl, remove it.

## Skills

Use skills as reusable human-readable playbooks. They should be short,
auditable, and portable across Aider, Pi, OpenCode, and Qwen Code where
possible.

Recommended local skills:

- `kernel-mainline-slice`
- `evidence-matrix-row`
- `devicetree-binding-review`
- `dts-runtime-scope-review`
- `pinctrl-clock-reset-review`
- `netdev-etiquette`
- `commit-message-review`
- `cover-letter-review`
- `review-response-log`
- `ai-output-rejection-review`

Each skill should contain:

- purpose
- inputs
- forbidden shortcuts
- required output shape
- stop conditions

Skills should not grant authority. They should make the review process harder
to misread.

## Hooks and Local Gates

Hooks are more important than agents. They prevent the most common AI failure:
moving too fast with a plausible but dirty patch.

### Candidate Kernel Tree Hooks

Use a local hook stack in the candidate Linux tree.

Pre-commit checks:

- reject `WIP`, `fixup!`, `squash!`, `try`, and debug commits
- reject generated artifacts
- reject UART logs, DTBs, images, modules, objects, and compressed captures
- run `git diff --check`
- flag private host paths
- flag `Signed-off-by:` if the commit was made by an automated account

Post-agent checks:

- show `git status --short`
- list changed files
- run artifact scan
- run private-path scan
- run diffstat
- record model, harness, endpoint, and task ID

Pre-format-patch checks:

- apply series to fresh branch with `git am`
- run checkpatch on formatted patches
- run relevant DT/build checks
- verify base commit
- verify evidence matrix coverage
- verify runtime logs match the exact series
- verify tool-generated content provenance is recorded
- verify any proposed disclosure note is separate from the patch until human
  approval

Pre-send checks:

- send raw email to self
- apply received raw email with `git am`
- inspect for HTML, MIME attachments, wrapping, charset changes, and broken
  threading
- verify recipient matrix

### Repository Hooks

For this repository, hooks should reject:

- binary boot artifacts
- generated kernel outputs
- stale validation summaries without source logs
- claims of Ethernet support
- patch files without base records
- evidence rows without source paths

## Benchmarking Plan

Before picking a permanent agent, run the same benchmark tasks across Aider,
Pi, OpenCode, Qwen Code, and OpenHands.

### Required Benchmark Tasks

1. Commit message rewrite

- input: messy but correct patch
- expected output: maintainer-style commit message without overclaiming

2. DTS scope reduction

- input: DTS with overbroad enabled hardware
- expected output: disabled or removed unsupported nodes

3. Evidence extraction

- input: vendor/BSP snippets plus mainline precedent
- expected output: evidence matrix rows with source paths and confidence

4. Build-log repair

- input: compiler or dtbs_check warning
- expected output: smallest fix only

5. Semantic rejection

- input: patch that passes tools but has wrong subsystem placement
- expected output: reject, explain why, do not edit

6. UART panic analysis

- input: UART log plus patch context
- expected output: narrow diagnosis and next experiment

7. Patch split audit

- input: mixed subsystem patch
- expected output: ordered patch split proposal

### Benchmark Metrics

Collect:

- harness
- model
- runtime
- quantization
- context length
- prompt tokens
- TTFT
- tokens/sec
- wall time
- tool-call failures
- malformed JSON/tool calls
- patch applies: yes/no
- validation result
- semantic review result
- human correction required
- whether output overclaimed

The winning stack is not the fastest stack. The winning stack is the one with
the lowest semantic rejection rate while still being fast enough to use.

## Recommended Working Layout

Use these current and planned logical endpoints:

```text
current:
192.168.50.11:127.0.0.1:8082  qwen36-27b-long   Q4_K_M, llama.cpp Vulkan, Codex via SSH
192.168.50.252:127.0.0.1:8001 qwen36-27b-fast   Q4_K_M, llama.cpp Vulkan, Codex via SSH

planned:
192.168.50.252:8003            qwen36-review-aux 7900 XT or CPU/GPU offload
192.168.50.225:8080            local-ai-gateway  deterministic routing and logging
```

Use these working directories:

```text
kernel-mainline/           clean Linux candidate tree
kernel-scratch/            agent scratch branches and experiments
Home Lab/cubie-a7s-armbian project documentation and evidence
homelab/                   orchestration scripts, runbooks, and benchmarks
hardware-logs/             UART and boot logs outside public branch
```

## Concrete Local Pipeline

Use this as the operational pipeline for the local hardware stack. It is a
candidate-generation pipeline, not a submission pipeline.

### Phase 0: Patch Intent Gate

Create a task record before any model sees the code.

Required inputs:

- narrow problem statement
- affected subsystem
- base commit
- target branch
- target files
- evidence sources
- expected proof commands
- explicit non-goals
- allowed path set
- maximum repair attempts, default `2`

Verification check:

- halt if the task cannot be stated as one reviewable logical change
- halt if hardware values, compatible strings, clocks, resets, or ABI claims do
  not have evidence
- halt if the likely patch split is unknown

### Phase 1: Network Topology and Runtime Deployment

Establish the heterogeneous headless layout without putting container or model
load on the Mac Mini.

On `mac-mini`:

- run Codex Desktop as the only operator-facing dispatcher
- keep the homelab orchestration repo and runbooks local to Codex
- dispatch work to Linux hosts through SSH
- collect benchmark outputs and proof-log references
- do not install Docker Desktop
- do not run validation containers or sustained LLM endpoints by default

On `192.168.50.225`:

- reserve as the lightweight Linux service host
- later host deterministic gateway/proxy services if needed
- later host proof-log index or dashboard services if useful
- do not use it as a serious model-serving host

On `192.168.50.252`:

- expose `8001` for the primary RTX 3090 coding endpoint
- expose `8003` for auxiliary review, embeddings, or reranking on the 7900 XT
  or CPU/GPU offload
- log GPU runtime, model name, quantization, context length, and model hash

On `192.168.50.11`:

- start with native llama.cpp Vulkan before containers or ROCm/HIP
- keep the first endpoint bound to Strix loopback for benchmarking
- use `scripts/strix-llamacpp-native` from Codex Desktop to manage it
- later expose `8002` for long-context review only after routing/security is
  intentionally chosen
- optimize for prompt ingestion stability and context size, not edit latency
- log model hash, quantization, context settings, and runtime version

Phase 1 verification:

- verify SSH from Codex Desktop to every headless host
- verify GPU visibility on `192.168.50.252` and `192.168.50.11`
- probe every active `/v1/models` endpoint from its intended network location
- run a one-token or short-completion smoke test against each endpoint
- run `docker compose ps` only on Linux hosts that are actually using Compose
- verify no Mac containers were introduced
- halt if any endpoint is unhealthy, misrouted, or serving an unexpected model

Current completed Strix check:

- downloaded Qwen3.6-27B `Q4_K_M` GGUF to Strix
- started llama.cpp Vulkan on `127.0.0.1:8082`
- verified RADV Strix Halo GPU path in the server log
- ran the fair bench from Codex Desktop
- result: `agent_candidate`, 6/6 cases passed

Current completed RTX 3090 check:

- downloaded the same Qwen3.6-27B `Q4_K_M` GGUF to `192.168.50.252`
- verified matching model SHA256
- started llama.cpp Vulkan on `127.0.0.1:8001`
- verified `NVIDIA GeForce RTX 3090` in the server log
- ran the fair bench from Codex Desktop
- result: `agent_candidate`, 6/6 cases passed

Current completed validation-harness check:

- built `local/kernel-build-validate:20260606` on `192.168.50.252`
- current image ID:
  `sha256:d4a2fba26625b80557c2b855acb4089d415a8cb484c212409fee64bda0fae7a8`
- recorded tool versions in a proof log
- captured a dummy `PASS`
- captured an expected dummy `FAIL`
- captured a real `git diff --check` `PASS`
- captured a real `git diff --check` `FAIL` for trailing whitespace
- added a built-in strict checkpatch proof for the current dirty diff,
  including untracked files
- added Python `ply` and `git` modules so kernel SPDX checks run inside
  `scripts/checkpatch.pl`

Current completed kernel scratch check:

- synced the Strix kernel WIP from
  `192.168.50.11:/srv/projects/cubie-a7s-armbian/sources/mainline-linux`
  to `192.168.50.252:/srv/projects/kernel-work/scratch/strix-mainline-linux`
- preserved the WIP base commit `8fde5d1d47f6`
- kept sync additive by default, with no `--delete`
- fixed the rsync exclusions so root-level build outputs such as `/vmlinux`
  are skipped without dropping source files named `vmlinux.*`
- noted that `.git/index` may appear as a repeat dry-run transfer because it is
  a volatile Git cache file, not a source-content mismatch
- ran `git diff --check` in the AMD validation container against the synced
  tree
- proof ID:
  `synced-strix-mainline-git-diff-check-584ac4f56f72`
- result: `PASS`
- ran `scripts/checkpatch.pl --strict` against the current synced diff
- proof ID:
  `synced-strix-mainline-checkpatch-current-diff-strict-4c6a137383fe`
- result: `FAIL`, with `0 errors, 9 warnings, 1 checks`
- ran targeted A733 CCU binding validation
- proof ID:
  `synced-strix-mainline-dt-binding-check-73bf3de72d64`
- result: `PASS`
- ran targeted Cubie A7S DTB validation
- proof ID:
  `synced-strix-mainline-dtbs-check-b6e4c7ddfccf`
- result: `FAIL`; `sun60i-a733.dtsi` references `CLK_BUS_GMAC0` and
  `RST_BUS_GMAC0`, but the A733 dt-bindings headers currently do not define
  them
- deferred unproven GMAC from the first Cubie A7S validation slice rather than
  inventing clock/reset identifiers
- added `allwinner,sun60i-a733-mmc` to the existing MMC binding pattern using
  `allwinner,sun20i-d1-mmc` as fallback
- proof ID:
  `a733-mmc-compatible-binding-dt-binding-check-562c5187dab1`
- result: `PASS`
- proof ID:
  `a733-defer-unproven-gmac-cubie-a7s-dtbs-check-94d5f0714c56`
- result: `PASS`
- latest strict checkpatch proof:
  `a733-defer-unproven-gmac-checkpatch-current-diff-strict-d61c953b97c1`
- result: `FAIL`, with `0 errors, 7 warnings, 1 checks`

Current completed review-handoff check:

- generated a maintainer review payload from the synced tree
- included changed files, untracked files, diff, diff stat, maintainer route,
  proof IDs, and proof hashes
- sent the payload to Strix through SSH against its loopback model endpoint
- wrote reviewer notes under `task-packets/kernel/reviews/`
- refreshed the payload with both the `git diff --check` `PASS` and strict
  checkpatch `FAIL`
- current payload SHA256:
  `024943eb73c30b5b4b9b13c0f46f0624934eacd27428fb1ee42b9064fd4be0b6`
- halted with `halted_for_human_gate=1`
- observed that Strix correctly noticed the checkpatch failure but inferred some
  checkpatch details loosely; raw proof logs remain the authority
- created the task packet
  `task-packets/kernel/a733-gmac-clock-reset-bindings.json`
- refreshed Strix review around the GMAC blocker with four proof logs
- GMAC blocker payload SHA256:
  `9b373d6a0c4b4ba61894ad1d79bf6893276207fa9e5fc9f27c9ff6eb0314d673`
- current policy: do not invent A733 GMAC clock/reset identifiers; find evidence
  for the clock/reset map or defer unproven Ethernet from the first validation
  slice
- latest repaired-slice review payload SHA256:
  `962ab817120d7d9b45eb007c40d2c8003e52cd70351e7e80e6aeff91ff209f1b`
- latest Strix advisory risks: minimal CCU driver, A733 workaround in shared
  pinctrl core, and too-broad board-support expectations

### Phase 2: Containerized Validation Environment

Build a Linux-hosted validation container that makes tool results reproducible
instead of dependent on accidental host packages.

Do not build or run this container on the Mac Mini by default. Prefer
`192.168.50.252` or `192.168.50.225` for the validation container, depending on
whether the task needs fast local storage, CPU, or proximity to the kernel
scratch tree.

The `build-validate` image should include:

- pinned `aarch64-linux-gnu-gcc`
- pinned build-essential and kernel build dependencies
- `dtc`
- `dtschema`
- `yamllint`
- `sparse`
- documentation build dependencies when documentation changes are in scope
- exact version reporting for every validation tool

Mount policy:

- mount `kernel-scratch/` read/write only during active test loops
- mount `proof-logs/` read/write as a named volume
- mount reference kernel trees read-only unless the task explicitly needs a
  scratch worktree
- do not mount `$HOME`
- do not mount SSH keys
- do not mount browser profiles, chat logs, or private project directories
- do not mount any directory containing the word `telegram`

Phase 2 verification:

- build the container from pinned inputs
- record the container image digest
- run `make ARCH=arm64 dt_binding_check` against a dummy schema
- run a known failing dummy schema and confirm failure is captured
- run `git diff --check` and `scripts/checkpatch.pl --strict` on a dummy patch
- confirm proof logs include raw stdout, stderr, exit code, command, versions,
  timestamps, and hashes

Avoid Docker-on-macOS filesystem behavior entirely unless a later explicit
design decision chooses Colima or a Linux VM for a narrow reason. The default
kernel validation path is Linux-native.

### Phase 3: Task Distribution and Terminal Validation

The orchestrator is deterministic. It may ask models for edits, summaries, and
reviews, but it owns routing, validation, logging, and stop conditions.

Distribution rules:

- route short edit tasks to `192.168.50.252:8001`
- route long-context investigation to the managed Strix loopback endpoint over
  SSH today, or `192.168.50.11:8002` later if intentionally exposed
- route embeddings/reranking to `192.168.50.252:8003`
- strip unrelated project context
- provide bounded, evidence-based context, not an arbitrary 50-line maximum
- require unified diffs or normal git worktree edits
- reject edits outside the allowed path set
- reject binary changes and generated artifacts

Validation loop:

1. apply or inspect the proposed diff in `kernel-scratch/`
2. run the required proof commands in `build-validate`
3. write immutable proof logs
4. if a command fails, send the exact command, exit code, proof ID, and relevant
   stderr/stdout excerpt back to `192.168.50.252:8001`
5. preserve the full raw log even when the model receives a truncated excerpt
6. allow the smallest repair only
7. stop after the configured repair-attempt limit
8. stop immediately on semantic uncertainty, subsystem uncertainty, or
   conflicting evidence

Phase 3 verification:

- inject a dummy syntax error in a scratch branch
- confirm the harness captures failure with a nonzero exit code
- confirm log truncation preserves first actionable diagnostics and suppresses
  repeated cascades only in the model-facing excerpt
- confirm the full raw log remains available by proof ID
- confirm the repair loop stops after the configured attempt limit

### Phase 4: Long-Context Review and Human Approval Gate

Only after relevant validation commands pass may the orchestrator create a
review payload for Strix.

Review payload:

- patch diff
- patch intent record
- proof log IDs and hashes
- exact terminal command summaries
- `MAINTAINERS` excerpts
- `scripts/get_maintainer.pl` output
- recent relevant commits for touched files
- relevant binding schemas or subsystem docs
- AI/tool provenance summary
- known non-goals and untested areas

Use this reviewer prompt:

```text
Find three reasons a Linux kernel maintainer would reject this code.
```

Execution halt:

- print the finalized diff
- print proof IDs and hashes
- print maintainer-routing evidence
- print Strix rejection risks
- print provenance summary
- stop completely

Absolute constraints:

- do not apply the patch to a candidate branch
- do not add trailers
- do not create a submission series
- do not send email
- do not mark the task mainline-ready

Phase 4 verification:

- run an end-to-end dry run
- confirm Strix receives the curated payload
- confirm review risks cite evidence or explicitly report no grounded risks
- confirm the orchestrator halts for human approval
- confirm no candidate branch, trailer, or outbound mail action occurs

## Promotion Rules

An AI-produced diff may move from scratch to candidate only after the human
operator accepts the patch candidate packet and only when:

- it touches one reviewable slice
- every non-obvious value has a strong evidence row
- it applies from the recorded base
- it builds at its point in the series
- relevant validation logs are exact and fresh
- runtime claims match exact artifacts
- Strix reviewer did not identify a semantic blocker
- tool-generated content provenance is recorded
- likely patch split and maintainer route are understood
- human review accepts the diff

No agent may add:

- `Signed-off-by:`
- `Reviewed-by:`
- `Acked-by:`
- `Tested-by:`
- `Assisted-by:`

The orchestrator may prepare a provenance note for the human operator, but the
human decides the final disclosure text and any trailers.

No agent may send email.

## What Not To Do

Do not:

- optimize for maximum autonomy
- let a model decide that a patch is mainline-ready
- use a model dispatcher
- expose broad shell MCP tools to autonomous agents
- treat checkpatch as proof of correctness
- treat dtbs_check as proof of hardware behavior
- treat any local `PASS` as maintainer acceptance
- treat boot-to-initramfs as full board support
- enable Ethernet until reset, clock, wrapper, MDIO, PHY, carrier, and link
  behavior are proven
- let agent output rewrite evidence to match code
- let a generated patch carry human trailers
- benchmark only success cases

## Immediate Recommendation

Build the remaining baseline in this order:

1. Keep Strix native Vulkan Qwen3.6-27B `Q4_K_M` as the first measured
   long-context baseline.
2. Keep RTX 3090 native Vulkan Qwen3.6-27B `Q4_K_M` as the first measured
   fast-coding baseline.
3. Built-in verification harness with proof logs and forced terminal-output
   ingestion.
4. Aider: first editing harness.
5. Strix semantic reviewer prompt/skill.
6. Hook stack for artifact rejection, base checks, and validation logs.
7. ThinkCentre or AMD deterministic gateway only when routing needs justify it.
8. Benchmark Pi, OpenCode, Qwen Code, Gemini CLI, and OpenHands against Aider.
9. Benchmark `gpt-oss-20b` and higher Qwen3.6 GGUF quants as challengers.
10. Add MCP servers only after the hook stack and verification harness are
   working.

This ordering avoids the failure mode where a sophisticated harness produces
high-volume bad patches before the local process can reject them.

## Current Bottom Line

The best local setup is:

- RTX 3090: Qwen3.6-27B quantized for speed, used by Aider/Qwen Code/OpenCode
  for small patch drafting; first measured lane is native llama.cpp Vulkan at
  32K context on `192.168.50.252`.
- Strix: measured Qwen3.6-27B `Q4_K_M` native llama.cpp Vulkan endpoint, used
  for investigation, evidence review, and maintainer-style rejection at
  `192.168.50.11`.
- 7900 XT: auxiliary review, embeddings, reranking, and benchmark endpoint.
- Codex Desktop: dispatcher/operator surface.
- Gateway: optional deterministic router on Linux, not model-selected routing
  and not Docker Desktop on the Mac.
- Verification: whitelisted proof tools that run `checkpatch.pl`,
  `dt_binding_check`, `dtbs_check`, builds, and `git am`, then feed raw
  terminal output back to the local model.
- Harness: Aider first, Pi/OpenCode/Qwen Code as benchmark challengers,
  OpenHands/SWE-agent as stress tests only.
- MCP: narrow custom servers for kernel tree reads, evidence, build validation,
  hardware logs, patch series mechanics, and lore/maintainer lookup.
- Hooks: strict enough that an agent cannot accidentally promote dirty work.

If this stack fails, it will fail because the model cannot make correct
semantic judgments, not because the process let bad work slip through quietly.
That is the right failure mode.

## Sources Checked

- Qwen3.6-27B model card:
  <https://huggingface.co/Qwen/Qwen3.6-27B>
- vLLM OpenAI-compatible server docs:
  <https://docs.vllm.ai/en/v0.6.5/serving/openai_compatible_server.html>
- vLLM FP8 KV-cache blog:
  <https://vllm-project.github.io/2026/04/22/fp8-kvcache.html>
- ExLlamaV2 / TabbyAPI README:
  <https://github.com/turboderp-org/exllamav2>
- Ollama OpenAI compatibility:
  <https://docs.ollama.com/openai>
- OpenHands LLM overview:
  <https://docs.openhands.dev/openhands/usage/llms/llms>
- OpenHands local LLM guide:
  <https://docs.openhands.dev/openhands/usage/llms/local-llms>
- SWE-agent FAQ:
  <https://swe-agent.com/0.7/usage/usage_faq/>
- Qwen Code repository:
  <https://github.com/QwenLM/qwen-code>
- OpenAI GPT-5.3-Codex announcement:
  <https://openai.com/index/introducing-gpt-5-3-codex/>
- OpenAI gpt-oss open models:
  <https://openai.com/open-models/>
- DeepSeek API changelog:
  <https://api-docs.deepseek.com/updates/>
- Gemini CLI repository:
  <https://github.com/google-gemini/gemini-cli>
- Aider repository:
  <https://github.com/aider-ai/aider>
- Pi / Earendil Works repository:
  <https://github.com/earendil-works/pi>
- OpenCode docs:
  <https://opencode.ai/docs>
- OpenCode repository:
  <https://github.com/opencode-ai/opencode>
- Overeager coding agents paper:
  <https://arxiv.org/abs/2605.18583>
- Token usage in coding agents paper:
  <https://arxiv.org/abs/2604.22750>
- LiteLLM docs:
  <https://docs.litellm.ai/>
- llama-swap repository:
  <https://github.com/mostlygeek/llama-swap>
- Model Context Protocol server concepts:
  <https://modelcontextprotocol.io/docs/learn/server-concepts>
- Linux kernel submitting patches:
  <https://docs.kernel.org/process/submitting-patches.html>
- Linux kernel patch submission checklist:
  <https://docs.kernel.org/process/submit-checklist.html>
- Linux kernel email client guidance:
  <https://docs.kernel.org/process/email-clients.html>
- Linux kernel AI coding assistant policy:
  <https://docs.kernel.org/process/coding-assistants.html>
- Linux kernel generated-content guidelines:
  <https://docs.kernel.org/process/generated-content.html>
- Linux kernel checkpatch documentation:
  <https://docs.kernel.org/dev-tools/checkpatch.html>
- Devicetree binding submission rules:
  <https://docs.kernel.org/devicetree/bindings/submitting-patches.html>
- Devicetree binding schema guide:
  <https://docs.kernel.org/devicetree/bindings/writing-schema.html>
- Devicetree ABI notes:
  <https://docs.kernel.org/devicetree/bindings/ABI.html>
- SoC maintainer process:
  <https://docs.kernel.org/process/maintainer-soc.html>
- Netdev maintainer handbook:
  <https://docs.kernel.org/process/maintainer-netdev.html>
