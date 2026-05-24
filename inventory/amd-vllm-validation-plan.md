# AMD vLLM Validation Plan

## Purpose

Plan the first AMD-first vLLM validation path while preserving current healthy
local model serving and routing. This plan does not start vLLM, install vLLM,
stop containers, change `model-dispatch`, or change Open WebUI.

The goal is to define the inspection and approval gates needed before any
runtime experiment uses AMD's RTX 3090 as a temporary vLLM validation target.

## Current AMD Facts

- AMD is the better first vLLM candidate.
- AMD has RTX 3090 visible through `nvidia-smi`.
- The NVIDIA driver reports CUDA 13.2 support.
- RTX 3090 VRAM is mostly occupied by the current `qwen3-coder-30b`
  llama.cpp container.
- AMD currently has healthy containers:
  - `qwen3-coder-30b` on port 8083.
  - `gemma4-7900xt` on port 8084.
- AMD current endpoints return OpenAI-compatible `/v1/models`.
- `vllm` was not found in the current user path.
- Python is 3.14.4.
- ThinkCentre `model-dispatch` and Open WebUI routing are healthy and
  unchanged.

## Why AMD Goes First

AMD goes first because it already has the clearest NVIDIA validation path:
the RTX 3090 is visible, the driver reports CUDA 13.2 support, and existing
local OpenAI-compatible endpoints are healthy enough to provide a comparison
baseline.

Strix remains later because ROCm tools are absent there and port 8000 is
occupied. A Strix attempt would add driver/toolchain and port uncertainty before
proving the simpler NVIDIA/vLLM path.

## Inspect Before Any vLLM Run

Before any vLLM process is started, a future slice must recheck AMD live state
read-only:

- GPU visibility and driver/runtime details.
- Current VRAM use.
- Current container names, images, ports, and health.
- Existing listeners on likely vLLM ports.
- Existing Python and package environment constraints.
- Whether `vllm` exists in any intended runtime environment.
- Available model files, formats, and storage locations.
- Whether candidate commands would require network access, package installs,
  container pulls, sudo, Docker writes, or service changes.

If any inspection step implies a host role change, routing change, billing
exposure, persistent state change, or security posture change, stop and write
an approval brief before implementation.

## RTX 3090 VRAM Issue

The RTX 3090 is not currently free for vLLM. Its VRAM is mostly occupied by the
healthy `qwen3-coder-30b` llama.cpp container on port 8083.

That container must not be stopped, restarted, replaced, or reconfigured during
planning. Freeing the RTX 3090 is Phase 5 and requires explicit operator
approval after the candidate vLLM method, model, port, and rollback plan are
documented.

## Candidate Validation Options

Candidate options for a future runtime slice:

- Use an already-present local vLLM runtime if inspection finds one outside the
  current user path.
- Use a containerized vLLM runtime only if the image is already present or the
  operator explicitly approves any pull/install path.
- Use an isolated Python environment only if package versions, Python support,
  and install source are documented and explicitly approved.
- Defer AMD runtime validation if no no-install candidate exists and the next
  step would require package installation or network access.

The first live validation should prefer the smallest reversible path that can
serve one candidate model on a temporary port and answer OpenAI-compatible curl
checks.

## Port Choice Constraints

- Do not use port 8083 because it belongs to `qwen3-coder-30b`.
- Do not use port 8084 because it belongs to `gemma4-7900xt`.
- Do not assume port 8000 is free; Strix already has a port 8000 conflict, and
  AMD must be checked read-only before choosing any port.
- Prefer a temporary, clearly documented validation port that is not currently
  used by AMD, `model-dispatch`, Open WebUI, OpenCode, Continue.dev, LiteLLM,
  dashboards, monitoring, or observability.
- Do not add the temporary port to `model-dispatch` until after Aider/vLLM proof.

## Model Choice Constraints

- Prefer a local model that is already present on AMD or otherwise available
  without new network downloads.
