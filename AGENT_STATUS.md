# Agent Status

## Current status

Slice 7 is active. The homelab docs are being updated to reflect the planned transition away from LiteLLM as the active routing layer.

## Current slice

Slice 7: transition OpenCode and Open WebUI away from LiteLLM active path.

## Files changed in current uncommitted work

- `PROJECT_PLAN.md`
- `DECISIONS.md`
- `AGENT_STATUS.md`

## Decision being recorded

LiteLLM should be phased out of the active OpenCode/OpenWebUI path. The OpenRouter free-model discovery and free-only filtering mechanism should be preserved and moved toward neutral generated artifacts under `/srv/openrouter-free/`.

## Risks or blockers

The layout, workflow, and roadmap docs still need to be updated after this decision is committed.

## Recommended next action

Review and commit this decision-state update, then update `HOMELAB_LAYOUT.md`, `WORKFLOW.md`, and `ROADMAP.md`.
