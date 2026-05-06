# Current Slice

## Slice 16: Synchronize architecture docs with live OpenCode state

Update homelab architecture and workflow documentation so the repo reflects the actual deployed OpenCode routing state.

## Purpose

The live homelab state changed during Slices 14 and 15:

- AMD OpenCode no longer defaults through LiteLLM.
- AMD OpenCode now defaults to direct AMD local-coder.
- AMD OpenCode now includes a manual generated OpenRouter-free provider.
- LiteLLM remains active for Open WebUI and rollback.
- OpenRouter remains manual-only in OpenCode.

The docs must reflect reality so the repo remains trustworthy as canonical context for humans and agents.

## Scope

Documentation-only updates:

- `HOMELAB_LAYOUT.md`
- `WORKFLOW.md`
- `ROADMAP.md`
- `OPENROUTER_FREE_ARTIFACT_PLAN.md`
- `ROUTING_INVENTORY.md`

## Constraints

- No live config changes.
- No service restarts.
- No OpenRouter calls.
- No OpenCode config edits.
- No LiteLLM changes.
- No Open WebUI changes.
- No remote mutation.

## Required documentation changes

### HOMELAB_LAYOUT.md

Update OpenCode routing description:

Old conceptual path:

```text
OpenCode
→ LiteLLM
→ local/OpenRouter
```

Current live path:

```text
OpenCode on AMD
→ direct AMD local provider by default
→ manual generated OpenRouter-free provider available
→ LiteLLM removed from OpenCode default path
```

Document:

- local provider name: `homelab-local`
- OpenRouter provider name: `homelab-openrouter-free`
- OpenRouter remains manual-only
- LiteLLM retained for Open WebUI and rollback

### WORKFLOW.md

Update operator workflow:

OpenCode now runs directly against AMD local-coder by default.

OpenRouter free-only models are available manually through generated provider config.

LiteLLM is no longer part of the default OpenCode execution path.

### ROADMAP.md

Mark completed:

- OpenCode direct-local migration
- OpenRouter-free manual provider migration

Add future work item:

- optional direct AMD backup provider
- optional removal of LiteLLM from OpenCode entirely after stability period
- possible later Open WebUI routing reevaluation

### OPENROUTER_FREE_ARTIFACT_PLAN.md

Update status:

- generated provider now live on AMD OpenCode
- direct local provider now live
- OpenRouter remains manual-only
- no automatic cloud fallback exists

### ROUTING_INVENTORY.md

Update actual current routing inventory:

AMD OpenCode:

- default provider: `homelab-local`
- direct endpoint: `http://192.168.50.252:8083/v1`
- manual provider: `homelab-openrouter-free`
- verified free model count: 25
- OpenRouter default usage: disabled/manual-only

LiteLLM:

- still active for Open WebUI
- retained for rollback
- not default OpenCode path anymore

## Acceptance Criteria

- Repo docs match live deployed behavior.
- OpenCode routing path is accurately described.
- Manual-only OpenRouter behavior is documented.
- LiteLLM’s reduced role is documented.
- No live services or configs are changed.
- Git diff is shown before commit.
