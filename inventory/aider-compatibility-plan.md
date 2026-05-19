# Aider Compatibility Plan

## Purpose

Plan how to diagnose why Aider receives empty responses from local
`model-dispatch` aliases. This is a documentation-only planning slice. Do not
run more Aider trials yet.

## Observed Failures

- Aider version `0.86.2` is installed.
- Aider can start from `/srv/projects/homelab`.
- Aider can be constrained to one file.
- Aider asked to add extra files and the user rejected or skipped them.
- Aider trials using local `model-dispatch` aliases failed with empty
  responses:
  - `openai/coding`
  - `openai/local/amd-coder`
- The AMD containers were healthy during the failures:
  - `qwen3-coder-30b`
  - `gemma4-7900xt`
- Previous normal chat-completion validation for `local/amd-coder` succeeded
  through `model-dispatch`, so the failure may be specific to Aider's request
  pattern, model metadata expectations, edit format, or provider handling.

## Hypotheses

- Aider expects a response format or behavior not satisfied by
  `model-dispatch` or the local llama.cpp response.
- The `model-dispatch` alias works for normal chat completion but may not
  satisfy Aider's edit format expectations.
- Generic route aliases such as `coding` may be less compatible than direct
  explicit model IDs.
- Aider may need model metadata, an edit format override, or provider
  configuration for local OpenAI-compatible endpoints.
- Aider may send request fields that the local backend ignores, rejects, or
  handles differently than OpenAI-compatible clients expect.
- Aider may request streaming, tool-like behavior, reasoning metadata, or
  structured edit output that is not preserved by the current dispatch path.
- Aider's LiteLLM model naming path may treat `openai/coding` differently than
  a direct OpenAI-compatible `--openai-api-base` plus explicit model name.

## What To Inspect First

- Aider local configuration and environment variables, without changing them:
  - model name passed to Aider
  - API base URL
  - API key placeholder behavior
  - edit format settings
  - weak model or editor model settings
  - any `.aider*` repo or user config files
- Aider documentation for local OpenAI-compatible models, edit formats, model
  metadata, and provider configuration.
- The exact request and response shape expected by Aider for the selected model
  type.
- Existing repo notes that record validated `model-dispatch` aliases and direct
  AMD endpoints.
- Whether Aider has a known model settings registry entry for the local model
  IDs or needs an explicit override.

## Local Model-Dispatch Compatibility Checks

These checks are for a later validation slice. They inspect the compatibility
surface without running Aider.

- Confirm `/v1/models` exposes both generic aliases and direct local aliases:
  - `coding`
  - `local/amd-coder`
  - any explicit AMD model ID exposed by the dispatcher
- Compare a minimal chat-completion request against an Aider-like request using
  the same `model-dispatch` alias.
- Check whether responses include a non-empty `choices[0].message.content`.
- Check whether responses include fields Aider or LiteLLM may expect, such as
  `id`, `object`, `created`, `model`, `choices`, `finish_reason`, and `usage`.
- Check whether `stream: false` and any Aider-like parameters are forwarded in a
  way local backends accept.
- Prefer direct explicit model IDs for the first compatibility check before
  generic route aliases.

## Direct AMD Endpoint Compatibility Checks

These checks are for a later validation slice. They compare `model-dispatch`
behavior with the direct AMD OpenAI-compatible endpoint without editing AMD
services.

- Query the direct AMD endpoint's `/v1/models`.
- Run the same minimal chat-completion payload used against `model-dispatch`.
- Run the same Aider-like non-streaming payload used against `model-dispatch`.
- Compare response status, JSON shape, content length, finish reason, and usage
  fields.
- If direct AMD succeeds but `model-dispatch` fails, inspect the dispatcher
  normalization path in a separate source-repo slice before touching live
  config.
- If both direct AMD and `model-dispatch` return empty content for the
  Aider-like payload, focus on Aider model settings, edit format, and local
  backend support.

## Verified OpenRouter-Free Fallback Test Option

A later slice may test Aider against a verified free OpenRouter model from the
existing allowlist only if local checks do not identify the issue.

Rules:

- Use only a verified free OpenRouter model already present in the allowlist.
- Do not expose the broad paid OpenRouter catalog.
- Do not recommend paid frontier models for Aider, OpenCode, Cline, or other
  non-Codex agents.
- Keep the test bounded to one repo, one file, and one reviewable diff.
- Prefer a dry compatibility check before any Aider edit trial.

## What Not To Do

- Do not run Aider in this planning slice.
- Do not run additional Aider trials until a later validation slice.
- Do not edit `/srv/model-dispatch`.
- Do not edit `/srv/projects/model-dispatch`.
- Do not restart services.
- Do not change OpenCode, Continue.dev, Open WebUI, LiteLLM, dashboards,
  monitoring, or observability.
- Do not add wrappers, daemons, watchers, hidden jobs, approval automation, or
  MCP failure-supervision.
- Do not recommend paid frontier models for non-Codex agents.
- Do not commit as part of this slice.

## Validation Commands For A Later Slice

These commands are examples for a later validation slice. Confirm endpoints and
approval boundaries before running them.

```sh
aider --version
```

```sh
curl -sS http://192.168.50.225:4010/v1/models
```

```sh
curl -sS http://192.168.50.225:4010/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "local/amd-coder",
    "stream": false,
    "messages": [
      {"role": "user", "content": "Reply with exactly: ok"}
    ]
  }'
```

```sh
curl -sS http://192.168.50.225:4010/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "coding",
    "stream": false,
    "messages": [
      {"role": "system", "content": "You are a coding assistant."},
      {"role": "user", "content": "Return a short unified diff that changes one markdown heading."}
    ]
  }'
```

```sh
curl -sS <direct-amd-openai-compatible-base>/v1/models
```

```sh
curl -sS <direct-amd-openai-compatible-base>/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "<direct-amd-model-id>",
    "stream": false,
    "messages": [
      {"role": "user", "content": "Reply with exactly: ok"}
    ]
  }'
```

```sh
aider --model openai/local/amd-coder --show-model-warnings
```

```sh
aider --model openai/local/amd-coder --edit-format diff --show-model-warnings
```

Do not run the Aider commands above until the later slice explicitly authorizes
new Aider trials.
