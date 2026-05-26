# Workflow: Two Surfaces Plus `advisor-packet`

This describes the normal working loop for homelab coding projects.

Last updated: 2026-05-23.

## Summary

The steady-state workflow is:

```text
Web UI advisor/planner
  + advisor-packet markdown summary
  + targeted evidence requests
  + exact commands or controlled manual edit steps
  + Review Coach diff explanation
  + user commit and push after review
```

The goal is to reduce copy/paste and context bloat. The goal is not autonomous supervision. The user remains responsible for approving direction, reviewing diffs, and deciding when work is done.

Codex remains the primary manual agent for planning, sequencing, approval
briefs, and risky live-service work. The core walking skeleton is manual and
safe: the planner asks for targeted evidence, gives exact commands or
controlled edit steps, the user runs them, the Review Coach explains diffs in
layman's terms, and the user commits and pushes after review.

Aider, OpenCode, and CodeGraphContext write workflows are evaluation-only for
now. OpenHuman is abandoned for the current phase because it creates
signup/service pressure. None of these tools may become infrastructure,
automation, or an approval system.

## Agent Division of Labor

Use agents by task shape, not by which one best fits the routing architecture.

| Agent | Role |
|---|---|
| Codex | Primary for planning, migration choreography, documentation slices, approval briefs, and risky live-service steps. |
| Claude Code | Strong frontier-code alternative and second opinion for difficult implementation or review. |
| Aider | Evaluation-only for bounded repo patch trials; not part of the core walking skeleton. |
| Hermes | Observer, summarizer, reviewer, recorder, and approved-skill-assisted preservation checker only; no canonical repo mutation or live-service action. |
| OpenCode | Later local-agent experiment; not the default or primary coder, and nothing should depend on it. |
| OpenHuman | Abandoned for the current phase because it creates signup/service pressure. |
| Continue.dev | Editor assist and review for selected code chunks. |
| Cline | Sandbox-only experimentation. |
| Review Coach | Explains diffs in layman's terms and ends with Commit, Revise, Revert, or Inspect more. |

Codex, Claude Code, and any evaluation agents are manually invoked tools. Do
not wrap them in daemons, scheduled jobs, hidden approval flows, paid-provider
automation, or repo-wide autonomous workflows.

## Aider Evaluation Boundary

Aider is evaluation-only for now. Do not make it required for the walking
skeleton, and do not depend on it for normal workflow edits.

Aider trials, when explicitly approved, must stay to one repo, one named-file
bounded edit, and one reviewable diff. Aider is not a planner, migration
controller, deployment tool, or architecture decision-maker.

Do not use Aider for:

- Core walking-skeleton workflow edits.
- Live deployment.
- Service restarts.
- Docker or systemd changes.
- Secrets or `.env` changes.
- Multi-host changes.
- Broad architecture decisions.

Aider output must be validated before commit. Review the diff and run the
slice's checks. Do not add Aider wrappers, default paths, or normal handoff
requirements around Aider.

For Aider model testing, prefer local LLMs or verified OpenRouter-free models
only. Qwen thinking-off or non-thinking mode is the baseline for patch
workflows. Reasoning-parser mode belongs in a separate review/architecture
validation path before it is considered for any coding workflow.

## Hermes Boundary

Hermes may observe, summarize, review, record preservation findings, and use
approved skills for read-only preservation checks. Hermes must not edit
canonical repositories, install live skills, restart services, change model
routing, supervise failures autonomously, or become an approval daemon.

## Codex-Assisted Deployment Rule

Codex can be used to draft patches and documentation, including implementation
plans and operator command blocks.

Codex must work inside a repository or disposable worktree and leave reviewable
diffs. It must not run hidden automation, become infrastructure, approve its own
changes, or operate as a background service.

The user remains the final approver for direction, live service changes,
deployment commands, and commits.

## Client Setup

The Framework laptop remains a thin client:

- Browser
- Terminal/SSH
- VS Code
- Remote-SSH
- Continue.dev, optional for editor-side review

No canonical project state lives on the laptop. The laptop is the screen; the project host is the computer.

## Normal Session Loop

### 1. Start From Project State

Open the project on its host:

