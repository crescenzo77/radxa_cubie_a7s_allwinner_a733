# A733 DTS v2 Static Proof Command Packet

Status: local-only; no-run; no-send
Updated: 2026-06-13

This packet turns the DTS v2 static proof plan into a concrete future command
recipe for Strix. It is not proof that the commands have been run, not a build
log, not a patch, not send approval, and not permission to mutate hardware.

Do not execute this packet unless a future cycle explicitly contracts the proof
run after rereading the authority files.

## Inputs

Authority files:

- `runbooks/kernel-a733-mainline-enablement-workflow.md`
- `inventory/hardware/cubie-a7s-lab.json`
- `task-packets/kernel/a733-cycle-ledger.md`
- `task-packets/kernel/a733-supervised-batch-queue.md`
- `task-packets/kernel/a733-unsent-communications-ledger.md`

Proof planning files:

- `task-packets/kernel/a733-dts-v2-local-delta-plan.md`
- `task-packets/kernel/a733-dts-v2-static-proof-plan.md`
- `task-packets/kernel/a733-dts-v2-static-validation-hosts.md`
- `task-packets/kernel/a733-dts-v2-static-proof-preflight.md`
- `task-packets/kernel/a733-dts-v2-uart-pinctrl-local-preview.patch`

Observed best host:

- host: `strix`
- source tree to reference only: `/srv/projects/cubie-a7s-armbian/sources/mainline-linux`
- observed head: `8fde5d1d47f69db6082dfa34500c27f8485389a5`
- required isolation: create a temporary full worktree or another
  intentionally isolated tree before applying the DTS v2 delta

Known prerequisite caveat: read-only inventory observed
`arch/arm64/boot/dts/allwinner/sun60i-a733.dtsi` and
`arch/arm64/boot/dts/allwinner/sun60i-a733-cubie-a7s.dts` as untracked files
in the Strix source tree. A detached worktree at
`8fde5d1d47f69db6082dfa34500c27f8485389a5` is therefore not sufficient unless
a future preflight proves those files are committed or otherwise present in the
isolated proof tree.

Latest preflight result: the A733 DTS/DTSI prerequisite files are still
untracked on Strix, so a future static proof must not use a plain detached
worktree unless those files are first committed or otherwise preserved in the
isolated proof tree.

## Preflight Checks

Run these only in a future contracted proof cycle:

```sh
set -eu

HOST_TREE=/srv/projects/cubie-a7s-armbian/sources/mainline-linux
PROOF_TREE=/tmp/a733-dts-v2-static-proof-tree
BUILD_DIR=/tmp/a733-dts-v2-static-proof-build
PATCH=/tmp/a733-dts-v2-uart-pinctrl-local-preview.patch
LOG_DIR=/tmp/a733-dts-v2-static-proof-logs

hostname
uname -a
git -C "$HOST_TREE" status --short --branch
git -C "$HOST_TREE" rev-parse --show-toplevel
git -C "$HOST_TREE" rev-parse HEAD
command -v aarch64-linux-gnu-gcc
command -v make
command -v dtc
test -x "$HOST_TREE/scripts/checkpatch.pl"
test -x "$HOST_TREE/scripts/get_maintainer.pl"
```

Stop if the observed host tree is missing, if tools are missing, or if the
selected proof tree would reuse the dirty detached host tree in-place.
Also stop if the source A733 DTS/DTSI files exist only as untracked files and
the isolation method would omit them.

## Isolation Setup

Preferred shape for a future proof cycle, if the prerequisite A733 DTS files
are committed at the selected base:

```sh
rm -rf "$PROOF_TREE" "$BUILD_DIR" "$LOG_DIR"
mkdir -p "$LOG_DIR"
git -C "$HOST_TREE" worktree add --detach "$PROOF_TREE" 8fde5d1d47f69db6082dfa34500c27f8485389a5
git -C "$PROOF_TREE" status --short --branch
```

