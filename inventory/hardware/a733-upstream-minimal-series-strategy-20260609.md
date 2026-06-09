# A733 Upstream Minimal Series Strategy - 2026-06-09

This is a private planning note. Do not copy private lab paths, IP addresses,
raw UART logs, or local-model text into an upstream submission.

## Current Conclusion

Do not send the historical 9-patch v4 export as an upstream series. Treat it as
a local validation/export tree.

The likely upstreamable direction is a smaller board/SoC enablement series
stacked on the active or accepted A733 RTC, CCU/PRCM, and pinctrl
prerequisites. Corrected-root runtime proof now exists for the exact v4
validation Image and DTB, but a regenerated candidate still needs prerequisite
API reconciliation.

## Dependencies To Coordinate

Known active external references:

```text
Depends-on: 20260121-a733-rtc-v1-0-d359437f23a7@pigmoral.tech
Depends-on: 20260310-a733-clk-v1-0-36b4e9b24457@pigmoral.tech
Depends-on: 20250821004232.8134-1-andre.przywara@arm.com
```

Local public-inbox research through 2026-06-09 found no newer Linux A733
CCU/pinctrl v2 work. Re-check RTC, CCU/PRCM, pinctrl, and MMC compatible
coverage before preparing any sendable branch.

## Drop From Local Export

Drop or defer these local patches from a first sendable slice:

- A733 CCU binding and driver, while Junhui Liu's CCU/PRCM RFC remains active.
- A733 pinctrl binding and driver, while Andre Przywara's pinctrl RFC remains
  active.
- MAINTAINERS `sun60i` pattern unless maintainers ask for it or prerequisite
  subsystem work establishes the pattern first.
- Ethernet/GMAC, VPU, display, Wi-Fi, Bluetooth, USB-C, PCIe, and other
  unproven hardware blocks.

Do not submit local CCU/PRCM or pinctrl work independently while the overlap is
unresolved.

## Candidate Minimal Series Shape

Expected target shape, subject to maintainer feedback:

1. `dt-bindings: arm: sunxi: Add Radxa Cubie A7S`
   - document `radxa,cubie-a7s`
   - pair it with `allwinner,sun60i-a733`
   - keep this to board/SoC compatibles only
2. Optional: `dt-bindings: mmc: Add Allwinner A733 compatible`
   - include this only if the chosen base still lacks
     `allwinner,sun60i-a733-mmc`
   - keep it to the compatible/fallback binding update
3. `arm64: dts: allwinner: Add sun60i-a733.dtsi`
   - compatible and basic SoC structure
   - CPU nodes
   - timer
   - GICv3
   - UART0
   - SDMMC0
   - phandles/clock/reset/pinctrl references matching the accepted or current
     prerequisite RFCs
4. `arm64: dts: allwinner: Add Radxa Cubie A7S board`
   - `model`
   - board compatible
   - `chosen { stdout-path = "serial0:115200n8"; }`
   - enable UART0 and SDMMC0 only

The A733 MMC compatible now has an explicit blocker: if the chosen base does
not already document it, carry a focused binding patch before the DTS user or
use only an already documented compatible if that is technically correct.

## Runtime Proof Required First

The exact v4 kernel and DTB have a clean corrected-root UART proof using:

```text
root=PARTUUID=db375e07-7682-4d4e-b8bc-a923dd0b027e rootfstype=ext4 rootwait ro rootflags=noload init=/bin/sh
```

The proof shows mainline Linux enumerating `mmcblk0` and partitions, including
`mmcblk0p3`, and mounting the root filesystem read-only via the corrected
PARTUUID path. The old `root=UUID=...` panic is not runtime proof.

## Local Shape Gate

Before any A733 export is treated as maintainer-facing, run:

```sh
scripts/a733-series-shape-gate /path/to/exported/patches
```

For the current public `patches/` export this gate passes because the export
has been reshaped away from the historical 9-patch scaffolding. Passing the
shape gate is not enough: `scripts/a733-prereq-api-audit` must also pass before
candidate regeneration. A candidate export should be limited to board binding,
optional A733 MMC binding, SoC DTSI, and board DTS patches; it must carry the
active RTC, CCU/PRCM, and pinctrl `Depends-on:` IDs and avoid local CCU/PRCM,
pinctrl, MAINTAINERS, vendor-U-Boot workaround, or unrelated hardware feature
patches.

## Anti-Goals

- No vendor-DTB pollution: no `arm,sun60iw2p1`, vendor path aliases,
  bootloader workaround nodes, `fdt_high` workarounds, or display nodes for
  vendor U-Boot.
- No hard-coded RAM size in DTS; rely on bootloader memory fixup.
- No feature creep beyond the first UART0 + SDMMC0 proof slice.
- No claim that the vendor U-Boot `drm_debug=1` workaround is a kernel or DTS
  fix. It is a lab-only RAM workaround to bypass vendor FDT mutation while
  testing the mainline DTB.
