# Agent Status

## Current status

Slice 16 is ready to synchronize homelab architecture docs with the new live OpenCode routing state.

## Current slice

Slice 16: synchronize architecture docs with live OpenCode state.

## Why this is needed

The deployed OpenCode routing path changed during Slices 14 and 15.

The repo must now be updated so:

```text
repo docs == actual deployed state
```

Without this update:

- agents receive stale routing assumptions
- future migrations become harder to reason about
- rollback paths become less trustworthy
- architecture docs drift from reality

## Current live state

AMD OpenCode:

- default provider: `homelab-local`
- default execution path: direct AMD local 3090
- manual provider: `homelab-openrouter-free`
- OpenRouter usage: manual-only
- automatic cloud fallback: disabled

LiteLLM:

- still active
- still used by Open WebUI
- retained for rollback
- no longer default OpenCode path

## Files that require updates

- `HOMELAB_LAYOUT.md`
- `WORKFLOW.md`
- `ROADMAP.md`
- `OPENROUTER_FREE_ARTIFACT_PLAN.md`
- `ROUTING_INVENTORY.md`

## Constraints

This slice is documentation-only.

No:

- live config edits
- service restarts
- OpenRouter calls
- OpenCode changes
- LiteLLM changes
- Open WebUI changes
- remote mutation

## Recommended next action

Transfer these files into `strix:/srv/projects/homelab/`, commit the slice transition, then perform documentation edits only.
