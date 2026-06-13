# A733 H187 source-shape comment review

Captured: 2026-06-13T05:45Z

## Purpose

Review the source context around the H153/H154 CCU/NSI changes so a future
approved materialization pass can add comments where they help maintainer
review, without creating kernel commits now.

This note is documentation only. It does not approve kernel-source commits,
hardware runs, Cubie staging, patch publication, sending mail, service changes,
cron changes, or model-routing changes.

## Source context inspected

Read-only source context was inspected around:

- the `nsi` and `bus-nsi` clock definitions;
- the `ahb-store` and `ahb-cpus` gate definitions;
- the `mbus-msi-lite0` and `mbus-store` gate definitions;
- the A733 CCU probe path where the NSI update bit is pulsed.

## Current raw-diff shape

The H153/H154 raw diffs are intentionally minimal. They mostly change flags
and add the NSI update write. That is useful for preserving evidence, but the
future maintainer-facing commits should consider adding small source comments
where the hardware dependency is otherwise invisible from the clock name.

## Patch 1 comment guidance

Patch 1 changes `ahb-cpus` from non-critical to `CLK_IS_CRITICAL`.

The source currently places `ahb-cpus` beside nearby AHB gates, immediately
after `ahb-store`. There is no comment explaining that the CPU-visible path to
R-domain registers depends on this bridge.

Future materialization should consider adding a short comment immediately
before `ahb_cpus_clk`, for example:

```c
/*
 * The CPU reaches the R-CCU and RTC register windows through this bridge
 * into the CPUS/R domain. Keep it enabled so later R-domain register
 * accesses do not stall after clk_disable_unused().
 */
```

This comment belongs with patch 1, not patch 2 or patch 3, because it explains
the standalone CPUS bridge fix and avoids blending it with the SDMMC0/NSI
root-device story.

## Patch 2 comment guidance

Patch 2 changes storage and NSI fabric clocks to `CLK_IS_CRITICAL`.

The source groups the relevant definitions in two places:

- `nsi` and `bus-nsi` near the NSI parent list;
- `ahb-store`, `mbus-msi-lite0`, and `mbus-store` near the AHB and MBUS gate
  lists.

Do not over-comment every gate. The commit message can carry most of the
evidence and uncertainty. If a source comment is added, keep it broad and
avoid claiming that `mbus-msi-lite0` is independently proven required.

Safe wording for H153 if a comment is desired:

```c
/*
 * SDMMC0 normal IDMA needs the storage and NSI fabric path kept alive.
 * Keep the verified fabric bundle enabled until the dependency can be
 * represented by a more specific consumer or fabric model.
 */
```

If H154 passes and patch 2 omits `mbus-msi-lite0`, use the same broad wording
without mentioning `mbus-msi-lite0`.

## Patch 3 comment guidance

Patch 3 currently adds `SUN60I_A733_NSI_REG` near the NSI clock definition and
pulses `CCU_SUNXI_UPDATE_BIT` during A733 CCU probe, before the PLL audio
quirk.

That placement is reasonable because it happens after the register base is
mapped and before the common CCU registration call. The current raw-diff
comment is short:

```c
/*
 * Boot firmware can leave the NSI mux/divider configuration pending;
 * commit it before fabric consumers start probing.
 */
```

Future materialization can keep this comment, but the commit message should
carry the nuance from H171:

- the update bit is self-clearing;
- helper paths can pulse it when operations run;
- the tested boot path did not have an early consumer operation that committed
  NSI before SDMMC0 normal IDMA needed the fabric;
- the pulse alone was insufficient without the NSI/storage fabric keepalive
  set.

Do not expand the source comment into a long hardware-test narrative.

## Patch boundary recommendation

Keep the three-patch boundary from H153/H154:

1. CPUS bridge criticality.
2. Storage and NSI fabric keepalive.
3. NSI update-bit commit.

This keeps the independently reviewable CPUS bridge issue separate from the
more policy-heavy fabric keepalive issue and the update-bit design question.

## Maintainer risk notes

- `CLK_IS_CRITICAL` is blunt. H176/H170 should keep asking maintainers whether
  a more explicit consumer or fabric model is preferred.
- Patch 2 is the highest discussion-risk patch because it encodes fabric
  policy, and H153 keeps one clock that is not independently isolated.
- Patch 3 may trigger a broader sunxi-ng design discussion about
  registration-time treatment for update-bit MP clocks.

## Guardrails

- Do not edit kernel source from this review without explicit approval.
- Do not create a materialization worktree without explicit approval.
- Do not use H154 patch 2 unless the H157 proof passes.
- Do not use Cubie1.
