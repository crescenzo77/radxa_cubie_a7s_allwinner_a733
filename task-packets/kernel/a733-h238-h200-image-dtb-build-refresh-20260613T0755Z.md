# A733-SDMMC-H238: H200 Image/DTB Build Refresh

Captured: 2026-06-13T07:55:12Z

## Purpose

Refresh full boot-artifact build evidence for the exact H200/H215 source state
without installing artifacts, changing source, sending mail, changing services,
or touching hardware.

This packet is documentation only. It is not a resend approval, not a new mail
draft, not a source change, not a boot package, and not a hardware action.

## Scope

- Host role: build host
- Source worktree: temporary detached worktree from exact H200
- Exact source commit: `de486cb24c361a86cba26738f24332df780872b0`
- Build config: recorded H200 build configuration
- Build config SHA256: `dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202`
- Target DTB: `allwinner/sun60i-a733-cubie-a7s.dtb`
- Build parallelism: `-j32`

## Method

Created a temporary detached worktree from the exact H200 commit, copied the
recorded H200 build `.config`, ran `olddefconfig`, then ran:

```sh
make -C "$wt" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j32 \
  Image allwinner/sun60i-a733-cubie-a7s.dtb
```

The temporary worktree was removed after the check. The source H200 worktree
was not modified. No artifact was staged to any board.

## Result

- Image/DTB build return code: `0`
- Diagnostic grep for `warning:` or `error:`: no matching lines
- Temporary worktree status at end of build: clean

Generated artifact hashes:

```text
05c6fd1ac3aa9311be1e6b4bcb48ad05ab14189c7dea574410d3b4d2151efc70  arch/arm64/boot/Image
6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a  arch/arm64/boot/dts/allwinner/sun60i-a733-cubie-a7s.dtb
dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202  .config
```

Artifact sizes:

```text
arch/arm64/boot/Image                                      43309568 bytes
arch/arm64/boot/dts/allwinner/sun60i-a733-cubie-a7s.dtb       4705 bytes
.config                                                     321548 bytes
```

## Comparison To H201

The rebuilt DTB hash matches the H201 exact hardware-proof DTB hash:

```text
6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a
```

The rebuilt Image is nonzero and built cleanly, but its SHA256 differs from the
H201 proof Image hash. Treat that as expected build metadata drift unless a
future reproducibility task controls kernel build timestamps and version
strings explicitly. This H238 check is a buildability refresh, not a claim of
bit-for-bit Image reproducibility.

## Interpretation

The exact H200/H215 source still builds a clean arm64 `Image` and Radxa Cubie
A7S DTB from the recorded H200 configuration. The DTB is byte-identical to the
H201 proof DTB; the Image remains buildable but is not claimed bit-identical.

This complements H201 hardware proof, H223/H230 apply/source-equivalence
checks, H225/H227/H228 focused object checks, and H236 sunxi-ng subtree build
coverage.

## Next Action

Continue to wait for H215 public indexing or maintainer response. Do not send a
duplicate follow-up unless H219's resend/alternate-action gate is satisfied.
