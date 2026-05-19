# Aider Compatibility Read-Only Inspection

## Purpose

Inspect why Aider received empty responses from local `model-dispatch` aliases
by comparing OpenAI-compatible response shapes from:

- `model-dispatch` aliases that Aider used.
- The direct AMD Qwen3 Coder OpenAI-compatible endpoint.

This inspection is read-only. It does not run Aider, edit services, restart
services, or change any client configuration.

## Endpoints Inspected

| Endpoint | Base URL | Purpose |
|---|---|---|
| `model-dispatch` | `http://192.168.50.225:4010/v1` | Active routing layer used by aliases such as `coding` and `local/amd-coder`. |
| Direct AMD Qwen3 Coder | `http://192.168.50.252:8083/v1` | Direct backend endpoint used to compare whether the empty-response behavior exists below `model-dispatch`. |

## Exact Read-Only Commands To Run Manually

Run these from any shell that can reach both endpoints. They only read model
lists and request non-streaming chat completions.

### 1. Inspect `model-dispatch` model list

```sh
curl -sS http://192.168.50.225:4010/v1/models | python3 -m json.tool
```

What this proves:

- Whether `model-dispatch` exposes the aliases Aider tried.
- Whether `coding` and `local/amd-coder` appear in `/v1/models`.
- Whether the model list response has OpenAI-compatible top-level shape.

Expected response fields:

- `object`
- `data`
- each `data[]` item should include at least `id` and `object`

### 2. Inspect direct AMD model list

```sh
curl -sS http://192.168.50.252:8083/v1/models | python3 -m json.tool
```

What this proves:

- Whether the direct AMD endpoint is reachable.
- Which exact model ID the backend advertises.
- Whether the direct backend model list has OpenAI-compatible top-level shape.

Expected response fields:

- `object`
- `data`
- each `data[]` item should include at least `id` and `object`

### 3. Capture the first direct AMD model ID

```sh
AMD_MODEL="$(curl -sS http://192.168.50.252:8083/v1/models | python3 -c 'import json,sys; data=json.load(sys.stdin); print(data["data"][0]["id"])')"; printf '%s\n' "$AMD_MODEL"
```

What this proves:

- The direct AMD endpoint returned parseable JSON.
- The next direct AMD calls use the backend's advertised model ID instead of a
  guessed name.

Expected response fields:

- The source `/v1/models` response should include `data[0].id`.

### 4. Minimal `model-dispatch` check for `local/amd-coder`

```sh
curl -sS http://192.168.50.225:4010/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "local/amd-coder",
    "stream": false,
    "temperature": 0,
    "messages": [
      {"role": "user", "content": "Reply with exactly: ok"}
    ]
  }' | python3 -m json.tool
```

What this proves:

- Whether the `local/amd-coder` alias can produce a normal non-empty chat
  completion through `model-dispatch`.
- Whether `model-dispatch` returns a JSON object rather than an empty body or
  streamed event data.

Expected response fields:

- `id`
- `object`
- `created`
- `model`
- `choices`
- `choices[0].index`
- `choices[0].message.role`
- `choices[0].message.content`
- `choices[0].finish_reason`
- `usage`, if the backend reports token usage

### 5. Minimal `model-dispatch` check for `coding`

```sh
curl -sS http://192.168.50.225:4010/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "coding",
    "stream": false,
    "temperature": 0,
    "messages": [
      {"role": "user", "content": "Reply with exactly: ok"}
    ]
  }' | python3 -m json.tool
```

What this proves:

- Whether the generic `coding` alias behaves differently from
  `local/amd-coder`.
- Whether alias routing changes response fields, model names, or content.

Expected response fields:

- Same fields as the `local/amd-coder` chat-completion check.
- `choices[0].message.content` should be non-empty.

### 6. Minimal direct AMD check

```sh
curl -sS http://192.168.50.252:8083/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d "{
    \"model\": \"${AMD_MODEL}\",
    \"stream\": false,
    \"temperature\": 0,
    \"messages\": [
      {\"role\": \"user\", \"content\": \"Reply with exactly: ok\"}
    ]
  }" | python3 -m json.tool
```

What this proves:

- Whether the direct AMD endpoint can produce a normal non-empty chat
  completion without `model-dispatch`.
- Whether the direct backend response shape differs from the dispatcher
  response shape.

Expected response fields:

- Same chat-completion fields as above.
- `choices[0].message.content` should be non-empty.

### 7. Aider-like diff request through `model-dispatch` `local/amd-coder`

```sh
curl -sS http://192.168.50.225:4010/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "local/amd-coder",
    "stream": false,
    "temperature": 0,
    "messages": [
      {"role": "system", "content": "You are a coding assistant. Return only a unified diff."},
      {"role": "user", "content": "Create a unified diff that changes a markdown heading from Old Title to New Title."}
    ]
  }' | python3 -m json.tool
```

What this proves:

- Whether a coding/edit-style prompt returns non-empty content through the
  dispatcher.
