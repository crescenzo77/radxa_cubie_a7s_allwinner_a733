# Workflow

This is the current workflow entrypoint.

Do not follow older workflow documents directly. Start here:

1. Read `PLAN_INDEX.md`.
2. Read the current plan named there.
3. Read `CURRENT_SLICE.md`.
4. Read `AGENT_STATUS.md`.
5. Act only inside the current slice.

Current operating workflow:

- `docs/provider-neutral-adhd-workflow.md`

Current patch-executor rule:

- Aider is the preferred bounded patch executor for planned strict slices.
- Aider acts only after the planner defines the slice.
- Aider must not plan, broaden scope, auto-commit, deploy, change services, or
  become autonomous.

The old two-surface workflow was archived instead of edited in place:

- `docs/archive/workflow-two-surface-superseded-2026-05-29.md`
