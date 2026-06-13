# A733 DTS v2 Static Proof Isolated-Copy Packet

Status: local-only; no-run; no-send
Updated: 2026-06-13

This packet defines the allowed future static-proof method when Strix A733
prerequisite files remain untracked. It is not a build log, not a patch, not
static proof, not send approval, and not permission to mutate kernel trees or
hardware. It is also not static proof and not permission to mutate kernel trees or hardware.

Do not execute this packet unless a future cycle explicitly contracts a static
proof run after rereading the authority files.

## Why This Exists

Read-only preflight in
`task-packets/kernel/a733-dts-v2-static-proof-preflight.md` confirmed that
these required files are untracked in the observed Strix tree:

- `arch/arm64/boot/dts/allwinner/sun60i-a733.dtsi`
- `arch/arm64/boot/dts/allwinner/sun60i-a733-cubie-a7s.dts`

Because those files are untracked, a plain detached worktree at
`8fde5d1d47f69db6082dfa34500c27f8485389a5` would omit them. A future proof pass
must either use a committed prerequisite branch or make an isolated copy that
preserves the untracked A733 prerequisite files.

## Required Inputs

- source host: `strix`
- source tree: `/srv/projects/cubie-a7s-armbian/sources/mainline-linux`
- observed head: `8fde5d1d47f69db6082dfa34500c27f8485389a5`
- preview patch:
  `task-packets/kernel/a733-dts-v2-uart-pinctrl-local-preview.patch`
- proof plan:
  `task-packets/kernel/a733-dts-v2-static-proof-plan.md`
- preflight:
  `task-packets/kernel/a733-dts-v2-static-proof-preflight.md`

## Future Contract Shape

A future execution cycle must record a fresh scope contract before running any
command. That contract must name:

- source tree
- isolated proof tree
- build output directory
- log directory
- patch path
- exact files expected to be preserved
- cleanup rule
- stop condition

## No-Run Command Template

This template is a recipe only. It was not run by this cycle.

```sh
set -eu

SOURCE_TREE=/srv/projects/cubie-a7s-armbian/sources/mainline-linux
PROOF_TREE=/tmp/a733-dts-v2-static-proof-tree
BUILD_DIR=/tmp/a733-dts-v2-static-proof-build
LOG_DIR=/tmp/a733-dts-v2-static-proof-logs
PATCH=/tmp/a733-dts-v2-uart-pinctrl-local-preview.patch

rm -rf "$PROOF_TREE" "$BUILD_DIR" "$LOG_DIR"
mkdir -p "$LOG_DIR"

rsync -a --delete \
  --exclude .git/worktrees \
  "$SOURCE_TREE"/ "$PROOF_TREE"/

git -C "$SOURCE_TREE" status --short --branch > "$LOG_DIR/source-status.txt"
git -C "$SOURCE_TREE" rev-parse HEAD > "$LOG_DIR/source-head.txt"
git -C "$PROOF_TREE" status --short --branch > "$LOG_DIR/proof-status-before.txt"
git -C "$PROOF_TREE" rev-parse HEAD > "$LOG_DIR/proof-head.txt"

sha256sum \
  "$SOURCE_TREE/arch/arm64/boot/dts/allwinner/sun60i-a733.dtsi" \
  "$SOURCE_TREE/arch/arm64/boot/dts/allwinner/sun60i-a733-cubie-a7s.dts" \
  "$SOURCE_TREE/arch/arm64/boot/dts/allwinner/Makefile" \
  > "$LOG_DIR/source-prereq-sha256.txt"

sha256sum \
  "$PROOF_TREE/arch/arm64/boot/dts/allwinner/sun60i-a733.dtsi" \
  "$PROOF_TREE/arch/arm64/boot/dts/allwinner/sun60i-a733-cubie-a7s.dts" \
  "$PROOF_TREE/arch/arm64/boot/dts/allwinner/Makefile" \
  > "$LOG_DIR/proof-prereq-sha256.txt"

diff -u "$LOG_DIR/source-prereq-sha256.txt" "$LOG_DIR/proof-prereq-sha256.txt"
```

Stop before any patch or build command if the prerequisite hashes differ, if
any required file is missing, or if the proof tree does not preserve the A733
source shape recorded by preflight.

## Static Proof Continuation

Only after the isolated copy preserves prerequisite files, continue with the
static commands from:

```text
task-packets/kernel/a733-dts-v2-static-proof-command-packet.md
```

The future proof cycle must still record:

- patch hash
- DTB hash
- `defconfig.log`
- `dtb.log`
- `check-dtbs.log`
- `checkpatch-strict.log`
- `get-maintainer.log`
- final dirty-tree state
- no-send posture
- no-hardware posture: no boot, no install, no UART capture, no power action

## Cleanup

The future proof cycle should remove the isolated proof tree and build output
after evidence is recorded, or record why they were retained:

```sh
rm -rf "$PROOF_TREE" "$BUILD_DIR"
```

Do not remove logs before hashes and locations are recorded.

## Stop Conditions

- authority files no longer permit local-only static proof
- Strix is unavailable
- source tree is missing
- `rsync` is unavailable; in short, rsync is unavailable
- required A733 DTS/DTSI prerequisite files are missing
- prerequisite hashes do not match between source tree and isolated copy
- patch does not apply cleanly
- patch changes more than the UART0 pinctrl movement
- any static proof command fails
- the future cycle would need hardware, public communication, or a public push
