# Patch Directory

This directory contains exported patch files for review preparation only. The
authoritative code lives in the Linux fork branches named from the repository
root README.

Current review export:

- previous validation branch: `candidate/a733-platform-clean-v4`
- base: `6f3ed7fec72fc8979b2a8c7219c0a9fcfc8d07b5`
- base subject: `Merge tag 'for-7.1/dm-fixes-3' of git://git.kernel.org/pub/scm/linux/kernel/git/device-mapper/linux-dm`
- previous validation head: `abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e`
- previous validation head subject: `MAINTAINERS: add Allwinner sun60i pattern`

Patch order:

1. `dt-bindings: arm: sunxi: add Radxa Cubie A7S`
2. `arm64: dts: allwinner: add Allwinner A733 SoC`
3. `arm64: dts: allwinner: add Radxa Cubie A7S`

These files are not a mailed submission series. They are a maintainer-shape
review export that intentionally drops the local CCU, pinctrl, standalone MMC
binding, and MAINTAINERS scaffolding from the earlier 9-patch draft. The DTS
patches carry explicit `Depends-on:` references for the active A733 RTC,
CCU/PRCM, and pinctrl RFCs.

A final regenerated candidate may add one MMC binding patch if the chosen base
does not already document `allwinner,sun60i-a733-mmc`. It must not grow into
local CCU, pinctrl, Ethernet, VPU, display, wireless, USB-C, or PCIe work.

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
