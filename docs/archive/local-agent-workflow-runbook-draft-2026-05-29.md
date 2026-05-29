# Local Agent Workflow Runbook

## Purpose

Use this runbook when a local or optional free-cloud model is helping with a
repository change. The goal is a repeatable human-approved loop:

```text
planner/advisor defines one bounded task
  -> patch tool edits only the selected repo and files
  -> reviewer inspects the Git diff
  -> user chooses Commit, Revise, Revert, or Inspect more
```

The patch tool does not plan the work, approve its own output, change services,
or commit by default.

## Supported Current Paths

### Planner / Advisor

- Codex Desktop on the Mac mini for planning, operator steps, and review.
- ChatGPT for planning or second-opinion review.
- Open WebUI through ThinkCentre model-dispatch for local advisor/reviewer
  prompts.

Recommended local advisor aliases:

- `local/strix-reasoning` for long-context reasoning and review.
- `local/strix-coder` for code-oriented local review or patch prompts.
- `local/amd-coder` for faster code-oriented local review or patch prompts.

### Patch Tool

Validated bounded patch paths:

- Aider against Strix Coder-Next llama.cpp:
  - host: `strix`
  - endpoint: `http://127.0.0.1:8082/v1`
  - helper: `scripts/aider-strix-coder-llamacpp`
- Aider against AMD coder through model-dispatch:
  - endpoint: `http://192.168.50.225:4010/v1`
  - model: `openai/local/amd-coder`

Both paths are validated only as bounded patch tools. They are not autonomous
coders, planners, deployment tools, or approval systems.

### Reviewer

Reviewer options:

- Codex Desktop.
- ChatGPT.
- Open WebUI with a local model.
- OpenRouter free model only when explicitly selected and tested.

The reviewer inspects the diff and recommends one user decision. It does not
approve automatically.

## Bounded Task Prompt Template

Use a prompt shaped like this for any patch tool:

```text
Repo: /srv/projects/<repo>
Task: <one specific change>
Files in scope: <exact file list or tightly bounded path>
Out of scope: services, Docker, systemd, routing, secrets, deployment,
unrelated formatting, broad rewrites, commits
Checks to run: <commands>
Stop after one reviewable Git diff. Do not commit.
```

## Aider Command Templates

Run Aider from the target repository working tree.

### Strix Coder-Next

```sh
cd /srv/projects/<repo>
/srv/projects/homelab/scripts/aider-strix-coder-llamacpp <file> \
  --message "Edit <file> only. Make the requested bounded change. Do not commit."
```

The helper checks that Strix Coder-Next is live on `127.0.0.1:8082`.

### AMD Coder Through Model-Dispatch

```sh
cd /srv/projects/<repo>
/home/enzo/.local/bin/aider <file> \
  --model openai/local/amd-coder \
  --openai-api-base http://192.168.50.225:4010/v1 \
  --openai-api-key dummy \
  --edit-format diff \
  --no-stream \
  --map-tokens 0 \
  --no-auto-commits \
  --no-gitignore \
  --yes-always \
  --input-history-file /tmp/aider-amd-input.history \
  --chat-history-file /tmp/aider-amd-chat.history.md \
  --llm-history-file /tmp/aider-amd-llm.history \
  --message "Edit <file> only. Make the requested bounded change. Do not commit."
```

Use `--yes-always` only for a tightly bounded non-interactive run where the file
scope is already explicit.

## Model Smoke Checks

Before relying on a local patch path, prove the model alias can answer through
model-dispatch:

```sh
cd /srv/projects/homelab
scripts/model-tool-loop-smoke --model local/amd-coder
scripts/model-tool-loop-smoke --model local/strix-coder
```

For Strix direct Aider use, also confirm the helper can reach
`127.0.0.1:8082`.

## Review Bundle

After the patch tool exits, run this in the target repo:

```sh
git status --short
git diff --check
git diff --stat
git diff
```

For code changes, also run the smallest relevant syntax, unit, or smoke check.
If no check exists, say that explicitly during review.

## Review Questions

The reviewer should answer:

- What changed?
- Did the diff stay inside the named scope?
- Did checks pass?
- Were services, secrets, routes, Docker, systemd, deployment, or unrelated
  files touched?
- Is the recommendation Commit, Revise, Revert, or Inspect more?

## User Decision

The user chooses one:

- `Commit`: commit the reviewed diff with a concise message.
- `Revise`: keep the diff and make a smaller follow-up correction.
- `Revert`: discard the diff before moving on.
- `Inspect more`: run more commands or ask another reviewer before deciding.

Do not commit until the user approves.

## Current Non-Working Or Unproven Paths

- OpenCode is installed on Strix but blocked for local model patching. It can
  list configured local models, but `opencode run` produced no visible model
  output or edits through AMD or Strix local models.
- Codex with a local model-dispatch provider is unproven.
- `local/amd-small` is not clean-agent-ready because it emitted reasoning
  content instead of clean final content on a tiny prompt.

Treat each as a separate future debugging or validation slice.

## Optional OpenRouter Free Path

OpenRouter free models are optional and explicit only.

- Do not route to paid OpenRouter models automatically.
- Do not use OpenRouter as a hidden fallback.
- Validate a free model first as an advisor or reviewer.
- Do not use it as a patch tool until a separate bounded patch validation
  proves the path.

## Hard Boundaries

Do not let any patch-tool run change:

- services
- Docker or systemd
- model-dispatch defaults
- Open WebUI defaults
- network routing
- secrets or `.env` files
- deployments
- hidden automations, daemons, watchers, or approval flows
- broad repo structure or unrelated formatting

If a task needs one of those, stop and make it an explicit user-approved slice.
