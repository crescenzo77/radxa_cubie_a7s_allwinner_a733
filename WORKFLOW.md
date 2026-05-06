# Workflow: Two Surfaces Plus `advisor-packet`

This describes the normal working loop for homelab coding projects.

Last updated: 2026-05-05.

## Summary

The steady-state workflow is:

```text
Web UI advisor/planner
  + advisor-packet markdown summary
  + self-hosted coding agent on the project host
  + user review and final decision
```

The goal is to reduce copy/paste and context bloat. The goal is not autonomous supervision. The user remains responsible for approving direction, reviewing diffs, and deciding when work is done.

Codex may be used manually during setup documentation work, but it must not become part of the operating workflow.

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
- Use `amd` for projects that need the RTX 3090 or while AMD remains the OpenCode execution host.

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

For planning, use the Strix reasoning model through Open WebUI. During the transition, Open WebUI may still reach models through LiteLLM, but the target is direct local model endpoints.

For coding-oriented discussion, use the AMD local-coder model if useful.

OpenRouter remains free-only, explicit, and non-primary. The target is generated free-only provider configuration, not broad OpenRouter access and not automatic paid fallback.

### 4. Hand a Bounded Prompt to the Coder

Use a self-hosted coding agent on the coding PC or project host.

Current default:

```bash
opencode
```

Run it on AMD or in the relevant project host directory.

Current live configuration may still use Homelab LiteLLM during the transition. Target state is a direct local-coder provider for OpenCode, with generated OpenRouter-free models available only as manual fallback.

Aider was evaluated and eliminated from the homelab steady-state workflow after unsafe file-handling behavior during a simple documentation task. Do not use Aider as the default or fallback coder for this workflow.

The coder prompt should include:

- The current slice.
- Specific files or areas in scope.
- Constraints.
- Acceptance criteria.
- The instruction to update `AGENT_STATUS.md` with what happened, what changed, and what needs user approval.

### 5. Review the Result

The user reviews the diff. The system does not auto-approve coder actions.

Use normal git and editor tools:

```bash
git status
git diff --stat
git diff
```

Use VS Code Remote-SSH for visual diff review. Continue.dev highlight-and-ask can help explain a specific code chunk, but it is optional and should remain a review aid, not an autonomous reviewer.

If the coder output is confusing, rerun `advisor-packet`, paste the packet into Open WebUI, and ask the advisor to interpret the state and draft the next bounded prompt.

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
| Implement a bounded task | OpenCode direct local-coder path | AMD/project host terminal |
| Review a diff | VS Code Remote-SSH and git | Project host |
| Ask about a specific code chunk | Continue.dev highlight-and-ask | VS Code |
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
- The coder runs multiple broad attempts without updating `AGENT_STATUS.md`.
- The advisor is asked to reason without current slice or diff context.
- The user is tempted to build an approval daemon instead of narrowing the slice.
- Codex or Claude-style tools start appearing in scripts, wrappers, timers, or API jobs.
- The Framework laptop accumulates project state.

The fix is usually to narrow `CURRENT_SLICE.md`, run `advisor-packet`, ask the advisor for the next prompt, and keep the user in the approval seat.
