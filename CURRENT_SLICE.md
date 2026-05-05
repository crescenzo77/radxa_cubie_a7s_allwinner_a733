# Current Slice

## Slice 4: Test the two-surface loop on one small real task

Use the current homelab repo to test the actual workflow:

1. Update project state.
2. Run `advisor-packet`.
3. Use the web UI advisor to review the packet.
4. Generate a bounded coder prompt.
5. Apply one small documentation improvement.
6. Review the diff.
7. Commit if acceptable.

## Test task

Make one small documentation improvement: add a short "How to use this repo" section to `PROJECT_PLAN.md`.

## Requirements

The new section should explain:

- `PROJECT_PLAN.md` stores the broad goal and current stage.
- `CURRENT_SLICE.md` stores the active task.
- `AGENT_STATUS.md` stores the current handoff/status.
- `DECISIONS.md` stores durable decisions.
- `AGENTS.md` stores coder rules.
- `scripts/advisor-packet` creates the compact advisor packet.

## Constraints

- Documentation only.
- No scripts.
- No service changes.
- No automation.
- No model API calls.
- No new tools.
- Keep the change small and reviewable.

## Acceptance Criteria

- `PROJECT_PLAN.md` has a concise "How to use this repo" section.
- `AGENT_STATUS.md` is updated after the change.
- `advisor-packet` is run at least once during the test.
- The final diff is reviewed before commit.
