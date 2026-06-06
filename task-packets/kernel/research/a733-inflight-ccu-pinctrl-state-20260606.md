# A733 In-Flight CCU/Pinctrl State

Generated: 2026-06-06
Research worker: `qwen36-27b-7900xt-research`
Host: `192.168.50.252`
Research endpoint: `http://127.0.0.1:8092/v1`
Evidence source: `https://lore.kernel.org/linux-sunxi/0`
Local public-inbox cache: `/tmp/lore-linux-sunxi-0.git`

## Summary

The current local Cubie A7S Linux kernel workflow should not create or submit
independent A733 CCU or pinctrl patches until the in-flight RFC work is either
rebased, coordinated, or deliberately excluded from the local candidate series.

Subject/body search in the `linux-sunxi` public-inbox cache through
2026-06-06 did not find a newer A733-specific Linux CCU or Linux pinctrl v2
after the RFCs listed below.

## CCU/PRCM Evidence

- `a68c56676ffff76125ebf8761676f26731b54070`
  `[PATCH RFC 0/8] clk: sunxi-ng: Add support for Allwinner A733 CCU and PRCM`
  by Junhui Liu, 2026-03-10.
- Scope: DT binding, SDM dual-pattern support, PRCM CCU, PLL clocks, bus
  clocks, module clocks, bus clock gates, and reset lines.
- RFC reason: several main CCU parent clocks are hard to determine from the
  manual. The implementation follows vendor practice and prior SoC designs
  where documentation is lacking.
- Dependency: the cover says this functionally relies on the A733 RTC series.
- `c737ff48970b0c0b3808ec3649fa421d6307bb0d`
  Chen-Yu Tsai reply, 2026-03-28, to the A733 CCU binding patch.
- Maintainer feedback found: the binding part was described as correct, but
  there were detailed naming/rate questions, including keeping unit numbers
  such as `PLL_GPU0` and checking whether `VIDEO0_8X` should be `12X` if it is
  the common parent for 4X and 3X dividers.

## Pinctrl Evidence

- `5f2058d77e1f26d053ba352fcd6fd2e32834d24c`
  `[RFC PATCH 0/9] pinctrl: sunxi: Allwinner A733 support`
  by Andre Przywara, 2025-08-21.
- Scope: new A733 MMIO frame layout, refactoring, set/clear GPIO registers,
  DT binding, `a733-r` compatible, and A733 driver stub.
- RFC reason: author did not have suitable hardware and was not fully
  confident that the IRQ number-to-pin mapping worked correctly.
- `94ad0f743b50ca1b149c9948988e3ce2d0957535`
  Julian Calaby reply, 2025-08-24, questioning whether `a733-r` and `a523-r`
  are actually compatible if the bank/pin counts match and pinmux values come
  from DT.

## Not Linux Kernel Pinctrl

- `19e57bbe0a1b824d2039b8c0411e2dfab0f9929b`
  `[PATCH v3 7/9] pinctrl: sunxi: a733: add initial support`
  by Yixun Lan, 2026-01-13.
- This patch was sent to `u-boot@lists.denx.de`; it is useful ecosystem
  context but is not the Linux kernel pinctrl driver series.

## 7900XT Research Summary

- Resolve CCU parent-clock ambiguities before relying on local CCU work.
- Address the existing CCU maintainer feedback on PLL naming and divider
  ratios before any resubmission.
- Confirm A733 pinctrl hardware behavior, especially IRQ-to-pin mapping.
- Decide whether `a733-r` should share handling with `a523-r` before adding
  bindings or compatibles.
- Keep watching for newer Linux CCU/pinctrl submissions; none were found in
  this archive through 2026-06-06.
- Keep U-Boot A733 work separate from Linux kernel patch planning.

## Patch Workflow Action

- Do not submit local A733 CCU or pinctrl patches as standalone Linux kernel
  work right now.
- For Cubie A7S enablement, prefer one of these paths:
  - rebase onto the public RFCs for local testing only
  - keep local CCU/pinctrl scaffolding out of upstream-facing patch exports
  - coordinate with the RFC authors before proposing overlapping Linux work
- Any future A733 CCU/pinctrl task packet must attach this packet and explain
  how the overlap was handled.

This packet is research input only. It is not validation proof and does not
authorize patch submission.
