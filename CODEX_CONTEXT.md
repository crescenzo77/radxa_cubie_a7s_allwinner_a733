# Codex Context Contract

This repo is the canonical context source for homelab agents.

Codex/Aider/OpenCode must treat these files as project memory:

- `AGENTS.md` — standing rules for agent behavior
- `CODEX_CONTEXT.md` — context contract for Codex/Aider/OpenCode
- `CURRENT_SLICE.md` — current work item and boundaries
- `AGENT_STATUS.md` — latest known state
- `DECISIONS.md` — durable architectural decisions
- `HOMELAB_LAYOUT.md` — where systems live and why
- `WORKFLOW.md` — how operator workflow is supposed to run
- `ROADMAP.md` — prioritized future work

## Required behavior

Before making changes, the agent must read:

1. `AGENTS.md`
2. `CODEX_CONTEXT.md`
3. `CURRENT_SLICE.md`
4. `AGENT_STATUS.md`

If the task touches architecture, routing, service placement, workflow, model selection, security posture, or migration strategy, the agent must also read:

1. `HOMELAB_LAYOUT.md`
2. `WORKFLOW.md`
3. `ROADMAP.md`
4. `DECISIONS.md`

## Planning-change rule

If the agent changes any of the following, it must update the relevant repo docs in the same diff before continuing:

- plan
- scope
- architecture
- acceptance criteria
- risk assessment
- current slice
- next action
- rollback path
- operational assumptions
- service ownership
- model routing
- security posture

A plan change that is not reflected in the repo is incomplete.

## Execution boundaries

The agent must not perform live service changes unless explicitly instructed.

Live service changes include:

- editing production config files outside this repo
- restarting Docker containers
- changing systemd units or timers
- changing OpenCode, Open WebUI, LiteLLM, DNS, dashboard, or MCP live config
- deleting or moving service data
- altering secrets or `.env` files

For live changes, the agent must first produce:

1. intended change
2. files or services affected
3. rollback path
4. validation command
5. exact command block

Then stop for operator approval.

## Preferred working pattern

The agent should work in small, reviewable steps:

1. inspect
2. summarize findings
3. propose change
4. edit repo docs or code
5. show diff
6. stop for review

Do not chain unrelated tasks in one run.

## Role split

WebUI is the strategic supervisor.

Codex is primary for planning, sequencing, approval briefs, and risky
live-service work.

Aider is the bounded patch assistant for small, already-planned repo edits.

OpenCode is a later local-agent experiment, not the assumed default executor.

Continue.dev is editor assist, and Cline is sandbox-only.

The repo is the shared memory layer.

If Codex, Aider, or OpenCode is uncertain, it should write the uncertainty into
`AGENT_STATUS.md` instead of guessing.
