# A733 Upstream Minimal Series Strategy - 2026-06-09

This is a private planning note. Do not copy private lab paths, IP addresses,
raw UART logs, or local-model text into an upstream submission.

## Current Conclusion

Do not send the current 9-patch v4 export as an upstream series. Treat it as a
local validation/export tree.

The likely upstreamable direction, after the corrected-root runtime proof, is a
smaller DTS/board enablement series stacked on the active or accepted A733
CCU/PRCM and pinctrl prerequisites.

## Dependencies To Coordinate

Known active external references:

```text
Depends-on: 20260310-a733-clk-v1-0-36b4e9b24457@pigmoral.tech
Depends-on: 20250821004232.8134-1-andre.przywara@arm.com
```

Local public-inbox research through 2026-06-06 found no newer Linux A733
CCU/pinctrl v2 work. Re-check this before preparing any sendable branch.

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

1. `arm64: dts: allwinner: Add sun60i-a733.dtsi`
   - compatible and basic SoC structure
   - CPU nodes
   - timer
   - GICv3
   - UART0
   - SDMMC0
   - phandles/clock/reset/pinctrl references matching the accepted or current
     prerequisite RFCs
2. `arm64: dts: allwinner: Add Radxa Cubie A7S board`
   - `model`
   - board compatible
   - `chosen { stdout-path = "serial0:115200n8"; }`
   - enable UART0 and SDMMC0 only

The A733 MMC compatible should not be assumed to need an independent patch
unless driver or binding review proves that separation is required.

## Runtime Proof Required First

Do not shape a sendable branch until the exact v4 kernel and DTB have a clean
UART proof using the corrected-root label:

```text
root=PARTUUID=db375e07-7682-4d4e-b8bc-a923dd0b027e rootfstype=ext4 rootwait ro rootflags=noload init=/bin/sh
```

The proof must show mainline Linux enumerating `mmcblk0` and partitions,
including `mmcblk0p3`, or equivalent root-device evidence. The old
`root=UUID=...` panic is not runtime proof.

## Local Shape Gate

Before any A733 export is treated as maintainer-facing, run:

```sh
scripts/a733-series-shape-gate /path/to/exported/patches
```

For the current public `patches/` export this gate must fail, because that
directory still contains the local 9-patch scaffolding series. A candidate
sendable export should not pass this gate unless it is shaped as the narrow
DTS/board slice, includes the two active prerequisite `Depends-on:` IDs, and
does not include local CCU/PRCM, pinctrl, standalone MMC compatible,
MAINTAINERS, vendor-U-Boot workaround, or unrelated hardware feature patches.

## Anti-Goals

- No vendor-DTB pollution: no `arm,sun60iw2p1`, vendor path aliases,
  bootloader workaround nodes, `fdt_high` workarounds, or display nodes for
  vendor U-Boot.
- No hard-coded RAM size in DTS; rely on bootloader memory fixup.
- No feature creep beyond the first UART0 + SDMMC0 proof slice.
- No claim that the vendor U-Boot `drm_debug=1` workaround is a kernel or DTS
  fix. It is a lab-only RAM workaround to bypass vendor FDT mutation while
  testing the mainline DTB.