- Prefer `strix:/srv/projects/<project-name>/` once the canonical source convention is established.
- Use `amd` only for projects that need the RTX 3090 or an explicit local-agent evaluation slice.

Read or update the shared operating files:

- `PROJECT_PLAN.md`
- `CURRENT_SLICE.md`
- `DECISIONS.md`
- `AGENT_STATUS.md`
- `AGENTS.md`

The slice should be narrow enough that the coder can complete it and the user can review it.

### 2. Build an Advisor Packet

Run `advisor-packet` from the project working tree.

The packet should include, bounded by default:

- Current slice
- Decision log
- Agent status
- Agent instructions
- `git status`
- `git diff --stat`
- Bounded `git diff` excerpt
- Bounded recent coder log, if present

The packet is intentionally compact. It should avoid full raw terminal logs unless the log is short and directly relevant.

### 3. Plan in Open WebUI

Open:

```text
http://192.168.50.225:3000
```

Use the advisor to:

- Understand the current project state.
- Clarify what should happen next.
- Check whether the coder’s proposed direction is still aligned with the current slice.
- Turn the next action into a prompt for the coding agent.

Open WebUI now reaches models through `model-dispatch` on ThinkCentre:

```text
http://192.168.50.225:4010/v1
```

Recommended Open WebUI choices:

- Use `auto-local` for normal advisor/planning prompts.
- Use `auto-reasoning-local` for long planning, architecture review, or decision-heavy prompts.
- Use `auto-coding-local` for coding chat and code-oriented explanations.
- Use `auto-small-local` only for short, lightweight prompts.

Direct `amd-backup-gemma4-26b-8k` should not be used for long pasted logs or large advisor packets. Its context window is too small for that use; validated routing showed `auto-small-local` skipped the AMD Gemma 8k endpoint when the estimated total was about 18k tokens and routed to AMD Qwen 32k instead.

OpenRouter remains free-only, explicit, and non-primary. In Open WebUI, choose `openrouter-free/openrouter/auto-free-router` or a specific `openrouter-free/<verified-model>:free` model only when you intentionally want a free cloud model. The OpenRouter paid catalog must remain hidden, and OpenRouter must not become an automatic fallback.

For Open WebUI web search, keep the working SearXNG JSON snippet path by leaving `BYPASS_WEB_SEARCH_WEB_LOADER=true` and pinning the task model to explicit local `amd-coder-qwen3-coder-30b-32k`.

### 4. Run Controlled Manual Steps

Use the planner to turn the next action into exact commands or controlled
manual edit steps. The user runs the commands in a terminal and keeps the
change bounded to the current slice.

For file edits, prefer explicit steps such as:

- Open this file.
- Change this section.
- Replace this paragraph.
- Run these checks.

For planning, sequencing, live-service risk, operator approval briefs, or any
task that could affect host roles, routing, billing exposure, persistent state,
security posture, Docker, systemd, or deployment behavior, use Codex instead.

Claude Code is a strong frontier-code alternative and second opinion when the
implementation is difficult enough to justify another high-capability manual
agent.

OpenCode is deferred to a later local-agent experiment. It is no longer assumed
to be the next primary operating agent, and nothing in the walking skeleton
should depend on it.

Continue.dev remains editor assist and review. Hermes remains observer/reviewer
only. Cline remains sandbox-only.

### Optional MCP / CodeGraphContext Evaluation Boundary

CodeGraphContext write workflows are evaluation-only. This is day-to-day
operating guidance, not a live MCP config change and not permission to enable
MCP live.

Default pattern:

```text
canonical repo -> read-only context
sandbox repo/worktree -> writable experiment
reviewed diff/patch -> manual promotion
```

CodeGraphContext may read from approved canonical project repositories, but it must not write directly to canonical working trees by default. Any write-capable use must happen only inside a disposable sandbox, such as a Git worktree, temporary branch checkout, dedicated patch-proposal directory, or `/tmp` patch artifact.

Promote sandbox changes only through reviewed diffs, patches, manual copy, or branch review. Do not grant persistent broad mutation approval, and do not run an automatic MCP setup wizard against primary repositories.

