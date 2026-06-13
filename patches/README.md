# Patch Directory

This directory contains exported patch files for review preparation only. The
authoritative submitted v1 series is the public b4/lore thread linked from the
repository root README.

Current review export:

- review shape: 4 non-cover patches plus cover letter
- base: current local prerequisite stack after A733 RTC, CCU/PRCM, and pinctrl
  RFCs are applied
- base commit recorded by the patch export: `6428b90c6af7`
- historical validation branch: `candidate/a733-platform-clean-v4`
- historical validation head: `abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e`

Patch order:

1. `dt-bindings: mmc: add Allwinner A733 compatible`
2. `dt-bindings: arm: sunxi: add Radxa Cubie A7S`
3. `arm64: dts: allwinner: add Allwinner A733 SoC`
4. `arm64: dts: allwinner: add Radxa Cubie A7S`

These files are a maintainer-shape review export that intentionally drops the
local CCU and pinctrl driver work from the earlier 9-patch draft. They are no
longer the send authority for v1; use the public archive thread for the exact
submitted messages.

Current snapshot status: historical promoted review snapshot. The upstream v1
DTS series was sent with `b4` and is visible at:

```text
https://patch.msgid.link/20260613-a733-dts-v1-public-ready-v1-0-7787c94681db@gmail.com
```

The files include the human DCO sign-off authorized for this public review
export. They intentionally do not include nonstandard metadata trailers; any
final trailer decision must be made by the human submitter using current kernel
documentation and subsystem expectations.

Before any future upstream revision, regenerate the series from a clean kernel
tree, run the checks in `docs/mainline-cleanup-workflow.md`, reflect the b4
send before any real send, and record the exact results in `docs/status.md`.
The next revision must also address maintainer feedback from v1: UART0 pin
definitions should live in the main A733 DTSI, and the DT timing must be
rechecked against the state of the A733 clock prerequisites.
