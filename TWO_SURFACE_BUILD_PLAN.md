# Two-Surface Build Plan

## Purpose

Build a practical homelab workflow with two human-operated surfaces:

1. A web UI advisor/planner in Open WebUI.
2. A self-hosted coding agent on the coding PC or project host.

The bridge between them is a small local script, `advisor-packet`, that creates a compact markdown packet from project state. The purpose is to reduce copy/paste and context bloat, not to create autonomous supervision.

The user remains the final decision-maker. The system does not auto-approve coder actions.

## Target Architecture

```text
Framework laptop or other thin client
  -> Browser: Open WebUI advisor on thinkcentre
  -> SSH / VS Code Remote-SSH: project host

Project host
  -> Shared markdown state files
  -> Git history and diffs
  -> advisor-packet script
  -> OpenCode or Aider through LiteLLM

ThinkCentre
  -> LiteLLM at http://192.168.50.225:4000/v1
  -> Open WebUI at http://192.168.50.225:3000
  -> OpenRouter free-only fallback through LiteLLM

AMD
  -> Current OpenCode execution host
  -> RTX 3090 primary local coder model
  -> RX 7900 XT backup model

Strix
  -> Target canonical source host at /srv/projects/<project-name>/
  -> Reasoning/testbed inference
```

Codex may be used manually during setup work, but it must not become infrastructure.

## Files To Create

In the canonical homelab repo:

- `PROJECT_PLAN.md`
- `CURRENT_SLICE.md`
- `DECISIONS.md`
- `AGENT_STATUS.md`
- `AGENTS.md`
- `HOMELAB_LAYOUT.md`
- `WORKFLOW.md`
- `ROADMAP.md`

Local tool:

- `advisor-packet`

The script can live in the homelab repo first. Later it can be installed somewhere on `PATH` if that proves useful.

## Slice 1: Canonical Homelab Repo

Create:

```text
strix:/srv/projects/homelab/
```

Add the operating files and seed the docs from the two-surface versions.

Acceptance criteria:

- The repo exists on Strix.
- The operating files are committed.
- The docs identify AMD as current coding execution host, ThinkCentre as LiteLLM/Open WebUI host, Strix as target canonical source host, and Framework as thin client.
- No Codex automation is introduced.

## Slice 2: `advisor-packet`

Implement a small local script that prints bounded markdown.

Required inputs:

- `CURRENT_SLICE.md`
- `DECISIONS.md`
- `AGENT_STATUS.md`
- `AGENTS.md`
- Git status
- Git diff stat
- Bounded git diff excerpt
- Bounded recent coder log, if present

Acceptance criteria:

- Runs without network access.
- Produces output that can be pasted into Open WebUI.
- Bounds large sections by default.
- Uses only local files and git commands.
- Does not call any model API.
- Does not approve or reject coder actions.

## Slice 3: Agent Rules

Write `AGENTS.md` so OpenCode/Aider know how to work in the repo.

Required rules:

- Stay within `CURRENT_SLICE.md`.
- Keep changes narrow.
- Do not broaden scope without asking.
- Update `AGENT_STATUS.md` before handoff.
- Include files changed, tests/checks run, risks, and next proposed action.
- Treat the user as final approver.

Acceptance criteria:

- The coder produces a useful handoff brief.
- The advisor can understand state from `advisor-packet` without raw terminal logs.

## Slice 4: End-to-End Trial

Use the loop on one small real task.

Steps:

1. Write the slice in `CURRENT_SLICE.md`.
2. Run `advisor-packet`.
3. Paste packet into Open WebUI.
4. Ask advisor for a bounded coder prompt.
5. Run OpenCode or Aider on the project host.
6. Review git diff.
7. Decide whether to accept, revise, or reject.
8. Commit if accepted.

Acceptance criteria:

- One real change completes through the loop.
- User reviews the diff before commit.
- Any friction is documented.
- No autonomous supervision is added.

## Slice 5: Choose Preferred Coder

Evaluate OpenCode and Aider on real tasks.

Acceptance criteria:

- `DECISIONS.md` records whether OpenCode or Aider is preferred.
- The choice favors local/self-hosted LiteLLM where possible.
- The non-preferred tool remains manual fallback if useful.
- No paid-provider automation is required.

## Slice 6: Optional Improvements

Only after the basic loop proves useful, consider:

- tmux logging for coder sessions.
- A known coder log path for `advisor-packet`.
- Continue.dev review cleanup through LiteLLM labels.
- Convenience install path for `advisor-packet`.

Acceptance criteria:

- The improvement addresses observed friction.
- It remains local and understandable.
- It does not create a daemon, watcher, autonomous supervisor, or paid API automation.

## Explicitly Out of Scope

- Codex as infrastructure.
- Codex API calls.
- Claude/Codex automation wrappers.
- Scheduled AI jobs.
- Background approval jobs.
- Custom approval daemons.
- Hidden watcher agents.
- MCP failure-supervision.
- Paid OpenRouter automation.
- Any workflow that moves canonical state onto the Framework laptop.
- Large bespoke orchestration when markdown, git, LiteLLM, Open WebUI, OpenCode, and Aider are sufficient.
