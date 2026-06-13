# A733 H153 CCU upstream series plan

Captured: 2026-06-13T02:37Z

Model/tooling constraint: continued work used Codex Desktop / hosted ChatGPT only. No local model and no OpenRouter model was used.

## Current candidate

- Host: `strix`
- Worktree: `/srv/projects/kernel-work/runtime/a733-ccu-nsi-upstream-shape`
- Branch: `codex/a733-ccu-nsi-upstream-shape`
- Base: `d9aa2e15caae arm64: dts: allwinner: add Radxa Cubie A7S`
- Kernel source status: one uncommitted edit to `drivers/clk/sunxi-ng/ccu-sun60i-a733.c`
- Patch artifact: `task-packets/kernel/a733-h152-ccu-nsi-upstream-shape.patch`

The current H152 diff compiles and passes checkpatch, but it mixes three related fixes. For upstream review, split the story so each patch has a narrow failure mode and can be reviewed independently.

## Recommended split

### 1. `clk: sunxi-ng: a733: keep the CPUS AHB bridge clock critical`

Change:

- mark `ahb-cpus` at `0x5c0 BIT(28)` as `CLK_IS_CRITICAL`

Rationale:

- The CPU reaches the R-CCU/RTC register windows through this bridge.
- With `clk_disable_unused()` allowed to gate it, later R-domain register reads can stall.
- This is independent of the SDMMC0 IDMAC blocker and should remain a small standalone fix.

Draft commit message body:

```text
The A733 main CCU exposes an AHB gate for the bridge into the CPUS/R
domain. Linux has no regular consumer for that bridge, but the CPU still
needs it in order to access R-CCU and RTC register windows.

If clk_disable_unused() gates ahb-cpus, later R-domain register accesses
can stall the bus. Keep the bridge clock enabled for the lifetime of the
kernel, matching the hardware access path rather than a device consumer.

Tested on a Radxa Cubie A7S, where the unused-clock walk completes and
R-domain register accesses remain live with this gate kept critical.
```

### 2. `clk: sunxi-ng: a733: keep storage and NSI fabric clocks critical`

Change:

- mark `ahb-store` at `0x5c0 BIT(24)` as `CLK_IS_CRITICAL`
- mark `mbus-msi-lite0` at `0x5e0 BIT(29)` as `CLK_IS_CRITICAL`
- mark `mbus-store` at `0x5e0 BIT(30)` as `CLK_IS_CRITICAL`
- mark `nsi` at `0x580` as `CLK_IS_CRITICAL`
- mark `bus-nsi` at `0x584 BIT(0)` as `CLK_IS_CRITICAL`

Rationale:

- The storage path and SDMMC0 IDMAC depend on fabric lanes that do not have a clean Linux device consumer model in the current CCU description.
- Hardware evidence shows storage-only criticals avoid SDMMC clock-update timeout but still do not make normal IDMAC reach root.
- Hardware evidence shows NSI update plus critical `nsi`/`bus-nsi` allows SDMMC0 normal IDMA to enumerate `mmcblk0`, see partitions, mount root read-only, and start `/bin/sh`.

Draft commit message body:

```text
Several A733 fabric clocks sit between storage masters and memory but are
not represented as ordinary device consumers. Letting the unused-clock
walk gate these clocks can leave SDMMC0 unable to complete its internal
clock/update and IDMAC path even though the host controller itself has
probed.

Keep the storage AHB/MBUS lane and the NSI fabric clocks enabled. This
matches the existing treatment of critical fabric clocks such as MBUS and
DRAM on related sunxi-ng CCU drivers, where the clock is a SoC fabric
precondition rather than a per-device optional resource.

On Radxa Cubie A7S testing, keeping the storage lane critical avoids the
SDMMC clock-update timeout, and keeping the NSI clocks critical is required
with the NSI update commit for SDMMC0 normal IDMA to enumerate the card and
mount the root filesystem.
```

Open question for maintainers:

- Is `mbus-msi-lite0` strictly required, or is it a conservative fabric-lane keepalive based on the current verified shape?
- If maintainers prefer explicit consumers over `CLK_IS_CRITICAL`, what is the preferred modelling for A733 NSI/storage fabric paths?

