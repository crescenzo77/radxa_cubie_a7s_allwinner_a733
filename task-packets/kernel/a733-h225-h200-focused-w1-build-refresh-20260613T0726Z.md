# A733-SDMMC-H225: H200 Focused W=1 Build Refresh

Captured: 2026-06-13T07:26:06Z

## Purpose

Refresh focused compiler-warning evidence for the exact H200/H215 source state
without changing kernel source, services, board state, or model routing.

## Scope

- Host role: build host
- Source worktree: clean final H200 maintainer-polish worktree
- Exact source commit: `de486cb24c361a86cba26738f24332df780872b0`
- Branch at source worktree: final H200 maintainer-polish branch
- Source worktree status before check: clean
- Build config: recorded H200 build configuration
- Build config SHA256: `dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202`
- Compiler: `/usr/bin/aarch64-linux-gnu-gcc`
- Compiler version: `aarch64-linux-gnu-gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0`

## Method

Created a temporary detached worktree from the exact H200 commit, copied the
H200 build `.config`, ran `olddefconfig`, then ran a focused W=1 object build:

```sh
make -C "$wt" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- olddefconfig
make -C "$wt" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- W=1 \
  drivers/clk/sunxi-ng/ccu-sun60i-a733.o
```

The temporary worktree was removed after the check. The source H200 worktree
was not modified.

## Result

- Focused object build return code: `0`
- Warning/error grep for `warning:` or `error:`: no matching lines
- Built object: `drivers/clk/sunxi-ng/ccu-sun60i-a733.o`
- Temporary worktree status at end of build: clean

## Interpretation

The exact H200/H215 source state still has a clean focused arm64 `W=1` object
build for the A733 CCU driver under the recorded H200 build configuration.

This does not replace the H201 hardware proof or the H223 post-send
reproducibility check. It only refreshes focused compiler-warning confidence
for the touched driver.

## Next Action

Continue to wait for H215 public indexing or maintainer response. Do not send a
duplicate follow-up unless H219's resend/alternate-action gate is satisfied.
