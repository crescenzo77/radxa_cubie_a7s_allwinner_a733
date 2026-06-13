# A733-SDMMC-H224: H215 Maintainer Delta Map

Captured: 2026-06-13T07:21:36Z

## Purpose

Summarize the technical delta in the H215 RFC/RFT series against the visible
A733 CCU RFC baseline, in a form that is easy to use during maintainer review.

This packet is documentation only. It is not a new mail draft, not a resend
approval, and not a source change.

## Series Identity

- Sent series: H215 / H210 normalized RFC/RFT candidate
- Base: `d9aa2e15caae`
- Exact tested source state: `de486cb24c361a86cba26738f24332df780872b0`
- Touched source file: `drivers/clk/sunxi-ng/ccu-sun60i-a733.c`
- Post-send reproducibility refresh: H223 passed

## Delta Summary

The whole series changes one CCU driver source file. The source delta has
three types of change:

1. keep specific fabric/register-path clocks enabled with `CLK_IS_CRITICAL`;
2. give the NSI clock register a local symbolic name;
3. pulse the common sunxi-ng update bit once during A733 CCU probe to commit
   the boot-programmed NSI state.

## Per-Patch Map

### Patch 1: CPUS/R-domain bridge

Changes:

- `ahb-cpus` at `0x5c0 BIT(28)` changes from flags `0` to
  `CLK_IS_CRITICAL`.
- A short source comment explains that R-CCU and RTC register access depends
  on this bridge.

Reason:

- If the unused-clock walk gates this bridge, later R-domain register reads can
  stall.
- Keeping it enabled allowed the unused-clock walk and later R-domain reads to
  complete on Radxa Cubie A7S.

Caveat:

- This is a register-access-path keepalive, not a claim that a normal device
  consumer exists for the bridge.

### Patch 2: Storage and NSI fabric keepalive

Changes:

- `nsi` at register `0x580` gains `CLK_IS_CRITICAL` while retaining
  `CCU_FEATURE_UPDATE_BIT`.
- `bus-nsi` at `0x584 BIT(0)` gains `CLK_IS_CRITICAL`.
- `ahb-store` at `0x5c0 BIT(24)` gains `CLK_IS_CRITICAL`.
- `mbus-msi-lite0` at `0x5e0 BIT(29)` gains `CLK_IS_CRITICAL`.
- `mbus-store` at `0x5e0 BIT(30)` gains `CLK_IS_CRITICAL`.

Reason:

- These clocks sit on the storage/fabric path needed by SDMMC0 normal IDMA.
- The hardware-proven source state keeps the full set enabled through SDMMC0
  card enumeration and read-only root mount.

Caveat:

- `mbus-msi-lite0` remains evidence-preserving, not independently proven
  minimal. Do not claim it is the smallest possible storage-fabric set.

### Patch 3: NSI update-bit commit

Changes:

- Introduces `SUN60I_A733_NSI_REG` for `0x580`.
- Uses that name in the `nsi` clock definition.
- During A733 CCU probe, reads the NSI register and writes it back ORed with
  `CCU_SUNXI_UPDATE_BIT`.

Reason:

- The NSI clock uses the sunxi-ng update-bit mechanism.
- Firmware can leave the boot-programmed mux/divider state visible but not
  committed before SDMMC0 normal IDMA uses the fabric.
- Pulsing the update bit commits that state before fabric consumers probe.

Caveat:

- A common-framework treatment for update-bit clocks may be preferable if
  maintainers want this handled outside the A733 driver. The submitted shape is
  the narrow A733-specific hardware-tested expression.

### Patch 4: GIC and CPU peripheral clocks

Changes:

- `gic` at `0x560` changes from flags `0` to `CLK_IS_CRITICAL`.
- `cpu-peri` at `0x568` changes from flags `0` to `CLK_IS_CRITICAL`.

Reason:

- Hardware narrowing kept these two clocks while dropping earlier diagnostic
  IOMMU and `pll-periph0-480M` trial criticals.
- The exact tested source state reached SDMMC0 enumeration and read-only root
  mount with both clocks kept.

Caveat:

- This is the current hardware-tested keepalive shape. It should be narrowed
  only with stronger hardware evidence or maintainer guidance.

## One-Line Review Framing

H215 keeps the A733 CPUS/register-access bridge, storage/NSI fabric path, GIC,
and CPU peripheral clocks alive across unused-clock handling, then commits the
boot-programmed NSI update-bit state before SDMMC0 normal IDMA needs the
fabric.

## What Not To Claim

- Do not claim all Cubie A7S peripherals work.
- Do not claim Ethernet, display, VPU, USB-C, PCIe, Wi-Fi, Bluetooth, camera,
  or eMMC support.
- Do not claim `mbus-msi-lite0` is independently minimal.
- Do not claim the A733-specific NSI probe write is the only acceptable design;
  it is the tested narrow expression.
- Do not expand this into board-DTS scope.

## Ready Use

Use this map alongside:

- H218 for response phrasing;
- H219 for resend/alternate-action gating;
- H223 for post-send reproducibility evidence.
