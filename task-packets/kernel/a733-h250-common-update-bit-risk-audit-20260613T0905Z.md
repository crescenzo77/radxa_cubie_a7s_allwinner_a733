# A733-SDMMC-H250: Common Update-Bit Risk Audit

Captured: 2026-06-13T09:05Z

## Purpose

Audit the H245 common update-bit implementation after the H247 hardware proof,
with an eye toward maintainer review risk rather than additional mechanical
testing.

This packet is documentation only. It is not a source change, not a resend
approval, and not a new public thread.

## Implementation Shape Reviewed

H245 patch 3 adds:

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

It is called from `sunxi_ccu_probe()` after every `ccu_common` has `base` and
`lock` assigned, and before any clock hardware is registered for consumers.

## Ordering Assessment

The placement is defensible:

- `cclk->base` has been assigned;
- `cclk->lock` has been assigned;
- no consumer-visible clocks have been registered yet;
- the common CCU spinlock is initialized;
- the write is protected by the same lock used by the normal helper paths.

This avoids a consumer race and makes the helper a provider-internal
registration step.

## Scope Assessment

Checked update-bit clocks in the H215/H245 base:

```text
A523: mbus, iommu, dram
A733: nsi, mbus, gpu, dram
```

H245 therefore intentionally broadens patch 3 from:

```text
A733 NSI-only probe-time write
```

to:

```text
all clocks carrying CCU_FEATURE_UPDATE_BIT in each registered descriptor
```

That broadening is the main maintainer-review risk and should remain explicit
in any v2 framing.

## Existing Helper Behavior

The existing helper paths already OR `CCU_SUNXI_UPDATE_BIT` for some active
operations:

- gate enable/disable helpers;
- mux parent changes;
- simple divider rate changes.

However, checked MP/NM/NKMP rate helpers write registers without a generic
`CCU_FEATURE_UPDATE_BIT` OR in the snippets inspected. This matters for review
framing:

- H245 is a probe-time commit of boot-programmed state.
- H245 is not a complete audit or fix of every future update-bit rate-change
  path.
- If maintainers ask whether MP `set_rate()` also needs common update-bit
  handling, that is a separate follow-up question, not something H247 proves.

## Hardware Evidence Boundary

H247 proves the H245 common-helper option on Radxa Cubie A7S through:

- unused-clock cleanup;
- unused power-domain cleanup;
- SDMMC0 initialization;
- SD card enumeration as `mmcblk0` with partitions;
- read-only ext4 root mount;
- `/bin/sh`.

H247 does not prove:

- A523 runtime behavior;
- GPU or DRAM dynamic rate-change behavior;
- every possible consumer-driven update-bit clock operation;
- that common probe-time handling is preferable to the narrow A733 NSI write.

## Recommended Review Position

If maintainers ask for common update-bit handling, H245/H247 is a valid v2
starting point, but the cover/reply should say:

```text
This common helper is scoped to committing boot-programmed update-bit state
once during CCU registration. It does not claim to audit every later set_rate()
path for update-bit clocks. If reviewers prefer, that can be handled as a
separate framework cleanup.
```

If maintainers do not ask for common handling, keep H215 as the narrower
submitted posture.

## Next Action

No source edit is required solely from this audit. Keep H250 as response
material for common-helper review questions and as a reminder not to overclaim
H247.
