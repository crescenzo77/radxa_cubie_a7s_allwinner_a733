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

For bounded continuous work, use:

```sh
scripts/hermes-kernel-continuous-work
```

This runner calls `scripts/hermes-kernel-work-cycle` repeatedly, defaults to
three cycles, and stops early on roadblock, delay, timeout, or failure. It sends
notifications through the existing Hermes messaging route when those conditions
occur, and sends a final completion notification after the bounded run finishes.
Roadblock detection intentionally keys off Hermes' explicit `ROADBLOCK:` marker
instead of old status JSON fields like `human_required`, because Cubie runtime
proof, Cubie reboot, and Cubie boot-artifact staging are now operator-approved
autonomous work.

Useful environment controls:

```sh
HERMES_KERNEL_MAX_CYCLES=3
HERMES_KERNEL_SLEEP_SECONDS=300
HERMES_KERNEL_NOTIFY=1
HERMES_KERNEL_NOTIFY_TARGET=telegram
HERMES_KERNEL_NOTIFY_ON_COMPLETION=1
HERMES_CUBIE_ACCESS_TIER=partial
```

The continuous runner does not add Telegram-specific code. It calls:

```sh
"${HERMES_BIN}" send --to "${HERMES_KERNEL_NOTIFY_TARGET}" ...
```

Before running cycles, it performs a non-sending `hermes send --list` check and
warns if the channel directory has no discovered target. That warning does not
prove delivery failure because `hermes send --to telegram` may still use the
configured Telegram home channel.

## Runtime Proof Approval

Historic approval packet flow:

```sh
scripts/cubie-runtime-proof-approval-packet --board cubie2
```

The packet records board, UART, artifact path, exact first command, and stop
conditions. As of 2026-06-12, Cubie runtime proof work is controlled by
`HERMES_CUBIE_ACCESS_TIER`.

## Cubie Access Tiers

The default tier is `partial`.

`strict`:

- read-only inventory, SSH checks, UART mapping/capture, log pull, dry-runs,
  status packets, and approval/status briefs
- no `/boot` writes, artifact staging, reboot, power cycle, boot selection, or
  live state-changing proof
- no cubie1 state-changing proof

`partial`:

- everything in `strict`
- stage workflow-identified kernel/boot artifacts to the selected Cubie
- run live UART/runtime proof on cubie2 and cubie3
- reboot cubie2 or cubie3 through documented workflow commands
- no external power cycling, cubie1 state-changing proof, destructive storage
  operations, firmware/SPI/eMMC bootloader writes, or persistent bootloader
  default changes outside the proof workflow

`total`:

- everything in `partial`
- use cubie1, cubie2, and cubie3 for live proof and reproduction
- use documented Cubie power helpers for recovery power cycles if a board is
  wedged
- run documented recovery/vendor-restore steps from the homelab repo
- still no repartitioning, formatting, `dd`/raw block writes, firmware/SPI/eMMC
  bootloader writes, destructive cleanup, service/cron/model-routing changes,
  pushes, or mail submission

## Resource Flexibility

Required resources block the workflow when absent. Optional resources only
degrade the workflow.

Current examples:

- Required: `amd-research`, `strix-review`, Qdrant, Cubie2 UART, patch export
- Optional: `amd-fast`, OpenRouter free fallback, Framework client
- Approved Cubie autonomy: controlled by `HERMES_CUBIE_ACCESS_TIER`
- Still forbidden without approval: external power cycling, persistent
  bootloader default changes outside the proof workflow, service/cron changes,
  model-routing changes, kernel source commits, pushes, mail submission

## Generated State

Commit intentional summaries, evidence packets, approval packets, and decision
records. Tolerate Hermes dashboard/latest-file churn until stopping points,
then consolidate it into a meaningful commit or leave it explicitly reported as
generated state.
