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
HERMES_KERNEL_PROVIDER=openwebui-hub
HERMES_KERNEL_MODEL="Strix Qwen3.6 27B Dense ROCmFP4-MTP headQ6 GGUF rocmfp4-llama ROCm+Vulkan ctx256k self-spec reasoning-off coding"
```

The continuous runner does not add Telegram-specific code. It calls:

```sh
"${HERMES_BIN}" send --to "${HERMES_KERNEL_NOTIFY_TARGET}" ...
```

Before running cycles, it performs a non-sending `hermes send --list` check and
warns if the channel directory has no discovered target. That warning does not
prove delivery failure because `hermes send --to telegram` may still use the
configured Telegram home channel.

Kernel work cycles default to the local Strix model instead of the OpenRouter
free router because the Strix lane has been verified to use the terminal tool
for simple command execution. Override with `HERMES_KERNEL_PROVIDER` and
`HERMES_KERNEL_MODEL` only when the replacement model is known to use tools.

## Runtime Proof Approval

Historic approval packet flow:

```sh
scripts/cubie-runtime-proof-approval-packet --board cubie2
```

The packet records board, UART, artifact path, exact first command, and stop
conditions. As of 2026-06-12, Cubie runtime proof work is controlled by
`HERMES_CUBIE_ACCESS_TIER`. As of 2026-06-13, A733 multi-board work also uses
the board-role envelope in
`runbooks/kernel-a733-mainline-enablement-workflow.md`: one `burn` lane, one
`proving` lane, and one `reference` lane. The tier is a coarse maximum; the
board role is the per-board authority.

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
- use cubie1, cubie2, and cubie3 for live proof and reproduction only after
  each board has an explicit `burn`, `proving`, or `reference` role in
  `inventory/hardware/cubie-a7s-lab.json`
- run read-only checks, UART captures, and independent proof lanes concurrently
  across multiple Cubies when useful
- use documented Cubie power helpers for recovery power cycles if a board is
  wedged
- run documented recovery/vendor-restore steps from the homelab repo
- allow destructive discovery only on the board assigned `burn`, only when the
  recovery method is verified before that experiment class, and only with a
  pristine-image reset between hypothesis families
- firmware/SPI/eMMC bootloader writes, fuses, and unrecoverable persistent
  changes require an explicit burn-role sub-permission and verified recovery
  story; they are not enabled merely by setting tier `total`
- still no service/cron/model-routing changes, pushes, or mail submission
- `proving` runs only promoted artifacts; `reference` stays pinned to a
  known-good baseline and is passive unless human-gated
- serialize state-changing actions such as artifact staging, reboot,
  power-cycle, boot selection, recovery, or restore; do not change the state of
  multiple Cubies at the same time

## Interchangeable Agent And Claims

Run one live agent at a time for now. A single live agent may pipeline work
across boards, including a long burn-board experiment with heartbeat while it
runs software-only cycles. Do not enable cross-runtime concurrency until the
central claim service is active and verified.

The intended claim backend is the existing ThinkCentre Fault Ledger/FastMCP
SQLite-WAL pattern. Agents should call a narrow claim/release/heartbeat surface;
SQLite stays local to ThinkCentre. Do not rely on per-host local claim
directories for cross-host coordination.

Claim these contended resources before board-mutating or kernel-tree-mutating
work:

- work item ID
- board lane
- UART by-path
- power outlet or power-control handle
- kernel tree path
- staged artifact path, when relevant

Agent tier must be enforced server-side by the claim service using an
`AGENT_ID -> AGENT_TIER` registry. If that service is not available, treat the
agent as `local` tier and do not start destructive burn-board work.

Stale claim handling:

- software, proving, and reference: log before takeover
- burn: log, mark board state `UNKNOWN`, and force recovery-to-pristine before
  any new work trusts that board

`OPERATOR_PRESENT` defaults to `false`; `APPROVAL_TIMEOUT` defaults to `120s`.
If per-operation approval is required and no approval arrives before the
timeout, log and stop.

Recovery is a ladder, not a boolean:

- `soft-fallback`: non-default extlinux kernel/DTB/bootargs experiments only
- `sd-reimage`: removable microSD full-image recovery through SD-Mux/SDWire or
  equivalent controller path
- `fel-bootrom`: A733/SUN60IW2 BootROM/FEL recovery drilled with the actual
  board, controller-reachable OTG, entry method, and `sunxi-fel` or `xfel`

Only the highest drilled rung controls burn-board autonomy. A reachable but
undrilled recovery method is not verified.

RED is limited to public and commercial boundaries: public mail, `b4 send`,
real `git send-email` delivery, list replies, GitHub comments or pull requests,
public pushes, and additional paid/third-party API calls initiated by the
agent. Hardware destructiveness is governed by board role, not by RED.

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
