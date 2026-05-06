# Current Slice

## Slice 9: Create neutral OpenRouter-free artifact generator

Create a neutral OpenRouter-free artifact generation plan before changing any live OpenCode, Open WebUI, or LiteLLM configuration.

## Purpose

The routing inventory showed that the useful part of the LiteLLM setup is the OpenRouter free-model discovery and zero-price filtering logic in `/srv/litellm/render-config.py`.

The target is to preserve that safety logic while moving generated output toward neutral artifacts under `/srv/openrouter-free/`.

## Scope

Planning and safe implementation prep only:

- Inspect OpenCode config format.
- Define neutral artifact paths under `/srv/openrouter-free/`.
- Define generated files:
  - `free-models.raw.json`
  - `free-models.allowlist.json`
  - `opencode.generated.json`
  - `openwebui.generated.env`
- Preserve zero-price filtering.
- Preserve fail-closed behavior.
- Do not alter live OpenCode or Open WebUI config yet.

## Constraints

- Do not stop LiteLLM.
- Do not edit OpenCode config yet.
- Do not edit Open WebUI config yet.
- Do not alter systemd timers yet.
- Do not remove OpenRouter fallback.
- Do not expose paid OpenRouter models.
- Do not build a general router.
- Do not create a daemon or watcher.

## Acceptance Criteria

- A clear artifact-generation plan exists in the repo.
- The plan explains source inputs, generated outputs, and safety rules.
- No live services or configs are changed.
- Next implementation step is clearly defined.
