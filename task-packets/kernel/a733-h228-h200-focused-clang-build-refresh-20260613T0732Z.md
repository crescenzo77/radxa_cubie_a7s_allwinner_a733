# A733-SDMMC-H228: H200 Focused Clang Build Refresh

Captured: 2026-06-13T07:32:41Z

## Purpose

Refresh alternate-toolchain build evidence for the exact H200/H215 source state
without changing kernel source, services, board state, or model routing.

## Scope

- Host role: build host
- Source worktree: clean final H200 maintainer-polish worktree
- Exact source commit: `de486cb24c361a86cba26738f24332df780872b0`
- Source worktree status before check: clean
- Build config: recorded H200 build configuration
- Build config SHA256: `dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202`
- Clang version: `Ubuntu clang version 21.1.8 (6ubuntu1)`
- LLVM tool availability: `clang`, `ld.lld`, `llvm-ar`, `llvm-nm`, and
  `llvm-objcopy` were present

## Method

Created a temporary detached worktree from the exact H200 commit, copied the
recorded H200 build `.config`, ran `olddefconfig` with LLVM enabled, then ran a
focused Clang/LLVM object build:

```sh
make -C "$wt" ARCH=arm64 LLVM=1 olddefconfig
make -C "$wt" ARCH=arm64 LLVM=1 W=1 \
  drivers/clk/sunxi-ng/ccu-sun60i-a733.o
```

The temporary worktree was removed after the check. The source H200 worktree
was not modified.

## Result

- Focused Clang/LLVM object build return code: `0`
- Diagnostic grep for `warning:` or `error:`: no matching lines
- Built object: `drivers/clk/sunxi-ng/ccu-sun60i-a733.o`
- Temporary worktree status at end of build: clean

## Interpretation

The exact H200/H215 source state has a clean focused arm64 Clang/LLVM `W=1`
object build for the A733 CCU driver under the recorded H200 build
configuration.

This complements, but does not replace, H201 hardware proof, H223 post-send
reproducibility, H225 GCC `W=1` evidence, and H227 sparse evidence.

## Next Action

Continue to wait for H215 public indexing or maintainer response. Do not send a
duplicate follow-up unless H219's resend/alternate-action gate is satisfied.
