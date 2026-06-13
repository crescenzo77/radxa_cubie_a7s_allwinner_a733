# A733 DTS v2 Static Proof Plan

Status: local-only validation plan
Updated: 2026-06-13

This plan defines how to statically validate the held DTS v2 UART0 pinctrl
delta after a future kernel-tree edit. It is not a patch, not proof that the edit has already been made,
not send approval, and not permission to mutate hardware.

## Current Host Findings

Read-only inspection on the Mac-mini found:

- Clean sparse source tree:
  `/Users/enzo/projects/linux-a733-sparse`
- Clean sparse branch: `candidate/a733-platform-clean-v4`
- Clean sparse head: `abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e`
- Sparse tree limitation: no top-level `Makefile`, no `scripts/checkpatch.pl`,
  and no `scripts/get_maintainer.pl` are present in the sparse checkout.
- Full local source tree:
  `/Users/enzo/projects/linux-a733`
- Full tree branch: `candidate/a733-platform-clean-v6`
- Full tree head: `b1f20d455a600d33999cf893fdf0df8fb2ace538`
- Full tree limitation: known non-A733 dirty files remain under the checkout
  quarantine. Do not use it as a patch export source while quarantine remains
  active.
- Host tool availability: `/usr/bin/make`, `/opt/homebrew/bin/dtc`, and
  Python are present.
- Host tool gap: `aarch64-linux-gnu-gcc` was not found on PATH during this
  cycle.

## Required Validation Strategy

Local preview patch:

```text
task-packets/kernel/a733-dts-v2-uart-pinctrl-local-preview.patch
```

This preview only proves that the intended delta can be represented and checked
with `git apply --check` against the current clean sparse tree. It does not
prove DTB build, dt-schema, checkpatch, maintainer routing, or runtime behavior.

Host suitability for a future static proof is recorded in:

```text
task-packets/kernel/a733-dts-v2-static-validation-hosts.md
```

A no-run command packet for a future isolated Strix proof is recorded in:

```text
task-packets/kernel/a733-dts-v2-static-proof-command-packet.md
```

Current conclusion: Strix is the best observed future static-validation host
because it has a complete Linux source tree, `aarch64-linux-gnu-gcc`, `make`,
`dtc`, `scripts/checkpatch.pl`, and `scripts/get_maintainer.pl`. It must still
use a temporary clean worktree or another intentionally isolated tree because
the observed Strix mainline tree is dirty and detached.

Known prerequisite caveat: the observed Strix tree had A733 DTS prerequisite
files as untracked files. A detached worktree at the observed commit is not
sufficient unless a future preflight proves those files are committed or
otherwise present in the isolated proof tree.

Use a temporary full kernel worktree or a verified remote build tree for static
proof. Do not write build outputs into the source tree. Prefer an out-of-tree
build directory:

```sh
O=/tmp/a733-dts-v2-static-proof
```

The selected validation tree must satisfy all of these before a static proof
can be recorded as pass:

- complete Linux source checkout with top-level `Makefile`
- `scripts/checkpatch.pl` available
- `scripts/get_maintainer.pl` available
- clean or intentionally isolated worktree state
- A733 prerequisite DTS/DTSI files present in the isolated tree
- exact base commit and branch recorded
- DTS v2 UART0 pinctrl delta applied
- generated patch path recorded
- no public communication, public push, or hardware mutation
- future proof command packet reviewed against current authority files

## Static Commands

Run from the selected full source tree after applying the local DTS v2 delta:

```sh
git status --short --branch
git diff --check -- arch/arm64/boot/dts/allwinner/sun60i-a733.dtsi arch/arm64/boot/dts/allwinner/sun60i-a733-cubie-a7s.dts
make O="$O" ARCH=arm64 defconfig
make O="$O" ARCH=arm64 allwinner/sun60i-a733-cubie-a7s.dtb
make O="$O" ARCH=arm64 CHECK_DTBS=y allwinner/sun60i-a733-cubie-a7s.dtb
scripts/checkpatch.pl --strict <generated patch>
scripts/get_maintainer.pl <generated patch>
```

If cross-compilation is required by the selected host, add the exact
`CROSS_COMPILE=` value and record the compiler path. If the compiler is
missing, mark the static proof blocked; do not record a pass.

## Expected Output Packet

A future static proof packet must record:

- selected tree path, branch, and head
- whether the tree was temporary, sparse-expanded, remote, or full local
- `O=` build directory
- patch file path
- command transcript or log paths
- DTB path and hash
- generated patch hash
- `checkpatch.pl --strict` result
- `get_maintainer.pl` output path
- dirty-tree state after validation
- communication posture: local-only, no-send
- hardware posture: no boot, no install, no UART capture, no power action

## Stop Conditions

- no complete source tree is available
- selected tree is dirty outside the contracted DTS delta
- `aarch64-linux-gnu-gcc` or another required compiler is unavailable and no
  host-specific replacement is recorded
- `scripts/checkpatch.pl` or `scripts/get_maintainer.pl` is unavailable
- any validation command fails
- the patch grows beyond the UART0 pinctrl movement from
  `task-packets/kernel/a733-dts-v2-local-delta-plan.md`
- validation would require hardware mutation, public communication, or public
  push while local-only mode remains active
