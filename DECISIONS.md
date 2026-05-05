# Decisions

## 2026-05-05 — Two-surface workflow

Decision:
Use a two-surface workflow: web UI advisor/planner plus self-hosted coding agent.

Rationale:
This reduces copy/paste and context-window bloat without building a fragile autonomous approval system.

Consequences:
- The user remains the final approver.
- `advisor-packet` is only a local context packet generator.
- Markdown files and Git are the durable project state.
- Codex may be used manually during setup, but must not become infrastructure.

## 2026-05-06 — Slice 5 evaluation

Decision:
Aider is the preferred first candidate for the steady-state coder evaluation.
OpenCode remains available as a fallback.
Aider is not the final default until this bounded edit test is reviewed and accepted.
Aider must use Homelab LiteLLM, not direct paid-provider APIs.
No automation, daemon, watcher, or background job should be created around Aider.

Rationale:
Aider was tested as a candidate for the steady-state coder in the two-surface workflow.
It meets the requirements for Git-centered, terminal-based, bounded editing.
It does not pollute system Python and works inside a Git repo.
It produces reviewable diffs and respects workflow constraints.

Consequences:
- Aider is being evaluated as the first preferred coding agent.
- OpenCode remains available as a fallback.
- No automation or background processes are created around Aider.
- The final default will be determined after reviewing this bounded edit test.

## 2026-05-06 — Aider eliminated from homelab workflow

Decision:
Aider will not be used in the homelab steady-state workflow.

Rationale:
Aider installed cleanly and reached Homelab LiteLLM, but it failed a simple bounded documentation task in an unacceptable way. It created bogus files using prompt text as filenames and emptied `AGENT_STATUS.md`, one of the repo's control files. The repo had to be manually recovered.

This failure happened on a simple task, so simpler scope is not a sufficient safety control.

Consequences:
- Aider is not the default coder.
- Aider is not a fallback coder for the homelab workflow.
- Do not build wrappers, scripts, automation, or process steps around Aider.
- OpenCode through LiteLLM becomes the next coder path to evaluate and recenter around.
- The two-surface workflow remains valid: web UI advisor, OpenCode coder, `advisor-packet`, markdown state files, and Git review.
