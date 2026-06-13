# A733-SDMMC-H222: Upstream Prerequisite Drift Refresh

Captured: 2026-06-13T07:16:29Z

## Purpose

Check whether the public upstream baseline for the A733 CCU/RTC/pinctrl
prerequisites has moved underneath the H200/H215 CCU/NSI work.

This packet is a drift refresh only. It does not change kernel source, send
mail, run hardware, or authorize a resend.

## Local Baseline

- Current proven source state: H200 at
  `de486cb24c361a86cba26738f24332df780872b0`.
- Current sent series: H215, based on H210/H200, replying to the A733 CCU RFC
  patch-7 thread.
- Local Mac `linux-a733` still has known APFS case-collision status noise and
  was not modified.
- Local trees still show A733 CCU commits named
  `clk: sunxi-ng: add Allwinner A733 CCU support`, but those are local/prereq
  stack commits, not proof of mainline landing.

## Public Checks

Checked public search and source views for:

- `clk: sunxi-ng: add Allwinner A733 CCU support`
- `ccu-sun60i-a733.c`
- `20260310-a733-clk`
- `Allwinner A733 CCU`
- likely A733 CCU v2 query shapes
- A733 RTC v2 query shapes
- A733 pinctrl v2 / Andre Przywara query shapes

Notable public references found:

- Patchew still shows the March 2026 A733 CCU/PRCM RFC series:
  `https://patchew.org/linux/20260310-a733-clk-v1-0-36b4e9b24457%40pigmoral.tech/`
- Infradead still shows the A733 CCU RFC cover:
  `https://lists.infradead.org/pipermail/linux-riscv/2026-March/086818.html`
- `torvalds/linux` raw `drivers/clk/sunxi-ng/Kconfig` still does not show an
  A733 CCU symbol in the checked master view.
- `torvalds/linux` raw
  `drivers/clk/sunxi-ng/ccu-sun60i-a733.c` did not return a file in the
  checked master view.
- linux-sunxi mainlining status still lists A733 CCU/RTC/pinctrl as active
  mainlining topics.
- Patchwork views for A733 pinctrl still show Andre Przywara's A733 pinctrl
  RFC series as new/RFC in the checked result set.

H215 visibility was also refreshed during this drift pass:

- exact H215 message ID search returned no result;
- H215 subject/author search returned no result.

## Interpretation

The checked public sources do not show a newer A733 CCU v2 baseline, a
mainline-landed `ccu-sun60i-a733.c`, or a public H215 archive hit. This keeps
H200/H215 aligned with the currently visible A733 CCU RFC baseline.

This is not absolute proof that no private branch, delayed archive, or
unindexed mail exists. It is enough to avoid unnecessary rebasing or respinning
right now.

## Decision Impact

- Do not rebase or rewrite H200/H215 for upstream drift based on this check.
- Keep H219 controlling resend/alternate-action decisions.
- Keep H218 ready for maintainer questions.
- If a later public A733 CCU v2 appears, re-run source comparison against H200
  before drafting any v2 or follow-up.
