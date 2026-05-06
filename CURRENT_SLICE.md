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
- Inspect generated `/srv/openrouter-free/opencode.generated.json` if reachable.
- Inspect AMD OpenCode config over read-only SSH if reachable.
- Create a throwaway local test config if needed, but stop before executing anything networked.
- Do not alter `/home/enzo/.config/opencode/opencode.json`.
- Do not change OpenCode live provider settings.
- Do not call paid OpenRouter models.
- Do not alter LiteLLM or Open WebUI.

## Constraints

- Do not edit live OpenCode config.
- Do not edit Open WebUI config.
- Do not alter LiteLLM.
- Do not change OpenCode provider settings.
- Do not call paid OpenRouter models.
- Do not make live service changes.
- Use read-only inspection only.
- Do not make live production changes based on network responses without explicit approval.

## Result

OpenCode documentation confirms that `{env:VARIABLE_NAME}` is valid variable substitution syntax in config files, including provider `options.apiKey`.

Therefore, this placeholder is valid OpenCode syntax:

```json
"apiKey": "{env:OPENROUTER_API_KEY}"
```

If `OPENROUTER_API_KEY` is unset, OpenCode replaces the placeholder with an empty string.

## Current Limitation

Normal SSH aliases still failed inside this Codex execution environment before remote inspection could run:

```text
Bad owner or permissions on /etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf
```

Because of that, this slice verified syntax from official OpenCode documentation but did not inspect the remote generated artifact or AMD live OpenCode config in this run.

## Acceptance Criteria

- Determine whether `"apiKey": "{env:OPENROUTER_API_KEY}"` is valid for OpenCode.
- Document the result and next action.
- No live services or configs are changed.
- Git diff is shown for review.
- Stop before commit.
