# Patch Directory

This directory contains exported patch files for review preparation only. The
authoritative code lives in the Linux fork branches named from the repository
root README.

Current export:

- branch: `candidate/a733-platform-clean-v2`
- base: `6f3ed7fec72fc8979b2a8c7219c0a9fcfc8d07b5`
- base subject: `Merge tag 'for-7.1/dm-fixes-3' of git://git.kernel.org/pub/scm/linux/kernel/git/device-mapper/linux-dm`
- head: `11db6033ce0040edd70cac3def158e1befc6ecb6`
- head subject: `arm64: dts: allwinner: add Radxa Cubie A7S`

Patch order:

1. `dt-bindings: arm: sunxi: add Radxa Cubie A7S`
2. `dt-bindings: clock: add Allwinner A733 CCU`
3. `clk: sunxi-ng: add Allwinner A733 CCU support`
4. `dt-bindings: pinctrl: add Allwinner A733 pin controller`
5. `pinctrl: sunxi: add Allwinner A733 pin controller`
6. `dt-bindings: mmc: add Allwinner A733 compatible`
7. `arm64: dts: allwinner: add Allwinner A733 SoC`
8. `arm64: dts: allwinner: add Radxa Cubie A7S`

These files are not a mailed submission series. They now include the human
DCO sign-off authorized for this public candidate export, but the cover letter
still marks the series as draft-only until the open items in `docs/status.md`
are resolved.

Before any version is sent upstream, regenerate the series from a clean kernel
tree, run the checks in `docs/mainline-cleanup-workflow.md`, and record the
exact results in `docs/status.md`.