If the prerequisite A733 DTS files remain untracked on Strix, use a different
contracted isolation method that preserves those files without using the dirty
tree in-place, such as a temporary copy of the current source tree including
untracked A733 files. That future cycle must record the exact copy command,
source tree status, isolated tree status, and hashes for the copied A733 files.

The future proof cycle may choose a different base commit only if it records
why that base is more correct. It must not use the dirty Strix tree in-place,
and it must not record a proof pass from an isolated tree that lacks the A733
prerequisite files.

## Patch Staging

Copy the local preview patch into the proof host or regenerate the same delta
from the authority packet. Then run:

```sh
git -C "$PROOF_TREE" apply --check "$PATCH"
git -C "$PROOF_TREE" apply "$PATCH"
git -C "$PROOF_TREE" diff --check -- \
  arch/arm64/boot/dts/allwinner/sun60i-a733.dtsi \
  arch/arm64/boot/dts/allwinner/sun60i-a733-cubie-a7s.dts
git -C "$PROOF_TREE" diff -- \
  arch/arm64/boot/dts/allwinner/sun60i-a733.dtsi \
  arch/arm64/boot/dts/allwinner/sun60i-a733-cubie-a7s.dts \
  > "$LOG_DIR/a733-dts-v2-uart-pinctrl.patch"
```

Stop if the patch changes anything beyond the UART0 pinctrl label movement
defined in `task-packets/kernel/a733-dts-v2-local-delta-plan.md`.

## Static Proof Commands

Run from the isolated proof tree:

```sh
make -C "$PROOF_TREE" O="$BUILD_DIR" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig \
  2>&1 | tee "$LOG_DIR/defconfig.log"
make -C "$PROOF_TREE" O="$BUILD_DIR" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
  allwinner/sun60i-a733-cubie-a7s.dtb \
  2>&1 | tee "$LOG_DIR/dtb.log"
make -C "$PROOF_TREE" O="$BUILD_DIR" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- CHECK_DTBS=y \
  allwinner/sun60i-a733-cubie-a7s.dtb \
  2>&1 | tee "$LOG_DIR/check-dtbs.log"
"$PROOF_TREE/scripts/checkpatch.pl" --strict "$LOG_DIR/a733-dts-v2-uart-pinctrl.patch" \
  2>&1 | tee "$LOG_DIR/checkpatch-strict.log"
"$PROOF_TREE/scripts/get_maintainer.pl" "$LOG_DIR/a733-dts-v2-uart-pinctrl.patch" \
  2>&1 | tee "$LOG_DIR/get-maintainer.log"
```

Do not record a pass if any command fails.

## Evidence To Record

A future proof packet should record:

- host, kernel, tool paths, source tree, proof tree, and build directory
- proof tree base commit and final dirty state
- patch path and SHA-256
- DTB path and SHA-256
- `defconfig.log`
- `dtb.log`
- `check-dtbs.log`
- `checkpatch-strict.log`
- `get-maintainer.log`
- final `git -C "$PROOF_TREE" status --short --branch`
- no-send posture
- no-hardware posture: no boot, no install, no UART capture, no power action

## Cleanup Expectation

The future proof cycle should either remove the temporary worktree after
recording evidence or record why it was intentionally retained:

```sh
git -C "$HOST_TREE" worktree remove "$PROOF_TREE"
rm -rf "$BUILD_DIR"
```

Do not remove logs before their hashes and locations are recorded.

## Stop Conditions

- authority files no longer permit local-only static proof
- Strix is unavailable
- the host tree is missing or not the expected source tree
- A733 prerequisite DTS/DTSI files are untracked and the isolation method would
  omit them
- toolchain, `dtc`, `checkpatch.pl`, or `get_maintainer.pl` is unavailable
- an isolated proof tree cannot be created
- the patch no longer applies cleanly
- the patch changes more than the DTS v2 UART0 pinctrl move
- any build, DT schema, checkpatch, or maintainer-routing command fails
- the future cycle would need hardware, public communication, or a public push
