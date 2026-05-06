# Agent Status

## Current status

Slice 8 inventory is complete. Current OpenCode, Open WebUI, LiteLLM, OpenRouter refresh, and direct local endpoint state has been captured.

## Current slice

Slice 8: inventory current OpenCode, Open WebUI, and LiteLLM configuration.

## Files changed in current uncommitted work

- `ROUTING_INVENTORY.md`
- `AGENT_STATUS.md`

## Key findings

- OpenCode currently still routes through LiteLLM.
- Open WebUI currently still routes through LiteLLM.
- LiteLLM is running on ThinkCentre using `ghcr.io/berriai/litellm:main-latest`.
- OpenRouter free-model refresh is active and working.
- The useful free-model filtering logic lives in `/srv/litellm/render-config.py`.
- All direct local endpoints on AMD and Strix are healthy.

## Risks or blockers

LiteLLM is still live and should not be stopped yet. The next slice should migrate free-model discovery output to neutral `/srv/openrouter-free/` artifacts before touching OpenCode or Open WebUI config.

## Recommended next action

Review and commit the routing inventory, then plan the neutral OpenRouter-free artifact generation slice.
