# A733-SDMMC-H243: Common Update-Bit A523 Focused Check

Captured: 2026-06-13T08:24:00Z

## Purpose

Follow up H242 by checking the common update-bit prototype against the
non-A733 update-bit user that makes the common approach broader: A523.

This packet is documentation only. It is not a source change, not a v2, not a
resend approval, not a hardware action, and not a service, cron, mail-routing,
or model-routing change.

## Prototype

Recreated the H242 temporary prototype from exact H200/H215 source commit:

```text
de486cb24c361a86cba26738f24332df780872b0
```

Prototype shape:

- Add a common helper in `ccu_common.c` that iterates `desc->ccu_clks`.
- For each clock carrying `CCU_FEATURE_UPDATE_BIT`, read its register and write
  it back with `CCU_SUNXI_UPDATE_BIT` set.
- Call that helper in `sunxi_ccu_probe()` after base/lock assignment and before
  clock registration.
- Remove the A733-specific NSI update-bit pulse from the A733 CCU probe path.

Prototype diffstat:

```text
drivers/clk/sunxi-ng/ccu-sun60i-a733.c |  7 -------
drivers/clk/sunxi-ng/ccu_common.c      | 21 +++++++++++++++++++++
2 files changed, 21 insertions(+), 7 deletions(-)
```

## Validation

Used the recorded H201/H200 build config:

```text
dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202
```

Focused GCC `W=1` object build:

```text
drivers/clk/sunxi-ng/ccu_common.o: present
drivers/clk/sunxi-ng/ccu-sun55i-a523.o: present
drivers/clk/sunxi-ng/ccu-sun60i-a733.o: present
warning/error grep: no matching lines
```

Focused sparse `C=1 CHECK=sparse` object check:

```text
sparse version: 0.6.4
drivers/clk/sunxi-ng/ccu_common.o: checked
drivers/clk/sunxi-ng/ccu-sun55i-a523.o: checked
drivers/clk/sunxi-ng/ccu-sun60i-a733.o: checked
warning/error/sparse diagnostic grep: no matching lines
```

The temporary worktree was removed after the check. The exact H200 source tree
remained clean.

## Interpretation

The H242 common update-bit helper remains mechanically viable when the known
non-A733 update-bit user is checked explicitly. This reduces the immediate
build/static-analysis risk of a maintainer-directed common-helper v2.

It does not remove the semantic review risk: common handling still commits
boot-programmed state for all clocks carrying `CCU_FEATURE_UPDATE_BIT`, not only
A733 NSI. H215 should remain the default submitted posture because it is the
narrow exact-hardware-proven A733 expression.

## Next Action

If maintainers ask for common handling, H242 plus H243 provide the starting
point for a v2 design. A real v2 would still need full patch authoring, broader
validation, and A733 hardware proof before any resend or new submission.
