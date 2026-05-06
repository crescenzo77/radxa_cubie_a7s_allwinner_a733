# Current Slice

## Slice 12: Draft OpenCode direct-provider migration

Prepare a non-live draft migration from the current OpenCode LiteLLM-only configuration to direct local and generated free-only providers.

## Purpose

Draft the OpenCode provider migration before making any live OpenCode, Open WebUI, or LiteLLM changes.

Target draft shape:

- Direct local provider for AMD `local-coder`.
- Generated `homelab-openrouter-free` provider for manual OpenRouter free-only use.

## Scope

Drafting and read-only inspection only:

- Inspect current AMD OpenCode config read-only using the normal SSH alias.
- Inspect `/srv/openrouter-free/opencode.generated.json` read-only using the normal SSH alias.
- Design a proposed `opencode.json` shape.
- Document rollback path.
- Do not edit `/home/enzo/.config/opencode/opencode.json`.
- Do not change OpenCode live provider settings.
- Do not alter LiteLLM or Open WebUI.
- Do not call any OpenRouter model.
- Do not make live service changes.

## Constraints

- Use read-only inspection only.
- Use normal SSH aliases if remote inspection is needed.
- Do not use `ssh -F /dev/null` unless a later SSH-readiness slice explicitly allows it.
- Do not edit live OpenCode config.
- Do not edit Open WebUI config.
- Do not alter LiteLLM.
- Do not change OpenCode provider settings.
- Do not call any OpenRouter model.
- Do not make live service changes.
- Do not print secrets.
- Do not make live production changes based on network responses without explicit approval.

## Acceptance Criteria

- Current AMD OpenCode config is inspected read-only if SSH is available.
- `/srv/openrouter-free/opencode.generated.json` is inspected read-only if SSH is available.
- A proposed non-live `opencode.json` shape is documented.
- Rollback path is documented.
- No live services or configs are changed.
- Git diff is shown for review.
- Stop before commit.