H154 follow-up: `task-packets/kernel/a733-h154-mbus-msi-lite0-evidence-audit-20260613T0243Z.md` found that `mbus-msi-lite0` was bundled in the known-good storage-fabric diagnostic and was not isolated. Keep H153 as the evidence-preserving default until hardware proof says otherwise; use `task-packets/kernel/a733-h154-no-mbus-msi-lite0-variant/` as the controlled narrowing candidate.

### 3. `clk: sunxi-ng: a733: commit the boot-programmed NSI clock state`

Change:

- define `SUN60I_A733_NSI_REG` for `0x580`
- after the PLL fixup loop in `sun60i_a733_ccu_probe()`, read NSI and write it back with `CCU_SUNXI_UPDATE_BIT`

Rationale:

- The NSI clock has `CCU_FEATURE_UPDATE_BIT`, so mux/divider changes require the self-clearing update bit.
- Hardware evidence maps H149's `0x02002580 bit 27` condition to this exact update bit.
- A probe-time update pulse alone is not sufficient, but the update pulse plus critical NSI clocks resolves the SDMMC0 normal IDMAC root-device blocker.

Draft commit message body:

```text
The A733 NSI clock uses the common sunxi-ng update-bit mechanism. Boot
firmware can leave the NSI mux/divider value visible to Linux before the
corresponding self-clearing update bit has been committed from the Linux
CCU driver's point of view.

Commit the boot-programmed NSI clock state once during CCU probe, before
fabric consumers start probing. The write uses the existing
CCU_SUNXI_UPDATE_BIT mechanism and does not preserve the bit in readback,
because the hardware clears it after accepting the update.

On Radxa Cubie A7S testing, the update pulse by itself is not enough, but
the pulse together with critical NSI fabric clocks lets SDMMC0 normal IDMA
enumerate the card and mount the root filesystem.
```

Open question for maintainers:

- Should this be an A733-specific probe fixup, or should sunxi-ng commit boot-time values for `CCU_FEATURE_UPDATE_BIT` clocks more generally during registration?

## Validation already done

For the combined H152 candidate:

- `git diff --check`: pass
- `scripts/checkpatch.pl --strict /tmp/a733-h152-ccu-nsi-upstream-shape.patch`: pass
- focused arm64 object build of `drivers/clk/sunxi-ng/ccu-sun60i-a733.o`: pass

For the split H153 patch artifacts:

- Split draft worktree: `/srv/projects/kernel-work/runtime/a733-ccu-nsi-split-draft`
- Split patch directory: `task-packets/kernel/a733-h153-split-series/`
- Patch files:
  - `0001-clk-sunxi-ng-a733-keep-cpus-ahb-bridge-critical.patch`
  - `0002-clk-sunxi-ng-a733-keep-storage-and-nsi-fabric-critical.patch`
  - `0003-clk-sunxi-ng-a733-commit-boot-programmed-nsi-state.patch`

Validation run on `strix`:

```sh
cd /srv/projects/kernel-work/runtime/a733-ccu-nsi-split-draft
git reset --hard HEAD
git clean -fd
for f in /tmp/a733-h153-split/*.patch; do
  git apply --check "$f"
  git apply "$f"
  scripts/checkpatch.pl --strict "$f"
done
git diff --check
make O=/srv/projects/kernel-work/build/a733-ccu-nsi-split-draft \
  ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig
make O=/srv/projects/kernel-work/build/a733-ccu-nsi-split-draft \
  ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
  -j$(nproc) drivers/clk/sunxi-ng/ccu-sun60i-a733.o
```

Results:

- all three patches apply sequentially from the clean H152 base
- each patch passes `checkpatch --strict`
- final series passes `git diff --check`
- final series builds `drivers/clk/sunxi-ng/ccu-sun60i-a733.o`

## Next safe actions

- Review the split patch artifacts for narrative and whether patch 2 should include `mbus-msi-lite0`.
- Optionally test the H154 no-`mbus-msi-lite0` variant to decide whether patch 2 can be narrowed before making kernel commits.
- Optionally test the exact split H153 result on Cubie hardware as the evidence-preserving default.
- If hardware proof passes, commit the split series in a dedicated Strix worktree and run the normal validation floor.

## Needs approval

- Any Cubie hardware run of the exact H152 candidate.
- Any kernel-source commit in the Strix worktree.
- Any public RFC/reply/send to kernel mailing lists.
