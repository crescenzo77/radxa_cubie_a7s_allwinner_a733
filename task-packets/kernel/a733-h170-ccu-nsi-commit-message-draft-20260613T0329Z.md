# A733 H170 CCU/NSI commit-message draft

Captured: 2026-06-13T03:29Z

## Purpose

Prepare maintainer-quality commit-message text for the H153
evidence-preserving CCU/NSI split series, without committing kernel source,
generating sendable patches, running hardware, or sending mail.

This note is documentation only. It does not approve hardware runs, Cubie
staging, `/boot` writes, kernel commits, patch publication, service changes,
cron changes, or model-routing changes.

## Intended use

When kernel-source commit prep is explicitly approved, use this as the
starting point for real commits in a dedicated kernel worktree. After the
commits exist, regenerate patches with `git format-patch` and re-run normal
gates.

Do not send this note as mail. Do not paste these messages blindly; recheck
exact evidence and maintainer-thread state first.

## Series cover draft

```text
clk: sunxi-ng: a733: keep required fabric clocks enabled

This draft series records the CCU-side fixes that allowed Radxa Cubie A7S
(Allwinner A733 / SUN60IW2) boot testing to move past two clock/fabric
failures seen with the A733 CCU/RTC/pinctrl RFC stack.

The first patch is the narrowest and most independent fix: keep the
`ahb-cpus` bridge enabled so CPU accesses to R-CCU and RTC registers do
not stall after clk_disable_unused().

The second patch keeps the storage and NSI fabric clocks enabled. That is
the conservative, evidence-preserving shape that matched the hardware test
which let SDMMC0 normal IDMA enumerate the card and mount a read-only root
filesystem. One clock in that bundle, `mbus-msi-lite0`, has not yet been
isolated from the rest of the storage-fabric keepalive set, so the commit
message intentionally describes it as part of the verified bundle rather
than as independently proven required.

The third patch commits the boot-programmed NSI mux/divider state once
during A733 CCU probe using the existing sunxi-ng update-bit mechanism.
The update pulse alone was not sufficient in testing, but the pulse plus
the storage/NSI fabric keepalive set resolved the SDMMC0 normal-IDMA
root-device blocker.

These changes were tested on Radxa Cubie A7S over UART with mainline plus
the A733 CCU, RTC, and pinctrl RFC dependencies. The patches are being
split this way so that the CPUS bridge issue, the storage/NSI fabric
policy question, and the NSI update-bit question can be reviewed
separately.
```

## Patch 1 commit draft

Subject:

```text
clk: sunxi-ng: a733: keep the CPUS AHB bridge clock critical
```

Body:

```text
The A733 main CCU exposes an AHB gate for the bridge into the CPUS/R
domain. Linux has no regular device consumer for that bridge, but the CPU
still needs it in order to access the R-CCU and RTC register windows.

If clk_disable_unused() gates ahb-cpus, later R-domain register accesses
can stall the bus. Keep the bridge clock enabled for the lifetime of the
kernel, matching the hardware access path rather than a per-device
consumer.

On Radxa Cubie A7S testing, keeping this gate enabled let the unused-clock
walk complete and kept later R-CCU/RTC register accesses live.

Tested-on: Radxa Cubie A7S (A733 / SUN60IW2)
Signed-off-by: Enzo Adriano <enzo.adriano.code@gmail.com>
```

Notes before use:

- This is the strongest standalone patch.
- It can be discussed independently from the SDMMC0/NSI root-device blocker.
- Before committing, consider adding a short source comment if maintainers
  prefer the access-path rationale beside the clock definition.

## Patch 2 commit draft

Subject:

```text
clk: sunxi-ng: a733: keep storage and NSI fabric clocks critical
```

Body:

```text
Several A733 fabric clocks sit between storage bus masters and memory but
are not represented as ordinary device consumers. Letting the unused-clock
walk gate these clocks can leave SDMMC0 unable to complete its internal
clock/update or normal IDMA path even though the host controller itself has
probed.

Keep the storage AHB/MBUS lane and the NSI fabric clocks enabled. This is
the conservative hardware-verified shape for now: storage-fabric keepalive
removes the SDMMC0 clock-update timeout, and the same storage/NSI fabric
set together with the NSI update-bit commit lets SDMMC0 normal IDMA
enumerate the card and mount the root filesystem.

The `mbus-msi-lite0` gate was part of the verified storage-fabric bundle
but has not yet been isolated from `ahb-store` and `mbus-store`. Keep it
in this evidence-preserving patch until a narrower hardware result proves
it unnecessary.

Tested-on: Radxa Cubie A7S (A733 / SUN60IW2)
Signed-off-by: Enzo Adriano <enzo.adriano.code@gmail.com>
```

