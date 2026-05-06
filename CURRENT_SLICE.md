# Current Slice

## Slice 10: Verify OpenCode environment-variable interpolation

Verify OpenCode environment-variable interpolation without changing live OpenCode, Open WebUI, or LiteLLM configuration.

## Purpose

Slice 9 created neutral OpenRouter-free generated artifacts under `/srv/openrouter-free/`.

Before any generated OpenCode artifact can be wired into live config, OpenCode must be verified to support the generated API key placeholder:

```json
"apiKey": "{env:OPENROUTER_API_KEY}"
```

## Scope

Verification only:

- Inspect OpenCode documentation or local installed package behavior.
- Inspect generated `/srv/openrouter-free/opencode.generated.json`.
- Inspect AMD OpenCode config.
- Create a throwaway test config if needed.
- Do not alter `/home/enzo/.config/opencode/opencode.json`.
- Do not change OpenCode live provider settings.
- Do not call paid OpenRouter models.
- Do not alter LiteLLM or Open WebUI.

## Constraints

- Do not stop LiteLLM.
- Do not edit live OpenCode config.
- Do not edit live Open WebUI config.
- Do not alter systemd timers.
- Do not remove OpenRouter fallback.
- Do not expose paid OpenRouter models.
- Do not build a general router.
- Do not create a daemon or watcher.
- Do not make live production changes based on network responses without explicit approval.

## Acceptance Criteria

- Determine whether `"apiKey": "{env:OPENROUTER_API_KEY}"` is valid for OpenCode.
- Document the result and next action.
- No live services or configs are changed.
- Git diff is shown for review.
- Stop before commit.
