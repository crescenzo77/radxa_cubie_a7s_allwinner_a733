# Aider Evaluation Plan

## Purpose

Evaluate Aider as the preferred steady-state coding agent for the two-surface homelab workflow.

Aider is being evaluated because it is Git-centered, terminal-based, and suited to bounded edits. The goal is to reduce confusing approval prompts and produce reviewable diffs.

## Boundary

Aider is not an automation layer.

Do not add:

- Paid-provider API automation.
- Codex automation.
- Claude Code automation.
- Scheduled jobs.
- Background workers.
- Wrappers that hide billing or model calls.
- Daemons or watchers.
- MCP failure-supervision.

## Preferred install model

Use an isolated user-level install.

Preferred candidates:

1. uv tool install aider-chat
2. pipx install aider-chat

Do not install into system Python with sudo pip.

## Target host

Initial evaluation should happen on strix because the canonical homelab repo lives at /srv/projects/homelab.

If Aider later becomes the steady-state coder for GPU-bound work, evaluate whether it should also be installed on amd.

## LiteLLM routing target

Aider should point at the Homelab LiteLLM OpenAI-compatible endpoint:

http://192.168.50.225:4000/v1

Aider should use local/self-hosted LiteLLM model labels where possible.

No direct OpenRouter endpoint should be configured in Aider.

## Test task

Use Aider on one small documentation-only task in this repo.

Candidate task:

Update DECISIONS.md with the Slice 5 decision framework:

- Aider is the preferred first candidate.
- OpenCode remains available as fallback.
- Final decision depends on a real bounded edit test.
- No paid API automation is allowed.

## Success criteria

Aider passes evaluation if it:

- Installs cleanly without system Python pollution.
- Can run inside /srv/projects/homelab.
- Can use the LiteLLM endpoint.
- Produces a small, reviewable Git diff.
- Respects CURRENT_SLICE.md and AGENTS.md.
- Updates AGENT_STATUS.md with a useful handoff.
- Does not require paid-provider API automation.

## Failure criteria

Aider fails evaluation if it:

- Requires awkward or fragile config.
- Cannot use LiteLLM cleanly.
- Produces broad or hard-to-review diffs.
- Ignores project instructions.
- Creates more confusion than OpenCode.
- Requires paid API keys or direct paid-provider setup.
