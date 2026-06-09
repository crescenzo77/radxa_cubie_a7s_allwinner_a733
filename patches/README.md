# Patch Directory

This directory contains exported patch files for review preparation only. The
authoritative code lives in the Linux fork branches named from the repository
root README.

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

These files are not a mailed submission series. They are a maintainer-shape
review export that intentionally drops the local CCU and pinctrl driver work
from the earlier 9-patch draft. The cover letter carries explicit `Depends-on:`
references for the active A733 RTC, CCU/PRCM, and pinctrl RFCs.

The files include the human DCO sign-off authorized for this public review
export. They intentionally do not include nonstandard metadata trailers; any
final trailer decision must be made by the human submitter using current kernel
documentation and subsystem expectations.

Before any upstream submission, regenerate the patches again from the final
clean kernel candidate branch so the source branch, cover letter, diffstats,
and validation proofs all describe the same code.

Before any version is sent upstream, regenerate the series from a clean kernel
tree, run the checks in `docs/mainline-cleanup-workflow.md`, and record the
exact results in `docs/status.md`.
