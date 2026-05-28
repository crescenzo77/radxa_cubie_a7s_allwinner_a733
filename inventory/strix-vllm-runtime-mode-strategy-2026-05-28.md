# Strix vLLM Runtime Mode Strategy - 2026-05-28

Purpose: design the next Strix runtime mode strategy without changing live
services, ports, Docker Compose files, model-dispatch, or Open WebUI.

## Current Live Baseline

Validated before writing this note:

- Host: `strix`
- Repo: `/srv/projects/homelab`
- Latest homelab commit before this note:
  `333ac63 document real bounded aider trial`
- Active mode: `tool`
- Active served model: `qwen36-awq-agent-test`
- Active container: `vllm-strix-qwen36-awq-agent`
- ThinkCentre `model-dispatch.service`: active
- ThinkCentre service restart policy: `Restart=on-failure`

## Current Design

Two Strix vLLM runtimes are validated, but they share one host port:

| Mode | Compose file | Container | Served model | Role alias |
| --- | --- | --- | --- | --- |
| `tool` | `runtime/strix-qwen36-awq-agent/compose.yml` | `vllm-strix-qwen36-awq-agent` | `qwen36-awq-agent-test` | `local/tool-test` |
| `code` | `runtime/strix-qwen3-coder-next-awq-test/compose.yml` | `vllm-strix-qwen3-coder-next-awq-test` | `qwen3-coder-next-awq-agent-test` | `local/code-test` |

Both Compose files bind vLLM to host port `8010`. Because of that, both modes
cannot be live at the same time with the current design.

The helper at `scripts/strix-vllm-mode` is the current safe control point:

- `scripts/strix-vllm-mode status`
- `scripts/strix-vllm-mode tool`
- `scripts/strix-vllm-mode code`

It stops the other runtime, starts the selected runtime, waits for the expected
served model on `127.0.0.1:8010`, then runs the matching model-dispatch smoke
test.

## Problem To Solve Later

`local/tool-test` and `local/code-test` are role aliases that look like stable
model choices, but today they are mode-specific:

- `local/tool-test` works only when `tool` mode is active.
- `local/code-test` works only when `code` mode is active.
- The inactive alias fails because its served model is absent from the one live
  vLLM process.

That is acceptable for controlled validation. It is not a good long-term shape
if tools expect both aliases to be available at the same time.

## Strategy Options

### Option 1: Keep Manual One-Port Switching

Keep the current design and make the mode boundary more visible in docs and
operator prompts.

Pros:

- Already implemented and validated.
- No new ports, routes, service units, or persistence behavior.
- Lowest operational risk.
- Good fit while Aider and local agent workflows remain evaluation-only.

Cons:

- `local/tool-test` and `local/code-test` cannot both be used at once.
- Users and agents must know which mode is active before choosing an alias.
- Aider trials require a deliberate switch to `code` and a restore to `tool`.

Best use:

- Current default.
- Continue until there is a repeated need for simultaneous tool and code
  serving.

### Option 2: Two Ports On Strix

Run Qwen3.6 and Coder-Next on separate Strix ports, then update
model-dispatch aliases to point each role alias at its own backend.

Possible shape:

- Qwen3.6 remains on `strix:8010`.
- Coder-Next moves to a second explicit port, such as `strix:8011`.
- `local/tool-test` points to the Qwen3.6 backend.
- `local/code-test` points to the Coder-Next backend.

Pros:

- Both aliases can be live at the same time.
- Clear routing model.
- Minimal conceptual change for clients.

Cons:

- Requires live service changes.
- Requires Compose changes.
- Requires model-dispatch config changes and restart/reload planning.
- May exceed Strix memory or GPU capacity if both models run together.
- Needs new health, smoke, rollback, and resource checks.

Best use:

- Only after proving Strix can host both runtimes concurrently without memory,
  stability, or performance problems.

### Option 3: One Active Backend With Dispatch Awareness

Keep one Strix vLLM port, but make the dispatcher or a visible operator layer
aware that one alias is inactive depending on mode.

Pros:

- Avoids concurrent model memory pressure.
- Keeps the one-port runtime design.
- Could give clearer errors than a missing served model.

Cons:

- Requires model-dispatch behavior changes.
- Adds routing logic around runtime state.
- Could hide a mode switch behind a model request if designed poorly.

Best use:

- Only if better user-facing errors are needed before concurrent serving is
  justified.

### Option 4: Automatic Mode Switching

Let requests for `local/code-test` or `local/tool-test` trigger a runtime
switch automatically.

Pros:

- Convenient when it works.

Cons:

- Violates the current no-hidden-automation posture.
- A normal model request could stop the active runtime.
- Slow startup makes request timing unpredictable.
- Risky for Open WebUI or any other client expecting stable availability.

Best use:

- Do not use for the current phase.

## Recommendation

Keep Option 1 as the current operating strategy:

- Manual one-port switching remains the only approved runtime mode behavior.
- `tool` remains the stable baseline after tests.
- `code` is selected only for explicit Coder-Next or Aider evaluation work.
- Every `code` trial must restore `tool` afterward and prove `local/tool-test`.

Do not implement concurrent serving yet.

The next implementation slice, if selected later, should be a narrow
concurrency feasibility test, not a routing change. It should answer only:

- Can Strix run both models at once?
- What ports would they use?
- What memory and startup behavior are observed?
- Can both direct `/v1/models` endpoints respond at the same time?
- Can both model-dispatch aliases pass smoke tests after a controlled config
  change?
- What is the exact rollback?

## Non-Goals

This note does not:

- Change any Compose files.
- Change any ports.
- Change model-dispatch aliases or routes.
- Change Open WebUI defaults.
- Add systemd units, watchdogs, timers, or hidden automation.
- Start or stop any containers.
- Promote Aider to the core workflow.

## Suggested Next Action

Stop here, or write a separate approval brief for a future Strix two-port
concurrency feasibility test. Do not combine that test with model-dispatch
route changes or Open WebUI defaults.
