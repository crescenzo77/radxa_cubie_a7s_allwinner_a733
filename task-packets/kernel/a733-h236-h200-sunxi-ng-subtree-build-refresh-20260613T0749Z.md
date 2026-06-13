# A733-SDMMC-H236: H200 sunxi-ng Subtree Build Refresh

Captured: 2026-06-13T07:49:34Z

## Purpose

Refresh bounded integration-build evidence for the exact H200/H215 source state
by building the whole `drivers/clk/sunxi-ng/` subtree.

This packet is documentation only. It is not a resend approval, not a new mail
draft, not a source change, and not a hardware action.

## Scope

- Host role: build host
- Source worktree: temporary detached worktree from exact H200
- Exact source commit: `de486cb24c361a86cba26738f24332df780872b0`
- Build config: recorded H200 build configuration
- Build config SHA256: `dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202`
- Compiler: `aarch64-linux-gnu-gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0`

## Method

Created a temporary detached worktree from the exact H200 commit, copied the
recorded H200 build `.config`, ran `olddefconfig`, then ran:

```sh
make -C "$wt" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- W=1 \
  drivers/clk/sunxi-ng/
```

The temporary worktree was removed after the check. The source H200 worktree
was not modified.

## Result

- Subtree build return code: `0`
- Diagnostic grep for `warning:` or `error:`: no matching lines
- `drivers/clk/sunxi-ng/ccu-sun60i-a733.o` was built
- `drivers/clk/sunxi-ng/built-in.a` was produced
- Temporary worktree status at end of build: clean

The build included the shared sunxi-ng helpers and the relevant A733/A523 clock
drivers, including:

- `ccu_common.o`
- `ccu_gate.o`
- `ccu_mux.o`
- `ccu_div.o`
- `ccu_mp.o`
- `ccu-sun55i-a523.o`
- `ccu-sun60i-a733-rtc.o`
- `ccu-sun60i-a733.o`
- `ccu-sun60i-a733-r.o`

## Interpretation

The exact H200/H215 source state has a clean bounded arm64 `W=1` GCC build for
the whole `drivers/clk/sunxi-ng/` subtree under the recorded H200 build
configuration.

This complements, but does not replace, H201 hardware proof, H223/H230
reproducibility and artifact-integrity checks, H225 focused GCC `W=1`, H227
sparse, and H228 Clang/LLVM object-build evidence.

## Next Action

Continue to wait for H215 public indexing or maintainer response. Do not send a
duplicate follow-up unless H219's resend/alternate-action gate is satisfied.
