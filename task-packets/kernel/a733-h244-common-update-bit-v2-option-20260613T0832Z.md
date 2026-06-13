# A733-SDMMC-H244: Common Update-Bit V2 Option

Captured: 2026-06-13T08:32:00Z

## Purpose

Turn the H242/H243 common update-bit prototype into a maintainer-style local
patch artifact, so a common-helper v2 option is ready if maintainers ask for
one.

This packet is documentation and local prep only. It is not a resend approval,
not a new public thread, not a replacement for H215, not a hardware action, and
not a service, cron, mail-routing, or model-routing change.

## Artifact

Local artifact directory:

```text
task-packets/kernel/a733-h244-common-update-bit-v2-option/
```

Files:

```text
0001-clk-sunxi-ng-commit-update-bit-clocks-during-registr.patch
checkpatch-strict.txt
commit.txt
```

Temporary commit:

```text
087197b127e00a691e6b7aba04684916a6c0efe1
```

Base:

```text
de486cb24c361a86cba26738f24332df780872b0
```

Patch subject:

```text
clk: sunxi-ng: commit update-bit clocks during registration
```

## Patch Shape

The patch:

- adds a common helper in `ccu_common.c`;
- iterates `desc->ccu_clks` after base/lock assignment;
- for each `CCU_FEATURE_UPDATE_BIT` clock, writes back the current register
  value with `CCU_SUNXI_UPDATE_BIT` set;
- removes the A733-specific NSI update-bit pulse from the A733 CCU probe path.

Diffstat:

```text
drivers/clk/sunxi-ng/ccu-sun60i-a733.c |  7 -------
drivers/clk/sunxi-ng/ccu_common.c      | 21 +++++++++++++++++++++
2 files changed, 21 insertions(+), 7 deletions(-)
```

## Validation

Formatted patch checks:

```text
git diff --check HEAD~1..HEAD: PASS
scripts/checkpatch.pl --strict --show-types: PASS
git am --3way from recorded base: PASS
applied patch diffcheck: PASS
```

Focused build/static checks after applying the formatted patch from the
recorded base:

```text
arm64 GCC W=1 ccu_common.o: PASS
arm64 GCC W=1 ccu-sun55i-a523.o: PASS
arm64 GCC W=1 ccu-sun60i-a733.o: PASS
arm64 sparse C=1 ccu_common.o: PASS
arm64 sparse C=1 ccu-sun55i-a523.o: PASS
arm64 sparse C=1 ccu-sun60i-a733.o: PASS
sparse version: 0.6.4
diagnostic grep: no warning/error/sparse lines
```

Temporary worktrees were removed after the checks. The exact H200 source tree
remained clean.

## Interpretation

This artifact is a checkpatch-clean maintainer-style patch option for the
common update-bit direction. It is useful if reviewers say H215 patch 3 should
be expressed in common sunxi-ng code instead of as an A733-specific NSI pulse.

It should not replace H215 by default. H215 remains the currently submitted,
exact hardware-proven narrow A733 expression. The H244 patch is broader because
it commits boot-programmed state for every `CCU_FEATURE_UPDATE_BIT` clock in a
registered CCU descriptor, including A523 clocks.

## Next Action

Keep H215 as the submitted posture. If maintainer feedback asks for common
handling, use this artifact as the starting point for a real v2, then rerun full
validation including A733 hardware proof before any resend or new submission.
