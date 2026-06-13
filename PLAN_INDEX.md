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

## Current State Records

These are the official current entrypoints. Older versions with the same names
must be archived before replacement.

| File | Current purpose |
|---|---|
| `PLAN_INDEX.md` | Registry for current, superseded, archived, quarantined, and protected plan files |
| `PROJECT_PLAN.md` | Current project-plan entrypoint |
| `WORKFLOW.md` | Current workflow entrypoint |
| `ROADMAP.md` | Current roadmap entrypoint |
| `HOMELAB_LAYOUT.md` | Current layout entrypoint and host/repo meanings |
| `runbooks/kernel-knowledge-cortex.md` | Kernel evidence retrieval sidecar for the patch workflow |
| `runbooks/kernel-token-offload.md` | Local hardware token-offload workflow for kernel logs, diffs, research, and reviews |
| `runbooks/kernel-a733-mainline-enablement-workflow.md` | Project-specific A733/Cubie A7S mainline enablement workflow while communications are paused |
| `task-packets/kernel/a733-cycle-ledger.md` | Append-only bounded-cycle ledger for local A733 work |
| `task-packets/kernel/a733-supervised-batch-queue.md` | Role-gated hardware lane queue for burn/proving/reference Cubie work |
| `task-packets/kernel/a733-unsent-communications-ledger.md` | Held upstream communications ledger for messages that would normally be sent but are intentionally withheld |
| `CURRENT_SLICE.md` | Active task and boundaries |
| `AGENT_STATUS.md` | Latest handoff/status |
| `DECISIONS.md` | Durable decision log |

## Historical And Superseded Plans

| Status | Plan | Created | Superseded | Replacement | Reason |
|---|---|---:|---:|---|---|
| `Archived` | `docs/provider-neutral-adhd-workflow-evolution-2026-05-29.md` | 2026-05-29 | - | `docs/provider-neutral-adhd-workflow.md` | Long-form history/evolution record, not the operating plan. |
| `Archived` | `docs/archive/local-agent-workflow-runbook-draft-2026-05-29.md` | 2026-05-29 | 2026-05-29 | `docs/provider-neutral-adhd-workflow.md` | First local-agent runbook draft; archived instead of deleted. |
| `Archived` | `docs/archive/workflow-two-surface-superseded-2026-05-29.md` | 2026-05-05 | 2026-05-29 | `WORKFLOW.md` | Older two-surface workflow archived before creating the current workflow entrypoint. |
| `Archived` | `docs/archive/roadmap-two-surface-superseded-2026-05-29.md` | 2026-05-05 | 2026-05-29 | `ROADMAP.md` | Older roadmap centered on the two-surface walking skeleton archived before creating the current roadmap entrypoint. |
| `Archived` | `docs/archive/project-plan-superseded-2026-05-29.md` | 2026-05-05 | 2026-05-29 | `PROJECT_PLAN.md` | Older broad project plan archived before creating the current project-plan entrypoint. |
| `Archived` | `docs/archive/homelab-layout-two-surface-superseded-2026-05-29.md` | 2026-05-26 | 2026-05-29 | `HOMELAB_LAYOUT.md` | Older two-surface layout/workflow framing archived before creating the current layout entrypoint. |

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
6. Do not edit old plan files in place to make them current.
7. Archive or quarantine the old file first, then create a new current file at
   the stable path if that path should remain an entrypoint.
8. Do not delete workflow/history files.

## Archive And Quarantine Policy

Use `docs/archive/` for old plans that are useful historical records.

Use `docs/quarantine/` only for plans that are misleading, unsafe, or likely to
cause agent drift if accidentally followed.

A quarantined plan still remains part of history. It must be listed here with a
reason and a replacement path.