- Whether the response has the same shape as the minimal prompt.

Expected response fields:

- Same chat-completion fields as above.
- `choices[0].message.content` should contain text, ideally a diff-like answer.

### 8. Aider-like diff request through `model-dispatch` `coding`

```sh
curl -sS http://192.168.50.225:4010/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "coding",
    "stream": false,
    "temperature": 0,
    "messages": [
      {"role": "system", "content": "You are a coding assistant. Return only a unified diff."},
      {"role": "user", "content": "Create a unified diff that changes a markdown heading from Old Title to New Title."}
    ]
  }' | python3 -m json.tool
```

What this proves:

- Whether the generic alias behaves differently from the direct local alias on
  an edit-style prompt.
- Whether the empty-response behavior is tied to generic alias routing.

Expected response fields:

- Same chat-completion fields as above.
- `choices[0].message.content` should be non-empty.

### 9. Aider-like diff request through direct AMD

```sh
curl -sS http://192.168.50.252:8083/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d "{
    \"model\": \"${AMD_MODEL}\",
    \"stream\": false,
    \"temperature\": 0,
    \"messages\": [
      {\"role\": \"system\", \"content\": \"You are a coding assistant. Return only a unified diff.\"},
      {\"role\": \"user\", \"content\": \"Create a unified diff that changes a markdown heading from Old Title to New Title.\"}
    ]
  }" | python3 -m json.tool
```

What this proves:

- Whether the direct backend can handle the same edit-style prompt.
- Whether any empty or malformed response appears without the dispatcher.

Expected response fields:

- Same chat-completion fields as above.
- `choices[0].message.content` should be non-empty.

## How To Compare `model-dispatch` Vs Direct AMD

For each chat-completion response, compare:

- HTTP success or failure.
- Whether the body is parseable JSON.
- Top-level fields: `id`, `object`, `created`, `model`, `choices`, `usage`.
- `choices` length.
- `choices[0].message.role`.
- `choices[0].message.content` presence and length.
- `choices[0].finish_reason`.
- Whether `usage` is present, omitted, or malformed.
- Whether the `model` field changes unexpectedly across aliases.
- Whether minimal prompts work while edit-style prompts produce empty content.

The most important field is `choices[0].message.content`. Aider's observed
failure was an empty response, so a response can be transport-successful but
still incompatible if this field is missing, null, or an empty string.

## What Would Indicate A `model-dispatch` Issue

Likely `model-dispatch` issue:

- Direct AMD returns non-empty `choices[0].message.content`, but
  `model-dispatch` returns missing, null, or empty content for the same prompt.
- Direct AMD returns valid chat-completion JSON, but `model-dispatch` returns
  malformed JSON, an empty body, or a non-chat-completion shape.
- `local/amd-coder` works directly or through one alias, but `coding` fails.
- `model-dispatch` changes `finish_reason`, `choices`, or `message` structure
  in a way the direct backend does not.
- The dispatcher model list advertises an alias that cannot complete a basic
  non-streaming chat request.

## What Would Indicate A Direct Backend Issue

Likely direct backend issue:

- Direct AMD and `model-dispatch` both return empty content for the same
  minimal prompt.
- Direct AMD and `model-dispatch` both return empty content for edit-style
  prompts while preserving similar response shape.
- Direct AMD returns malformed JSON, no `choices`, no `message`, or an empty
  body.
- Direct AMD only works with one style of prompt but fails with simple coding
  or diff instructions.

## What Would Indicate An Aider Configuration Or Edit-Format Issue

Likely Aider configuration or edit-format issue:

- All manual `curl` checks return valid JSON with non-empty
  `choices[0].message.content`.
- `coding`, `local/amd-coder`, and direct AMD all handle both minimal and
  edit-style prompts.
- The response shape is compatible enough for normal OpenAI-style clients, but
  Aider still reports empty responses when run in a separate authorized slice.
- The model ID that Aider uses differs from the model ID validated manually.
- Aider expects a specific edit format, model metadata entry, weak model,
  editor model, or provider configuration that is not declared for
  `openai/coding` or `openai/local/amd-coder`.

Do not test these Aider hypotheses in this slice. Record them for the next
explicit Aider-trial slice if the read-only inspection does not identify a
dispatcher or backend response-shape problem.

## Next Action After Inspection

After the manual read-only commands are run, record the observed response
shapes in a follow-up status update or inspection-results document.

Recommended next decision:

- If direct AMD succeeds and `model-dispatch` fails, open a separate
  source-repo inspection slice for `/srv/projects/model-dispatch`; do not edit
  live `/srv/model-dispatch`.
- If both direct AMD and `model-dispatch` fail, inspect the AMD backend model
  serving behavior in a separate operations-approved slice.
- If both endpoints succeed with non-empty compatible responses, plan a separate
  Aider configuration slice focused on model metadata, edit format, and exact
  provider settings before running any new Aider edit trial.
