# Kernel Workflow Controls

Status: active baseline
Updated: 2026-06-12

These controls keep Hermes useful without making it brittle or risky.

## Host-Aware Paths

The source of truth is:

```text
inventory/kernel-workflow-paths.json
```

Use:

```sh
scripts/kernel-workflow-env
scripts/kernel-workflow-env --json
scripts/kernel-workflow-env --shell
```

Hermes and Codex should use this registry before assuming that a Mac path also
exists on ThinkCentre or Strix.

## Patch Export Contract

The current patch export is the host-specific `patch_export` path from the
registry. It should contain numbered `000*.patch` files. Flat patches are
review snapshots; branch stack and `b4 prep` remain the mailout source of
truth.

Use:

```sh
scripts/kernel-patch-export-status
scripts/a733-series-shape-gate "$(scripts/kernel-workflow-env --json | jq -r .paths.patch_export.selected)"
scripts/a733-prereq-api-audit "$(scripts/kernel-workflow-env --json | jq -r .paths.patch_export.selected)"
```

## RFC Recheck Packet

The workflow gate expects a dated markdown packet under:

```text
task-packets/kernel/research/a733-rfc-recheck-*.md
```

Use:

```sh
scripts/a733-rfc-recheck-packet
```

This wraps the existing public dependency checker and writes the packet shape
that `scripts/kernel-workflow-status` can parse.

## Supervised Hermes Work

For longer Hermes cycles, do not run a silent open-ended one-shot. Use:

```sh
scripts/hermes-kernel-work-cycle
```

The wrapper writes:

```text
task-packets/kernel/hermes-work/*-hermes-kernel-work.log
task-packets/kernel/hermes-work/*-hermes-kernel-work.md
```

Optional completion notification is disabled by default. Enable it per run with:

```sh
HERMES_KERNEL_NOTIFY=1 scripts/hermes-kernel-work-cycle
```

The target defaults to `telegram` and can be changed with
`HERMES_KERNEL_NOTIFY_TARGET`. The wrapper sends one concise completion,
timeout, or failure message through:

```sh
"${HERMES_BIN}" send --to "${HERMES_KERNEL_NOTIFY_TARGET}" ...
```

Notification failure is reported as a warning and does not change the work
cycle return code.

It does not grant permission for hardware, boot, service, cron, push, or kernel
source changes.

## Runtime Proof Approval

Before Cubie2 runtime proof work, generate an approval packet:

```sh
scripts/cubie-runtime-proof-approval-packet --board cubie2
```

The packet records board, UART, artifact path, exact first command, and stop
conditions. It does not stage artifacts or touch hardware.

## Resource Flexibility

Required resources block the workflow when absent. Optional resources only
degrade the workflow.

Current examples:

- Required: `amd-research`, `strix-review`, Qdrant, Cubie2 UART, patch export
- Optional: `amd-fast`, OpenRouter free fallback, Framework client
- Forbidden without approval: Cubie1 kernel proof, power cycling, `/boot`
  writes, bootloader changes, service/cron changes, kernel source commits,
  pushes

## Generated State

Commit intentional summaries, evidence packets, approval packets, and decision
records. Tolerate Hermes dashboard/latest-file churn until stopping points,
then consolidate it into a meaningful commit or leave it explicitly reported as
generated state.
