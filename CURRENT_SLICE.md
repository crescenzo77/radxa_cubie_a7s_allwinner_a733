# Current Slice

## Slice 7: Transition OpenCode and Open WebUI away from LiteLLM active path

Update the homelab documentation to reflect the planned transition away from LiteLLM as the active routing layer.

## Purpose

LiteLLM is no longer the target active routing layer for OpenCode or Open WebUI.

The useful part of the current setup is the OpenRouter free-model discovery and free-only filtering. That mechanism should be preserved, but the generated output should target OpenCode-safe provider config instead of LiteLLM config.

## Target direction

OpenCode should use:

- direct local-coder by default
- generated OpenRouter-free provider only as manual fallback
- no broad paid OpenRouter catalog
- no automatic cloud fallback
- no direct paid-provider API automation

Open WebUI should use:

- direct local model endpoints
- no required LiteLLM routing layer

LiteLLM should be:

- removed from the active path after testing
- kept temporarily for rollback
- not deleted immediately

## Requirements

Update documentation so it clearly says:

- LiteLLM is being phased out of the active OpenCode/OpenWebUI path.
- OpenRouter free-model discovery remains valuable and should be preserved.
- The free-model refresh output should move toward neutral artifacts under `/srv/openrouter-free/`.
- OpenCode should default to local-coder directly.
- OpenRouter fallback in OpenCode should be manual and generated free-only.
- Open WebUI should move back to direct local endpoints.
- LiteLLM should remain available temporarily for rollback only.

## Constraints

- Documentation only.
- No service changes yet.
- No config changes yet.
- No OpenCode config edits yet.
- No Open WebUI config edits yet.
- Do not stop or delete LiteLLM yet.
- Do not remove OpenRouter fallback.
- Do not create a custom router.

## Acceptance Criteria

- `PROJECT_PLAN.md` reflects the new transition away from LiteLLM active path.
- `DECISIONS.md` records the transition decision.
- `HOMELAB_LAYOUT.md`, `WORKFLOW.md`, and `ROADMAP.md` no longer describe LiteLLM as the long-term required routing layer.
- `AGENT_STATUS.md` summarizes the current state and next action.
- Changes are committed to Git.
