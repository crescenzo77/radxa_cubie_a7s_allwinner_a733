# Patch Directory

This directory contains exported patch files for review preparation only. The
authoritative code lives in the Linux fork branches named from the repository
root README.

Current draft export:

- branch: `candidate/a733-platform-clean-v4`
- base: `6f3ed7fec72fc8979b2a8c7219c0a9fcfc8d07b5`
- base subject: `Merge tag 'for-7.1/dm-fixes-3' of git://git.kernel.org/pub/scm/linux/kernel/git/device-mapper/linux-dm`
- head: `abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e`
- head subject: `MAINTAINERS: add Allwinner sun60i pattern`

Patch order:

1. `dt-bindings: arm: sunxi: add Radxa Cubie A7S`
2. `dt-bindings: clock: add Allwinner A733 CCU`
3. `clk: sunxi-ng: add Allwinner A733 CCU support`
4. `dt-bindings: pinctrl: add Allwinner A733 pin controller`
5. `pinctrl: sunxi: add Allwinner A733 pin controller`
6. `dt-bindings: mmc: add Allwinner A733 compatible`
7. `arm64: dts: allwinner: add Allwinner A733 SoC`
8. `arm64: dts: allwinner: add Radxa Cubie A7S`
9. `MAINTAINERS: add Allwinner sun60i pattern`

These files are not a mailed submission series or a sendable candidate. They
now include the human DCO sign-off authorized for this public draft export.
They intentionally do not include automatic coding-assistance trailers; any
final disclosure or trailer decision must be made by the human submitter using
current kernel documentation and subsystem expectations.

This directory was regenerated from the v4 candidate branch after public-review
cleanup. Before any upstream submission, regenerate the patches again from the
final clean kernel candidate branch so the source branch, cover letter,
diffstats, and validation proofs all describe the same code.

The cover letter still marks the series as draft-only until the open items in
`docs/status.md` are resolved.

Before any version is sent upstream, regenerate the series from a clean kernel
tree, run the checks in `docs/mainline-cleanup-workflow.md`, and record the
exact results in `docs/status.md`.