- Prefer a model format compatible with the chosen vLLM runtime.
- Avoid changing or moving the active `qwen3-coder-30b` and `gemma4-7900xt`
  model artifacts during validation planning.
- Do not select a model that requires paid-provider access, model API calls, or
  broad new automation.
- If the best candidate requires freeing RTX 3090 VRAM, stop for approval
  before touching the active 8083 container.

## Qwen Thinking-Off Baseline

For Aider-oriented patch output, the baseline is Qwen thinking-off or
non-thinking mode. The goal is predictable patch-oriented responses, not
long-form reasoning traces.

Reasoning-parser or thinking-on mode remains a separate review/architecture
validation path and should not be mixed into the first Aider patch-output
compatibility test.

## Rollback And Stop Conditions

Stop before implementation if:

- The next step would start vLLM.
- The next step would install packages, pull images, or require network access.
- The next step would stop, restart, or reconfigure `qwen3-coder-30b` or
  `gemma4-7900xt`.
- The next step would edit `model-dispatch`, `/srv/model-dispatch`, Open WebUI,
  OpenCode, Continue.dev, LiteLLM, dashboards, monitoring, or observability.
- The next step would require `sudo`, Docker write commands, or systemd write
  commands.
- The candidate model, runtime method, or port choice is unclear.
- The validation would affect host roles, routing behavior, billing exposure,
  persistent state location, or security posture.

Rollback for the later runtime slice should be simple: stop only the temporary
vLLM process that was explicitly approved and leave existing 8083, 8084,
`model-dispatch`, and Open WebUI behavior unchanged.

## What Not To Change Yet

- Do not run vLLM.
- Do not install vLLM.
- Do not stop or restart `qwen3-coder-30b`.
- Do not stop or restart `gemma4-7900xt`.
- Do not run Aider.
- Do not edit `model-dispatch`.
- Do not edit `/srv/model-dispatch`.
- Do not change Open WebUI.
- Do not change OpenCode.
- Do not change Continue.dev.
- Do not change LiteLLM.
- Do not change dashboards, monitoring, or observability.
- Do not run `sudo`, Docker write commands, or systemd write commands.
- Do not commit as part of this planning slice.

## Future Validation Phases

### Phase 1: Read-Only AMD Live-State Recheck

Recheck AMD GPU visibility, VRAM use, container state, endpoint health, port
listeners, Python/runtime state, and existing model artifacts without changing
anything.

### Phase 2: Identify Candidate vLLM Install/Runtime Method

Identify whether vLLM is already available through a local runtime, present
container image, or approved isolated environment. Do not install or pull
anything without explicit approval.

### Phase 3: Identify Candidate Model And Model Format

Choose the smallest useful local candidate model and confirm its format is
compatible with the selected vLLM runtime. Preserve active llama.cpp model
serving during this decision.

### Phase 4: Choose Temporary Port And Resource Plan

Pick a temporary unused AMD port and document GPU, VRAM, CPU, storage, and
rollback expectations. Keep the port out of `model-dispatch`.

### Phase 5: Stop Or Free RTX 3090 Only After Explicit Approval

If RTX 3090 VRAM must be freed, write an approval brief first. Do not stop or
restart `qwen3-coder-30b` until the operator approves the exact action.

### Phase 6: Start vLLM Only After Explicit Approval

Start the temporary vLLM runtime only after the runtime method, model, port,
resource plan, and rollback command are approved.

### Phase 7: Curl-Only OpenAI-Compatible Checks

Validate only with curl-style OpenAI-compatible checks first, including
`/v1/models` and a minimal non-streaming chat completion. Do not run Aider yet.

### Phase 8: Aider One-File Docs Trial Only After Curl Checks Pass

After response shape is proven, run a single bounded Aider trial against one
docs file in one repo with Qwen thinking-off or non-thinking mode as the patch
baseline.

### Phase 9: Model-Dispatch Alias Only After Aider/vLLM Proof

Add a dedicated `model-dispatch` alias only after vLLM response shape and
Aider compatibility are proven. That alias work requires a separate slice and
approval if it touches live routing.
