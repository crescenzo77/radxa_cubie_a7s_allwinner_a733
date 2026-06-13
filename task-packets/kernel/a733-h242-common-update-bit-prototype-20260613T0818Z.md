# A733-SDMMC-H242: Common Update-Bit Prototype

Captured: 2026-06-13T08:18:00Z

## Purpose

Prepare for likely maintainer feedback on H215 patch 3: whether the A733 NSI
probe-time update-bit pulse should instead be handled in common sunxi-ng code
for all clocks marked with `CCU_FEATURE_UPDATE_BIT`.

This packet is documentation only. It is not a source change, not a v2, not a
resend approval, not a hardware action, and not a change to services, cron jobs,
mail routing, or model routing.

## Baseline

Exact source commit:

```text
de486cb24c361a86cba26738f24332df780872b0
```

Relevant baseline behavior:

- Gate, mux, and divider helper writes already OR `CCU_SUNXI_UPDATE_BIT` when
  `CCU_FEATURE_UPDATE_BIT` is present.
- MP parent changes delegate to the mux helper.
- MP rate changes do not OR `CCU_SUNXI_UPDATE_BIT`.
- Common CCU registration does not currently pulse the update bit for
  boot-programmed register state.
- H215 patch 3 handles only the A733 NSI register in the A733 CCU probe path.

## Prototype Shape

In a temporary detached build-host worktree, tested this maintainer-directed
alternative:

1. Add a small common helper in `ccu_common.c`.
2. After `sunxi_ccu_probe()` assigns each `ccu_common` object's base pointer
   and lock, iterate `desc->ccu_clks`.
3. For each clock with `CCU_FEATURE_UPDATE_BIT`, read its register and write it
   back with `CCU_SUNXI_UPDATE_BIT` set.
4. Remove the A733-specific NSI update-bit pulse from the A733 CCU probe path.

Prototype diffstat:

```text
drivers/clk/sunxi-ng/ccu-sun60i-a733.c |  7 -------
drivers/clk/sunxi-ng/ccu_common.c      | 21 +++++++++++++++++++++
2 files changed, 21 insertions(+), 7 deletions(-)
```

Core helper shape:

```c
static void sunxi_ccu_commit_update_bit_clks(const struct sunxi_ccu_desc *desc)
{
	int i;

	for (i = 0; i < desc->num_ccu_clks; i++) {
		struct ccu_common *cclk = desc->ccu_clks[i];
		unsigned long flags;
		u32 reg;

		if (!cclk || !(cclk->features & CCU_FEATURE_UPDATE_BIT))
			continue;

		spin_lock_irqsave(cclk->lock, flags);
		reg = readl(cclk->base + cclk->reg);
		writel(reg | CCU_SUNXI_UPDATE_BIT, cclk->base + cclk->reg);
		spin_unlock_irqrestore(cclk->lock, flags);
	}
}
```

The helper was called before clock registration, after base/lock assignment.

## Validation

Static checks in the temporary worktree:

```text
git diff --check: PASS
arm64 GCC W=1 drivers/clk/sunxi-ng/ subtree build: PASS
arm64 sparse C=1 ccu_common.o and ccu-sun60i-a733.o: PASS
```

Diagnostics:

```text
warning/error grep: no matching lines
sparse version: 0.6.4
```

The temporary worktree was removed after the check. The exact H200 source tree
remained clean.

## Breadth / Risk

This prototype is mechanically viable, but it is broader than H215 patch 3.
Existing checked update-bit definitions include:

```text
A523: 3 CCU_FEATURE_UPDATE_BIT clock definitions
A733: 4 CCU_FEATURE_UPDATE_BIT clock definitions
```

That breadth is the main review risk. The common helper would commit
boot-programmed state for every descriptor carrying `CCU_FEATURE_UPDATE_BIT`,
not only A733 NSI. That may be the right abstraction if maintainers prefer the
framework to own update-bit commit semantics, but it is not the narrow
hardware-proven expression currently submitted as H215.

## Interpretation

The common update-bit direction is buildable and sparse-clean as a prototype.
It is suitable as a maintainer-directed v2 option, especially if reviewers
prefer to make `CCU_FEATURE_UPDATE_BIT` imply "commit the boot-programmed state
once during CCU registration."

Do not switch away from the H215 A733-specific NSI pulse by default. H215 is the
exact hardware-proven narrow form. The common helper is broader and should be
used only if maintainer feedback asks for common handling or accepts the
broader semantics.

## Next Action

Keep H215 as the current submitted posture. If maintainers ask for common
handling, use this packet as the starting point for a v2 design discussion and
rerun full validation, including at least A733 hardware proof and broader
sunxi-ng build/static coverage.
