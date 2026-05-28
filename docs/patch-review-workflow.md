# Patch Review Workflow

## Purpose

Use a coding tool to make one bounded patch, then use a separate reviewer to
decide whether the patch is safe to commit.

The important separation is:

```text
planner defines the bounded task
patch tool edits the repo
reviewer inspects the diff
user decides Commit, Revise, Revert, or Inspect more
```

Do not let the patch tool become autonomous, approve itself, or commit by
default.

## Surfaces

### 1. Planner / Advisor

The planner turns a vague task into a bounded prompt for the patch tool.

Planner options:

- Codex desktop on the Mac mini.
- ChatGPT.
- Open WebUI with local models.
- Another explicit advisor chosen by the user.

The planner prompt should name:

- the target repository
- exact files or areas in scope
- what not to touch
- required checks
- rollback path
- whether a commit is allowed after review

### 2. Patch Tool

The patch tool edits files and leaves a Git diff.

Patch tool options:

- Aider, for strict named-file edits only.
- Codex desktop or Codex CLI, when the user explicitly selects it for patching.
- OpenCode, as the preferred next local-model coding-agent candidate to
  evaluate.
- Another coding agent, only after a bounded validation slice.

Rules:

- One repository.
- Named files or clearly bounded area.
- No auto-commits.
- No live-service changes unless explicitly selected.
- No broad repo rewrites.
- Decline unrelated context/control files.
- Stop after one reviewable diff.

### 3. Reviewer / Review Coach

The reviewer inspects the patch before commit.

Reviewer options:

- Codex desktop on the Mac mini.
- ChatGPT.
- Open WebUI with a local model.
- OpenCode or another local agent, if explicitly used in review-only mode.
- Claude Code or another frontier reviewer, if selected by the user.

The reviewer is not limited to one provider. The role is provider-neutral.

The reviewer checks:

- `git status --short`
- `git diff --check`
- `git diff --stat`
- the actual diff
- whether the change stayed in scope
- whether tests or checks were run
- whether live services, secrets, routes, Docker, systemd, storage, or control
  docs were touched

For tiny docs edits, use the short review:

- Changed:
- Scope:
- Risk:
- Recommendation:

For code, services, configs, routing, Docker, systemd, storage, multiple files,
or unclear scope, use the full review:

- What changed:
- Scope check:
- Risk:
- Proof:
- What to inspect:
- Recommendation:

Every review ends with one of:

- Commit
- Revise
- Revert
- Inspect more

### 4. User Approval

The user makes the final call.

The reviewer may recommend, but it does not approve automatically. The user
decides whether to commit, revise, revert, or inspect more.

## Local Model Reviewer

A local model does not need a coding agent if it is only reviewing.

For review, the user can paste or provide:

- `git status --short`
- `git diff --check`
- `git diff --stat`
- relevant diff excerpts

Open WebUI plus model-dispatch is enough for this review-only surface.

A local model does need a coding harness if it is expected to edit files
directly. Candidate harnesses:

- Aider for strict patch mode.
- OpenCode for local-model coding-agent evaluation.
- Codex CLI only if a supported local-provider setup is proven separately.

## Current Tool Guidance

Aider is conditionally allowed as a bounded patch assistant, not as a general
autonomous coder.

Use Aider when:

- the task is one repo
- the files are named
- the edit is small
- auto-commits are disabled
- a separate reviewer will inspect the diff

Do not use Aider for:

- planning
- broad repo work
- service changes
- Docker or systemd changes
- secrets
- deployment
- architecture decisions
- long control/history docs

OpenCode is the better next candidate for a local-model coding-agent trial
because it can be evaluated separately from Aider while using the same
patch-review workflow.

Codex desktop remains a strong planner and reviewer from the Mac mini. Running
Codex on Strix with a local model is not currently proven in this homelab and
should be treated as a separate investigation, not an assumed workflow.

## Current Recommended Flow

1. Planner writes a bounded task.
2. Patch tool makes one diff.
3. Exit the patch tool.
4. Run:

   ```sh
   git status --short
   git diff --check
   git diff --stat
   git diff
   ```

5. Reviewer explains the diff in layman's terms.
6. User decides Commit, Revise, Revert, or Inspect more.
7. Commit only after proof.
