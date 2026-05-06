# Agent Status

## Current status

Slice 16 documentation edits are complete and ready for review.

## Current slice

Slice 16: synchronize architecture docs with live OpenCode state.

## What changed

Updated stale architecture and workflow documentation so the repo now reflects the deployed routing state:

- AMD OpenCode defaults to `homelab-local`.
- AMD OpenCode uses the direct local endpoint `http://192.168.50.252:8083/v1`.
- `homelab-openrouter-free` is documented as a manual-only provider.
- `homelab-openrouter-free` is documented as exposing 25 verified free OpenRouter models.
- LiteLLM is documented as still active for Open WebUI and retained for OpenCode rollback.
- Open WebUI is documented as not migrated yet.
- No automatic OpenRouter fallback is documented.

## What did not change

No live services or configs were changed.

No:

- OpenCode live config edits
- Open WebUI live config edits
- LiteLLM changes
- service restarts
- OpenRouter calls
- remote mutations
- commits

## Files changed

- `HOMELAB_LAYOUT.md`
- `WORKFLOW.md`
- `ROADMAP.md`
- `OPENROUTER_FREE_ARTIFACT_PLAN.md`
- `ROUTING_INVENTORY.md`
- `AGENT_STATUS.md`

## Checks run

- Read required context files:
  - `AGENTS.md`
  - `CODEX_CONTEXT.md`
  - `PROJECT_PLAN.md`
  - `CURRENT_SLICE.md`
  - `DECISIONS.md`
  - `AGENT_STATUS.md`
  - `HOMELAB_LAYOUT.md`
  - `WORKFLOW.md`
  - `ROADMAP.md`
  - `OPENROUTER_FREE_ARTIFACT_PLAN.md`
  - `ROUTING_INVENTORY.md`
- Ran `rg` scans for stale OpenCode-through-LiteLLM wording.
- Ran `rg` scans for current routing assertions.
- Ran `git diff --stat`.
- Ran `git status --short`.

## Results of checks

- No remaining stale OpenCode-through-LiteLLM default-path wording was found in the slice docs.
- Current routing docs now include:
  - `homelab-local`
  - `homelab-openrouter-free`
  - 25 verified free OpenRouter models
  - Open WebUI still using LiteLLM
  - LiteLLM retained for OpenCode rollback
  - OpenRouter manual-only behavior

## Known risks or blockers

No blockers.

Residual risk: this was a documentation-only synchronization against the live state provided in the task. No live config was inspected or changed during this slice.

## User approval needed

No approval is needed for the completed documentation edits.

Approval is still required before any future live service or config change.

## Recommended next action

Review the git diff, then commit Slice 16 if the documentation matches the intended live state.
## AMD 7900 XT backup provider result

Executed successfully on 2026-05-06.

Backup created on AMD:

```text
/home/enzo/.config/opencode/opencode.json.bak.20260506-185651.before-7900xt-backup
```

Live AMD OpenCode config now includes:

- primary provider: `homelab-local`
- primary model: `homelab-local/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
- backup provider: `homelab-local-backup`
- small model: `homelab-local-backup/google_gemma-4-26B-A4B-it-Q4_K_M.gguf`
- manual provider: `homelab-openrouter-free`

Validation output:

```text
build · Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf

opencode-direct-local-ok
```

Backup endpoint verified:

```text
http://192.168.50.252:8084/v1
google_gemma-4-26B-A4B-it-Q4_K_M.gguf
```

Result:

- OpenCode default remains AMD 3090 direct local.
- OpenCode `small_model` now points to AMD 7900 XT direct backup.
- OpenRouter-free remains manual-only.
- No OpenRouter call was made.
- LiteLLM unchanged.
- Open WebUI unchanged.

Recommended next action:

Update `HOMELAB_LAYOUT.md`, `WORKFLOW.md`, `ROADMAP.md`, and `ROUTING_INVENTORY.md` to reflect that AMD OpenCode now has a direct local backup provider for the RX 7900 XT endpoint.
