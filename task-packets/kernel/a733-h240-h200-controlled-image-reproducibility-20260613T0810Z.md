# A733-SDMMC-H240: H200 Controlled Image Reproducibility

Captured: 2026-06-13T08:10:00Z

## Purpose

Follow up on H238's note that the rebuilt `Image` was clean and nonzero but
not bit-identical to the H201 proof `Image`. This check tests whether the
preserved H201 proof `Image` can be reproduced when the visible kernel build
metadata is controlled.

This packet is documentation only. It does not change kernel source, board
state, services, cron jobs, model routing, mail routing, or public submission
state.

## Mailbox Boundary

Before switching to source-side work, the available Gmail connector profile was
checked. It is not the H215 sender mailbox. A narrow read-only search in that
connected mailbox for H215 Message-ID, subject, source-head, and patch-title
markers returned no results. Because the connected mailbox is not the H215
sender mailbox, this is not authoritative sender-delivery evidence and does not
change H219's resend gate.

## Inputs

- Source tree: exact H200/H215 source tree on the build host
- Exact source commit: `de486cb24c361a86cba26738f24332df780872b0`
- H201 proof package: preserved H200 boot-artifact package on the build host
- H201 proof `Image` SHA256:
  `8a159596dbfcd4e430aab6120e6860b0a25b617cefb8398e95318dbc05732a36`
- H201 proof DTB SHA256:
  `6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a`
- H201 proof config SHA256:
  `dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202`

The H201 proof `Image` includes this visible version string. The local builder
identity is redacted as `builder@build-host` in this public-safe note:

```text
Linux version 7.1.0-rc5-00181-gde486cb24c36 (builder@build-host) (aarch64-linux-gnu-gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0, GNU ld (GNU Binutils for Ubuntu) 2.46) #1 SMP PREEMPT Sat Jun 13 02:09:01 EDT 2026
```

## Method

Created a temporary detached worktree on the build host from exact H200 commit
`de486cb24c361a86cba26738f24332df780872b0`, copied the H201 proof config, and
rebuilt `Image` plus `allwinner/sun60i-a733-cubie-a7s.dtb` with:

```sh
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-
export KBUILD_BUILD_USER=<proof builder user>
export KBUILD_BUILD_HOST=<proof builder host>
export KBUILD_BUILD_VERSION=1
export KBUILD_BUILD_TIMESTAMP="Sat Jun 13 02:09:01 EDT 2026"
make olddefconfig
make -j$(nproc) Image allwinner/sun60i-a733-cubie-a7s.dtb
```

The temporary worktree was removed after the check. The H200 source tree
remained clean.

## Result

- Build return code: `0`
- Build diagnostics grep for `warning:` or `error:`: no matching lines
- Rebuilt config SHA256:
  `dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202`
- Rebuilt DTB SHA256:
  `6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a`
- Rebuilt `Image` SHA256:
  `72fd8ef1ea70b2e7badab2dec84a38d9f84f2f67e013a5ba29fc954e2aec9f1e`

Comparison with H201 proof artifacts:

```text
config: MATCH
DTB:    MATCH
Image:  DIFFER
```

The rebuilt `Image` and H201 proof `Image` have the same size:

```text
43309568 bytes
```

The rebuilt `Image` contains the same visible Linux version string as the H201
proof `Image`. The local builder identity is again redacted here:

```text
Linux version 7.1.0-rc5-00181-gde486cb24c36 (builder@build-host) (aarch64-linux-gnu-gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0, GNU ld (GNU Binutils for Ubuntu) 2.46) #1 SMP PREEMPT Sat Jun 13 02:09:01 EDT 2026
```

The first byte differences were inside the `Image` despite identical size and
visible version metadata.

## Interpretation

The exact H200/H215 source state is still cleanly buildable, and the Cubie A7S
DTB remains byte-identical to the H201 hardware-proof DTB when build metadata
is controlled.

The H201 proof `Image` is not bit-for-bit reproducible from the currently
recorded source, config, toolchain, and visible `KBUILD_BUILD_*` metadata alone.
This does not weaken the H201 boot proof, because H201 records the exact
artifact hashes that were staged and booted. It only means future records should
avoid claiming `Image` reproducibility unless additional build-environment
inputs are captured or controlled.

For maintainer-facing purposes, this reinforces the current wording: H201 is an
exact-artifact hardware proof, while H238/H240 prove clean rebuildability and
DTB reproducibility, not bit-identical `Image` reproduction.

## Next Action

Do not spend more cycles on `Image` bit-for-bit reproduction unless a maintainer
asks for it or a future proof pipeline needs reproducible boot artifacts. The
mainline path remains waiting for H215 public indexing, sender-mailbox delivery
evidence, or maintainer response under the H219 resend gate.
