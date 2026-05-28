# Strix Two-Model Feasibility Attempt - 2026-05-28

Purpose: record the failed first attempt to run both Strix vLLM models live at
the same time, and preserve the recovery facts.

## Goal

Move toward having both validated Strix models live:

- Qwen3.6 AWQ tool model on `8010`
- Qwen3-Coder-Next AWQ code model on `8011`

Then use the always-live Coder-Next path for bounded Aider work.

## Attempted Shape

Temporary, uncommitted changes were made:

- Coder-Next Compose port changed from `8010` to `8011`.
- `local/strix-qwen3-coder-next-awq-agent` in model-dispatch was pointed at
  `http://192.168.50.11:8011/v1`.
- `scripts/aider-code-test` was pointed at `127.0.0.1:8011`.
- `scripts/strix-vllm-mode` was changed locally to understand a `both` mode.

These changes were not committed.

## Result

The first concurrent Coder-Next start failed cleanly:

- Qwen3.6 remained live on `8010`.
- Coder-Next tried to reserve `gpu-memory-utilization=0.70`.
- vLLM reported only about `35.08 GiB` free out of `116.0 GiB`.
- vLLM refused startup because `0.70` requested about `81.2 GiB`.

The second retry lowered Coder-Next to `gpu-memory-utilization=0.25`.
That avoided the immediate memory reservation failure, but Strix became too
sluggish to accept SSH reliably. The user power-cycled Strix.

Treat this as a failed feasibility attempt, not a partial success.

## Recovery

After reboot:

- Strix came back online.
- Qwen3.6 restarted because its Compose runtime uses `restart: unless-stopped`.
- Coder-Next was left exited and then removed by `scripts/strix-vllm-mode tool`.
- Homelab runtime/helper files were restored from `HEAD`.
- ThinkCentre `model-dispatch/config.json` was restored from `HEAD`.
- Generated `scripts/__pycache__/` was removed.
- `scripts/strix-vllm-mode tool` passed.
- Final Strix active mode: `tool`
- Final served model: `qwen36-awq-agent-test`
- Final model-dispatch service state: active

## Current Safe Baseline

The system is back to the previous safe shape:

- Only Qwen3.6 AWQ is live on Strix port `8010`.
- `local/tool-test` works.
- Coder-Next is not live.
- `local/code-test` still requires a deliberate switch to Coder-Next mode.
- Aider remains evaluation-only.

## Lessons

- Two models may fit only with substantially lower memory settings, shorter
  context, or a different serving strategy.
- A simple second-port change is not enough.
- The next attempt needs a safer resource-first test before model-dispatch or
  Aider integration changes.

## Safer Next Attempt

For the next slice, do not touch model-dispatch or Aider first.

Recommended order:

1. Keep Qwen3.6 live on `8010`.
2. Start Coder-Next manually on `8011` with a very conservative memory target.
3. Validate only direct `curl http://127.0.0.1:8011/v1/models`.
4. Watch SSH responsiveness, memory, and Docker logs.
5. Stop Coder-Next immediately if SSH or shell responsiveness degrades.
6. Only after direct Strix stability is proven, update model-dispatch and Aider.

Suggested trial constraints:

- No restart policy for Coder-Next.
- No model-dispatch changes during the first direct test.
- No Aider run during the first direct test.
- No Open WebUI changes.
- Clear rollback command ready before starting.

## Do Not Commit From The Failed Attempt

Do not commit the temporary failed-attempt changes:

- Coder-Next `8011` Compose change
- `aider-code-test` `8011` check
- `strix-vllm-mode both`
- model-dispatch endpoint change to `8011`

Those changes should be reintroduced only after direct two-model stability is
proven.
