# Plan Index

This is the canonical registry for homelab workflow plans.

Use this file first when deciding which plan is current. Do not delete old
workflow, plan, history, or draft files. When a plan is replaced, preserve it in
place, archive it, or quarantine it, then record its status here.

## Status Labels

- `Current`: the active plan to follow now.
- `Superseded`: replaced by a newer plan but kept for history.
- `Archived`: old draft or history file intentionally preserved.
- `Quarantined`: misleading or unsafe plan that must not be followed without
  explicit review.

## Current Plan

| Status | Plan | Created | Superseded | Replacement | Reason |
|---|---|---:|---:|---|---|
| `Current` | `docs/provider-neutral-adhd-workflow.md` | 2026-05-29 | - | - | Active provider-neutral ADHD workflow. Roles are stable; providers/tools are swappable. |

## Historical And Superseded Plans

| Status | Plan | Created | Superseded | Replacement | Reason |
|---|---|---:|---:|---|---|
| `Archived` | `docs/provider-neutral-adhd-workflow-evolution-2026-05-29.md` | 2026-05-29 | - | `docs/provider-neutral-adhd-workflow.md` | Long-form history/evolution record, not the operating plan. |
| `Archived` | `docs/archive/local-agent-workflow-runbook-draft-2026-05-29.md` | 2026-05-29 | 2026-05-29 | `docs/provider-neutral-adhd-workflow.md` | First local-agent runbook draft; archived instead of deleted. |
| `Superseded` | `WORKFLOW.md` | 2026-05-05 | 2026-05-29 | `docs/provider-neutral-adhd-workflow.md` | Older two-surface workflow. Useful historical context, but not the current operating plan. |
| `Superseded` | `ROADMAP.md` | 2026-05-05 | 2026-05-29 | `docs/provider-neutral-adhd-workflow.md` | Older roadmap centered on the two-surface walking skeleton. Keep for history and future reconciliation. |
| `Superseded` | `PROJECT_PLAN.md` | 2026-05-05 | 2026-05-29 | `docs/provider-neutral-adhd-workflow.md` | Older broad project plan. Current plan status now lives in this index. |

## Protected Long-Context File

`docs/provider-neutral-adhd-workflow-evolution-2026-05-29.md` is the current
protected master history/evolution file. It is used as long context to review
the progression of discussion, plans, decisions, and changes.

Do not delete this file. If it is ever superseded, preserve it and register the
new replacement here before using the replacement.

## Rules For New Plans

1. Create the new plan as a separate file.
2. Add or update this index in the same diff.
3. Mark exactly one operating plan as `Current` unless the user explicitly wants
   multiple active plans for different projects.
4. Mark replaced plans as `Superseded`, `Archived`, or `Quarantined`.
5. Record the replacement plan and plain-language reason.
6. Do not delete workflow/history files.

## Archive And Quarantine Policy

Use `docs/archive/` for old plans that are useful historical records.

Use `docs/quarantine/` only for plans that are misleading, unsafe, or likely to
cause agent drift if accidentally followed.

A quarantined plan still remains part of history. It must be listed here with a
reason and a replacement path.