This rule is path-agnostic. It applies to operational source repos, project journal repos, documentation/control repos, and future project repos. Do not duplicate large videos, extracted frames, datasets, generated evidence, model outputs, or bulky review artifacts into sandboxes or Git unless that storage is explicitly intended.

Controlled manual steps should include:

- The current slice.
- Specific files or areas in scope.
- Constraints.
- Acceptance criteria.
- Exact commands or manual edit instructions.
- Checks to run before review.

### 5. Review the Result

The user reviews the diff. The system does not auto-approve changes.

Use normal git and editor tools:

```bash
git status
git diff --stat
git diff
```

Use VS Code Remote-SSH for visual diff review. Continue.dev highlight-and-ask can help explain a specific code chunk, but it is optional and should remain a review aid, not an autonomous reviewer.

Continue.dev uses LiteLLM-routed model IDs from thinkcentre:4000 rather than direct inference endpoints. This keeps editor-side review behavior aligned across models and avoids duplicating endpoint definitions on client devices.

Use the Review Coach to explain the diff in layman's terms. Every Review Coach
response must end with one of:

- Commit
- Revise
- Revert
- Inspect more

If the diff is confusing, rerun `advisor-packet`, paste the packet into Open
WebUI, and ask the advisor or Review Coach to interpret the state and draft the
next controlled manual step.

### 6. Decide, Commit, or Iterate

The user decides:

- Accept and commit.
- Ask the coder for a narrow follow-up.
- Reject the direction and reset manually with care.
- Update `DECISIONS.md` if a meaningful architectural or workflow choice was made.

Commit only after the user has reviewed the changes.

## Tool Decision Table

| Situation | Tool | Where |
|---|---|---|
| Plan a task | Open WebUI advisor | Browser |
| Summarize state for advisor | `advisor-packet` | Project working tree |
| Choreograph risky live-service work | Codex | Project working tree |
| Make a controlled manual edit | User following planner steps | Project working tree |
| Evaluate a bounded patch agent | Aider | Explicit evaluation slice only |
| Serve candidate local coding/reasoning models | vLLM | AMD or Strix explicit validation slice |
| Summarize or propose review skills | Hermes | Read-only observer/reviewer path |
| Get a frontier-code second opinion | Claude Code | Project working tree |
| Experiment with local-agent coding | OpenCode | Sandbox or later explicit slice |
| Review a diff | Review Coach, VS Code Remote-SSH, and git | Project host and browser |
| Ask about a specific code chunk | Continue.dev highlight-and-ask | VS Code |
| Try agent autonomy experiments | Cline | Sandbox only |
| Make final decision | User | Always |

## Coder Status Briefs

`AGENTS.md` should instruct the coding agent to leave concise status in `AGENT_STATUS.md` at handoff points.

The brief should include:

- What changed.
- What was not changed.
- Tests or checks run.
- Known risks.
- Files the user should inspect.
- Whether the coder is asking for approval before continuing.

This replaces copying long terminal transcripts into chat.

## What This Workflow Avoids

The workflow deliberately avoids:

- Auto-approving coder actions.
- Custom approval daemons.
- Hidden background watcher agents.
- MCP failure-supervision loops.
- Codex API automation.
- Claude/Codex wrapper infrastructure.
- Paid API automation.
- Large bespoke orchestration.

The durable state is simple markdown plus git history. The bridge is a local packet generator, not an autonomous control plane.

## Failure Modes

Watch for these patterns:

- Raw terminal output is repeatedly pasted into Open WebUI.
- A tool runs multiple broad attempts instead of the user following controlled manual steps.
- The advisor is asked to reason without current slice or diff context.
- The user is tempted to build an approval daemon instead of narrowing the slice.
- Codex or Claude-style tools start appearing in scripts, wrappers, timers, or API jobs.
- Aider is treated as required for normal workflow edits, or asked to plan, deploy, restart services, edit secrets, or make broad architecture decisions.
- Hermes is asked to mutate canonical repos, install live skills, restart services, or approve actions.
- OpenCode is treated as the default or primary coder without an explicit local-agent experiment slice.
- The Framework laptop accumulates project state.

The fix is usually to narrow `CURRENT_SLICE.md`, run `advisor-packet`, ask the advisor for the next prompt, and keep the user in the approval seat.
