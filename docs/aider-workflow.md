# Aider Workflow

## Purpose

Aider is a bounded patch assistant for small repository edits after the slice is
already planned.

Its job is to produce one narrow, reviewable Git diff. It is not the planner,
operator, deployment tool, service controller, or architecture reviewer.

## When To Use Aider

Use Aider when all of these are true:

- The active slice is already written in `CURRENT_SLICE.md`.
- The files or areas in scope are clear.
- The change is local to one repository.
- The desired output is one bounded edit.
- The result can be reviewed with normal Git diff.
- The rollback path is simple: reject or revert the diff.

Good Aider tasks include:

- Small documentation updates.
- Focused test additions.
- Narrow bug fixes.
- Mechanical edits where the intended files are known.
- Tight refactors inside one module or document set.

## When Not To Use Aider

Do not use Aider for:

- Planning a slice.
- Architecture decisions.
- Live deployment.
- Service restarts or reloads.
- Docker, systemd, reverse proxy, or production config changes.
- Secrets, tokens, credentials, or `.env` changes.
- Multi-host changes.
- Broad repo rewrites.
- Autonomous follow-up work.
- Anything requiring user approval before the next command.

Use Codex for planning, sequencing, approval briefs, and risky live-service
steps. Use Claude Code as a strong frontier-code alternative or second opinion
when needed. Keep OpenCode as a later local-agent experiment, Continue.dev as
editor assist, and Cline sandbox-only.

## Standard Aider Workflow

1. Read the active repo instructions and slice files:
   `AGENTS.md`, `CODEX_CONTEXT.md`, `CURRENT_SLICE.md`, `AGENT_STATUS.md`,
   `PROJECT_PLAN.md`, and `DECISIONS.md`.
2. Confirm the edit is one repo, one bounded task, and one reviewable diff.
3. Start Aider from the repository working tree.
4. Give Aider a narrow prompt with:
   - the active slice name
   - exact files or areas in scope
   - files and actions out of scope
   - required checks
   - instruction to avoid commits
5. Review the resulting diff manually.
6. Run the slice checks.
7. Update `AGENT_STATUS.md` with the handoff.
8. Stop for user review unless the user explicitly requested another bounded
   edit.

## Validation Checklist

Before accepting Aider output:

- `git status --short` shows only expected files.
- `git diff --check` passes.
- `git diff --stat` is narrow enough for the slice.
- The diff does not include unrelated formatting or churn.
- Required tests or checks were run, or marked unavailable with a reason.
- `AGENT_STATUS.md` records what changed, what did not change, files changed,
  checks run, results, risks, blockers, approval needs, and next action.
- No live service, secret, Docker, systemd, multi-host, or architecture change
  was made by Aider.

## Commit Guidance

Do not let Aider commit by default.

The user reviews the diff first. After review, commit manually with a concise
message that names the slice. If the Aider diff is wrong, reject it or revert it
with normal Git tools instead of asking Aider to broaden the task.

## Direct vLLM Trial Note

Direct vLLM trials must use one file only. The user reviews the diff before commit. If Aider edits unrelated files, reject the run and restore the diff.