Notes before use:

- This is the H153 evidence-preserving version.
- If H154 passes the approval-gated no-`mbus-msi-lite0` hardware proof,
  replace this body with the H154 variant below and do not claim
  `mbus-msi-lite0` is required.
- If maintainers object to `CLK_IS_CRITICAL`, be ready to ask for the
  preferred explicit-consumer or interconnect/fabric modelling.

## Patch 2 H154 variant commit draft

Use only if H154 passes hardware proof.

Subject:

```text
clk: sunxi-ng: a733: keep storage and NSI fabric clocks critical
```

Body:

```text
Several A733 fabric clocks sit between storage bus masters and memory but
are not represented as ordinary device consumers. Letting the unused-clock
walk gate these clocks can leave SDMMC0 unable to complete its internal
clock/update or normal IDMA path even though the host controller itself has
probed.

Keep the storage AHB/MBUS lane and the NSI fabric clocks enabled. Hardware
testing on Radxa Cubie A7S showed that keeping `ahb-store`, `mbus-store`,
`nsi`, and `bus-nsi` enabled, together with the NSI update-bit commit, is
sufficient for SDMMC0 normal IDMA to enumerate the card and mount the root
filesystem.

Tested-on: Radxa Cubie A7S (A733 / SUN60IW2)
Signed-off-by: Enzo Adriano <enzo.adriano.code@gmail.com>
```

Notes before use:

- This version intentionally omits `mbus-msi-lite0`.
- Do not use it unless the H157/H154 proof passes and the result packet records the pass criteria.

## Patch 3 commit draft

Subject:

```text
clk: sunxi-ng: a733: commit the boot-programmed NSI clock state
```

Body:

```text
The A733 NSI clock uses the common sunxi-ng update-bit mechanism. Boot
firmware can leave the NSI mux/divider value visible to Linux before the
corresponding self-clearing update bit has been committed from the Linux
CCU driver's point of view.

Commit the boot-programmed NSI clock state once during A733 CCU probe,
before fabric consumers start probing. The write uses the existing
CCU_SUNXI_UPDATE_BIT mechanism and does not preserve the bit in readback,
because the hardware clears it after accepting the update.

In the tested boot path, no normal consumer committed the boot-programmed
NSI state before SDMMC0 normal IDMA needed the fabric. Parent, gate, and
divider helper paths can pulse the update bit for clocks with
CCU_FEATURE_UPDATE_BIT, but the MP rate path itself does not appear to OR
in CCU_SUNXI_UPDATE_BIT.

On Radxa Cubie A7S testing, the update pulse by itself was not sufficient,
but the pulse together with critical NSI/storage fabric clocks let SDMMC0
normal IDMA enumerate the card and mount the root filesystem.

Tested-on: Radxa Cubie A7S (A733 / SUN60IW2)
Signed-off-by: Enzo Adriano <enzo.adriano.code@gmail.com>
```

Notes before use:

- This preserves the H165/H167 update-bit nuance.
- The maintainer-facing design question remains: A733-specific probe fixup
  versus generic registration-time handling for `CCU_FEATURE_UPDATE_BIT` MP
  clocks.
- Before committing, recheck whether a common helper already exists or would
  be preferred by sunxi-ng maintainers.

## Pre-commit checklist

Before creating real commits:

- Confirm whether H153 or H154 patch 2 should be used.
- Confirm the target base commit and dependency stack.
- Confirm whether patch 1 should include a source comment.
- Recheck Patchew/lore for a newer A733 CCU revision.
- Ensure the signoff identity is still correct.
- Do not include private paths, IPs, local-model references, or tool provenance in commit messages.

## Post-commit gates

After real commits exist in a dedicated kernel worktree:

- `git format-patch` into a scratch output directory.
- `git diff --check` or equivalent on the final branch.
- `scripts/checkpatch.pl --strict` on generated patches.
- Focused arm64 object build for `drivers/clk/sunxi-ng/ccu-sun60i-a733.o`.
- Public hygiene scan on generated mail artifacts.
- Final b4/lore recipient and thread check before any send.

## Guardrails

- Do not use Cubie1.
- Do not run H154 or H153 hardware proof without explicit operator approval.
- Do not create kernel-source commits without explicit operator approval.
- Do not send H167 or any generated patch series without explicit operator approval.
